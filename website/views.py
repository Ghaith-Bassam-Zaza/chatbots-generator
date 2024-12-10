from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from uuid import uuid4
from .models import db, Bot, Session, Message  
from flask_login import login_required, current_user
from generatorAPI.db_setup import initialize_database,session, ScrapedContent, Embedding
from generatorAPI.embeddings import generate_embeddings
from generatorAPI.scraper import scrape_website
from CONSTANTS import API_KEY
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Collect data from the form for creating a new bot
        bot_name = request.form['bot_name']
        bot_url = request.form['bot_url']
        
        # Create a new bot and save it to the database
        new_bot = Bot(name=bot_name, url=bot_url, user_id=current_user.id)
        db.session.add(new_bot)
        db.session.commit()

        # Initialize the bot: scrape, generate embeddings, and prepare for chat
        try:
            print("Initializing database...")
            initialize_database()

            print(f"Scraping website for bot: {bot_name}")
            scrape_website(bot_url, new_bot.id)

            print(f"Generating embeddings for bot: {bot_name}")
            generate_embeddings(new_bot.id)
        except Exception as e:
            db.session.delete(new_bot)
            db.session.commit()
            return jsonify({"error": f"Failed to initialize bot: {e}"}), 500

        # Generate the embed script for the user
        embed_script = f"""
            <div id="chat-container-{new_bot.id}" style="border: 1px solid #ccc; padding: 10px; width: 300px;">
                <div id="chat-history-{new_bot.id}" style="height: 200px; overflow-y: scroll; border-bottom: 1px solid #ccc; margin-bottom: 10px;">
                    <!-- Chat messages will appear here -->
                </div>
                <textarea id="chat-input-{new_bot.id}" placeholder="Type your message here..." style="width: 100%; height: 50px;"></textarea>
                <button id="send-button-{new_bot.id}" style="width: 100%; margin-top: 5px;">Send</button>
            </div>
            <script>
                const botId = '{new_bot.id}';
                const apiUrl = '{request.url_root}api/chat'; // Adjust the URL based on your API endpoint
                const chatContainer = document.getElementById('chat-container-' + botId);
                const chatHistory = document.getElementById('chat-history-' + botId);
                const chatInput = document.getElementById('chat-input-' + botId);
                const sendButton = document.getElementById('send-button-' + botId);

                let sessionId = localStorage.getItem('chat_session_' + botId);
                if (!sessionId) {{
                    sessionId = crypto.randomUUID(); // Generate a unique session ID
                    localStorage.setItem('chat_session_' + botId, sessionId);
                }}

                sendButton.addEventListener('click', () => {{
                    const userMessage = chatInput.value.trim();
                    if (!userMessage) return;

                    // Append user's message to the chat history
                    const userMessageDiv = document.createElement('div');
                    userMessageDiv.textContent = "You: " + userMessage;
                    chatHistory.appendChild(userMessageDiv);

                    // Send the message to the API
                    fetch(apiUrl, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ session_id: sessionId, bot_id: botId, message: userMessage }}),
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        const botMessageDiv = document.createElement('div');
                        botMessageDiv.textContent = "Bot: " + data.response;
                        chatHistory.appendChild(botMessageDiv);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }})
                    .catch(error => console.error('Error:', error));

                    chatInput.value = ''; // Clear the input
                }});
            </script>
            """

        return render_template('home.html', embed_script=embed_script, bots=get_user_bots(), user=current_user)

    # For GET request, show the home page with existing bots
    return render_template('home.html', embed_script='', bots=get_user_bots(), user=current_user)

# Fetch texts and embeddings from the database
def fetch_texts_and_embeddings(bot_id):
    try:
        contents = session.query(ScrapedContent).filter_by(bot_id=bot_id).all()
        embeddings_data = session.query(Embedding).filter_by(bot_id=bot_id).all()

        if not contents or not embeddings_data:
            print("No texts or embeddings found in the database.")
            return [], []

        embedding_map = {e.content_id: e.embedding for e in embeddings_data}
        texts, embeddings = [], []

        for content in contents:
            if content.id in embedding_map:
                texts.append(content.content)
                embedding_vector = eval(embedding_map[content.id])  # Convert string to list
                embeddings.append(embedding_vector)

        return texts, embeddings

    except Exception as e:
        print(f"Error fetching texts and embeddings: {e}")
        return [], []

# Initialize FAISS vector store
def initialize_faiss_vector_store(bot_id):
    texts, _ = fetch_texts_and_embeddings(bot_id)
    if not texts:
        raise ValueError("No texts found in the database.")

    try:
        embedding_model = OpenAIEmbeddings(openai_api_key=API_KEY)
        faiss_store = FAISS.from_texts(texts=texts, embedding=embedding_model)
        print("FAISS vector store initialized successfully.")
        return faiss_store
    except Exception as e:
        print(f"Error initializing FAISS vector store: {e}")
        raise

sessions = {}

@views.route('/api/chat', methods=['POST'])
def chat():
    """
    RESTful API for chatbot interaction.
    """
    try:
        # Parse input JSON
        data = request.get_json()
        session_id = data.get('session_id')
        bot_id = data.get('bot_id')
        user_message = data.get('message')

        if not session_id or not bot_id or not user_message:
            return jsonify({"error": "Missing required parameters: session_id, bot_id, or message"}), 400

        # Initialize FAISS vector store for the bot
        if bot_id not in sessions:
            print(f"Initializing FAISS vector store for bot_id {bot_id}...")
            vector_store = initialize_faiss_vector_store(bot_id)

            # Create a new memory and conversation chain
            memory = ConversationBufferMemory(memory_key="history")
            llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo-16k", openai_api_key=API_KEY)
            conversation = ConversationChain(llm=llm, memory=memory)

            # Save session data
            sessions[bot_id] = {
                "vector_store": vector_store,
                "conversation": conversation
            }
        else:
            vector_store = sessions[bot_id]["vector_store"]
            conversation = sessions[bot_id]["conversation"]

        # Perform similarity search
        similar_docs = vector_store.similarity_search(user_message, k=3)
        relevant_docs = [{"content": doc} for doc in similar_docs]

        # Generate chatbot response
        response = conversation.predict(input=user_message)

        return jsonify({
            "session_id": session_id,
            "bot_id": bot_id,
            "response": response,
            "relevant_docs": relevant_docs
        })

    except Exception as e:
        print(f"Error in chat API: {e}")
        return jsonify({"error": str(e)}), 500


def get_user_bots():
    # Retrieve all bots created by the current user
    return Bot.query.filter_by(user_id=current_user.id).all()

