from scraper import scrape_website
from embeddings import generate_embeddings
from chat import chat  # Assuming this starts the chatbot server
from db_setup import initialize_database

def main():
    # Initialize database
    initialize_database()

    # Define bot_id for this instance
    bot_id = 1  # Change this for different bots as needed

    # Scrape, generate embeddings, and start the chatbot for a specific bot_id
    # print(f"Scraping website for bot_id {bot_id}...")
    # scrape_website("https://sensia-consulting.com/", bot_id)
    # print("Scraping completed.")

    # print(f"Generating embeddings for bot_id {bot_id}...")
    # generate_embeddings(bot_id)
    # print("Embedding generation completed.")

    print(f"Starting chatbot service for bot_id {bot_id}...")
    chat(bot_id)
    print(f"Chatbot {bot_id} service is running.")

if __name__ == "__main__":
    main()
