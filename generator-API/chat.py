import os
from CONSTANTS import API_KEY
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from db_setup import session, ScrapedContent, Embedding
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

# Fetch texts and embeddings from the database
def fetch_texts_and_embeddings(bot_id):
    """
    Fetch texts and embeddings from the database.

    Returns:
        texts (list): List of texts from ScrapedContent.
        embeddings (list): List of corresponding embeddings.
    """
    try:
        # Query ScrapedContent and Embedding tables
        contents = session.query(ScrapedContent).filter_by(bot_id=bot_id).all()
        embeddings_data = session.query(Embedding).filter_by(bot_id=bot_id).all()

        if not contents or not embeddings_data:
            print("No texts or embeddings found in the database.")
            return [], []

        # Map content IDs to embeddings
        embedding_map = {e.content_id: e.embedding for e in embeddings_data}

        texts = []
        embeddings = []

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
    """
    Initialize the FAISS vector store using texts and embeddings from the database.

    Returns:
        faiss_store: The FAISS vector store instance.
    """
    texts, _ = fetch_texts_and_embeddings(bot_id)  # Fetch texts only
    if not texts:
        raise ValueError("No texts found in the database.")

    try:
        # Initialize embedding model with API key from CONSTANTS
        embedding_model = OpenAIEmbeddings(openai_api_key=API_KEY)

        # Create FAISS vector store using texts and the embedding model
        faiss_store = FAISS.from_texts(texts=texts, embedding=embedding_model)
        print("FAISS vector store initialized successfully.")
        return faiss_store

    except Exception as e:
        print(f"Error initializing FAISS vector store: {e}")
        raise

def chat(bot_id):
    """
    Main chat function for handling user interactions with the chatbot using bot_id.
    """
    try:
        print(f"Starting chatbot service for bot_id {bot_id}...")

        # Initialize FAISS vector store specific to the bot_id
        vector_store = initialize_faiss_vector_store(bot_id)

        # Load the conversation chain with memory
        memory = ConversationBufferMemory(memory_key="history")
        llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo-16k", openai_api_key=API_KEY)
        conversation = ConversationChain(llm=llm, memory=memory)

        print(f"Chatbot {bot_id} is ready. Start chatting!")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chatbot. Goodbye!")
                break

            similar_docs = vector_store.similarity_search(user_input, k=3)
            if similar_docs:
                for i, doc in enumerate(similar_docs):
                    print(f"Relevant Doc {i + 1}: {doc}")

            response = conversation.predict(input=user_input)
            print(f"Bot: {response}")

    except Exception as e:
        print(f"Error in chatbot service for bot_id {bot_id}: {e}")

# Example usage for testing
if __name__ == "__main__":
    chat()
