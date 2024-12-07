from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
import os
import openai
from db_setup import Embedding, ScrapedContent, session
import numpy as np

def fetch_embeddings_from_db():
    """
    Fetch embeddings and corresponding content from the database.
    """
    try:
        data = session.query(ScrapedContent, Embedding).filter(ScrapedContent.id == Embedding.content_id).all()
        if not data:
            print("No data found in the database.")
            return [], []

        texts = [content.content for content, _ in data]
        embeddings = [np.array(eval(embedding.embedding)) for _, embedding in data]
        return texts, embeddings
    except Exception as e:
        print(f"Error fetching embeddings from database: {e}")
        return [], []

def initialize_faiss_vector_store():
    """
    Initialize FAISS vector store with data fetched from PostgreSQL.
    """
    texts, embeddings = fetch_embeddings_from_db()
    if not texts or not embeddings:
        raise ValueError("No texts or embeddings found in the database.")
    
    embedding_model = HuggingFaceEmbeddings(model_name='thenlper/gte-base', model_kwargs={'device': 'cpu'})

    # Create FAISS vector store
    faiss_store = FAISS.from_texts(texts=texts, embedding=embedding_model, embeddings=embeddings)
    return faiss_store

def chat():
    print("Starting chat bot")

    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Set the huggingface tokenizer parallelism to false (avoids warnings)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Initialize FAISS with embeddings and content from PostgreSQL
    vector_store = initialize_faiss_vector_store()

    # Use MMR to reduce redundancy
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 3})

    # Configure LLM
    llm = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo-16k-0613")

    # Prompt template for RetrievalQA
    template = """Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say you don't know; don't try to make up an answer.

    Context:{context}
    Question:{question}

    Only return the helpful answer below and nothing else.
    Helpful answer:
    """
    qa_prompt = PromptTemplate(template=template, input_variables=['context', 'question'])

    # Initialize RetrievalQA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=False,
        chain_type_kwargs={'prompt': qa_prompt}
    )

    # Interactive chatbot loop
    while True:
        user_input = input("prompt: ")
        if user_input.lower() == 'exit':
            print("Exiting")
            break
        if user_input.strip() == '':
            continue
        try:
            result = chain({'query': user_input})
            print(f"Answer: {result['result']}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    chat()
