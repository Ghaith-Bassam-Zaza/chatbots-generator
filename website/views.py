from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from uuid import uuid4
from .models import db, Bot, Session, Message  
from flask_login import login_required, current_user
from CONSTANTS import WEB_DATABASE_URL
from generatorAPI.db_setup import initialize_database
from generatorAPI.embeddings import generate_embeddings
from generatorAPI.scraper import scrape_website

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Collect data from the form for creating a new bot
        bot_name = request.form['bot_name']
        bot_url = request.form['bot_url']
        
        # Create a new bot and save to the database
        new_bot = Bot(name=bot_name, url=bot_url, user_id=current_user.id)
        

        db.session.add(new_bot)
        db.session.commit()

        initialize_database()
        scrape_website(bot_url, new_bot.id)
        generate_embeddings(new_bot.id)

        # Generate the embed script to share with the user
        embed_script = f"""
        <script>
            const bot_id = '{new_bot.id}';
            const api_url = '/api/chat';
            const start_session_api_url = '/api/start_session';
            const session_id = localStorage.getItem('session_id') || '{uuid4()}';
            localStorage.setItem('session_id', session_id);

            if (!session_id) {{
                fetch(start_session_api_url, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ bot_id }})
                }})
                .then(response => response.json())
                .then(data => {{
                    session_id = data.session_id;
                    localStorage.setItem('session_id', session_id);
                }})
                .catch(error => {{
                    console.error('Error starting session:', error);
                }});
            }}

            async function sendMessage(message) {{
                const response = await fetch(api_url, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ bot_id, session_id, message }})
                }});
                const data = await response.json();
                console.log('Bot Response:', data.response);
                return data.response;
            }}
        </script>
        """

        return render_template('home.html', embed_script=embed_script, bots=get_user_bots(), user = current_user)

    # For GET request, show the home page with existing bots
    return render_template('home.html', bots=get_user_bots(),user = current_user)

@views.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.get_json()
    bot_id = data.get('bot_id')
    session_id = str(uuid4())

    # Store the new session in the database
    new_session = Session(bot_id=bot_id, session_id=session_id, user_id=current_user.id)
    db.session.add(new_session)
    db.session.commit()

    return jsonify({'session_id': session_id})

@views.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    bot_id = data.get('bot_id')
    session_id = data.get('session_id')
    message = data.get('message')

    # Validate and find the session from the database
    user_session = Session.query.filter_by(bot_id=bot_id, session_id=session_id, user_id=current_user.id).first()
    if not user_session:
        return jsonify({'error': 'Session not found or unauthorized access.'}), 404

    # Logic to handle the chat message and get response from the bot
    response = handle_bot_response(bot_id, message)

    # Store the message in the database for chat history if needed
    chat_message = Message(bot_id=bot_id, session_id=session_id, user_message=message, bot_response=response)
    db.session.add(chat_message)
    db.session.commit()

    return jsonify({'response': response})

def get_user_bots():
    # Retrieve all bots created by the current user
    return Bot.query.filter_by(user_id=current_user.id).all()

def handle_bot_response(bot_id, message):
    # Dummy response logic for demonstration; replace with actual bot logic
    return f"Response from bot {bot_id} to message: {message}"


