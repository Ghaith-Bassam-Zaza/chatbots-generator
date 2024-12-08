import openai
from db_setup import ScrapedContent, Embedding, session
import numpy as np
from CONSTANTS import API_KEY
# OpenAI API setup
openai.api_key = API_KEY

# Maximum tokens for embedding
MAX_TOKENS = 2048  # Adjust according to the embedding model's token limit

def generate_embeddings():
    try:
        # Fetch content from the database
        contents = session.query(ScrapedContent).all()
        if not contents:
            print("No content found in the database to generate embeddings.")
            return

        for content in contents:
            text = content.content
            if not text.strip():  # Skip empty content
                continue

            # Truncate text to the token limit
            truncated_text = text[:MAX_TOKENS]

            try:
                # Generate embedding using OpenAI
                embedding_response = openai.Embedding.create(
                    input=truncated_text,
                    model="text-embedding-ada-002"
                )
                embedding = embedding_response['data'][0]['embedding']
                if not embedding:
                    print(f"Warning: No embedding generated for content from {content.url}")
                    continue

                # Store embedding in the database
                embedding_entry = Embedding(content_id=content.id, embedding=str(embedding))
                session.add(embedding_entry)
                session.commit()
                print(f"Generated embedding for URL: {content.url}, Embedding length: {len(embedding)}")
            
            except openai.error.RateLimitError:
                print(f"Rate limit exceeded for URL: {content.url}. Skipping for now.")
                continue
            except openai.error.InvalidRequestError as e:
                print(f"Invalid request for URL: {content.url}. Error: {e}")
                continue

    except Exception as e:
        print(f"Error generating embeddings: {e}")

# Example usage for testing
if __name__ == "__main__":
    generate_embeddings()
