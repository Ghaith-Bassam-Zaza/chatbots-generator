import openai
from .db_setup import ScrapedContent, Embedding, session
import numpy as np
from CONSTANTS import API_KEY
# OpenAI API setup
openai.api_key = API_KEY

# Maximum tokens for embedding
MAX_TOKENS = 2048  # Adjust according to the embedding model's token limit
def generate_embeddings(bot_id):
    try:
        # Fetch content from the database for the given bot_id
        contents = session.query(ScrapedContent).filter_by(bot_id=bot_id).all()
        if not contents:
            print(f"No content found for bot_id {bot_id} to generate embeddings.")
            return

        for content in contents:
            text = content.content
            if not text.strip():
                continue

            truncated_text = text[:MAX_TOKENS]

            try:
                embedding_response = openai.Embedding.create(
                    input=truncated_text,
                    model="text-embedding-ada-002"
                )
                embedding = embedding_response['data'][0]['embedding']
                if not embedding:
                    print(f"Warning: No embedding generated for content from {content.url} (bot_id: {bot_id})")
                    continue

                # Store embedding in the database with bot_id
                embedding_entry = Embedding(content_id=content.id, embedding=str(embedding), bot_id=bot_id)
                session.add(embedding_entry)
                session.commit()
                print(f"Generated embedding for bot_id {bot_id} for URL: {content.url}, Embedding length: {len(embedding)}")

            except openai.error.RateLimitError:
                print(f"Rate limit exceeded for bot_id {bot_id}, URL: {content.url}. Skipping for now.")
                continue
            except openai.error.InvalidRequestError as e:
                print(f"Invalid request for bot_id {bot_id}, URL: {content.url}. Error: {e}")
                continue

    except Exception as e:
        print(f"Error generating embeddings for bot_id {bot_id}: {e}")

# Example usage for testing
if __name__ == "__main__":
    generate_embeddings()
