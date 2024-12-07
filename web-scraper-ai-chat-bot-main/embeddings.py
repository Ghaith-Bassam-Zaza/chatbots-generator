import openai
from db_setup import ScrapedContent, Embedding, session
import numpy as np
from CONSTANTS import API_KEY
# OpenAI API setup
openai.api_key = API_KEY

def generate_embeddings():
    try:
        # Fetch all content from the database
        contents = session.query(ScrapedContent).all()

        if not contents:
            print("No content found in the database to generate embeddings.")
            return

        for content in contents:
            # Skip if the content is empty
            if not content.content.strip():
                print(f"Skipping empty content for URL: {content.url}")
                continue

            # Skip if an embedding already exists for this content
            existing_embedding = session.query(Embedding).filter_by(content_id=content.id).first()
            if existing_embedding:
                print(f"Embedding already exists for URL: {content.url}")
                continue

            # Generate embedding using OpenAI
            try:
                response = openai.Embedding.create(
                    input=content.content,
                    model="text-embedding-ada-002"
                )
                embedding = response['data'][0]['embedding']
            except Exception as e:
                print(f"Error generating embedding for URL: {content.url}: {e}")
                continue

            # Save the embedding to the database
            embedding_entry = Embedding(content_id=content.id, embedding=str(embedding))
            session.add(embedding_entry)
            session.commit()
            print(f"Generated embedding for URL: {content.url}, Embedding length: {len(embedding)}")

    except Exception as e:
        print(f"Error generating embeddings: {e}")
