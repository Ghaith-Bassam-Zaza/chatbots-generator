from scraper import scrape_website
from embeddings import generate_embeddings
from chat import chat  # Assuming this starts the chatbot server
from db_setup import initialize_database

def main():
    # Initialize database (only creates tables if they do not exist)
    initialize_database()

    # Define the starting URL and depth
    start_url = "https://sensia-consulting.com/"
    start_depth = 3  # For now, depth is unused unless recursion is implemented in scraping.

    # Step 1: Scrape the website
    print("Scraping website...")
    scrape_website(start_url,start_depth)
    print("Scraping completed.")

    # Step 2: Generate embeddings
    print("Generating embeddings...")
    generate_embeddings()
    print("Embedding generation completed.")

    # Step 3: Start chatbot service
    print("Starting chatbot service...")
    chat()
    print("Chatbot service is running.")

if __name__ == "__main__":
    main()
