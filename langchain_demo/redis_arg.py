import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Redis as RedisVectorStore
from langchain.chains import RetrievalQA

# Set Redis connection information
REDIS_URL = "redis://127.0.0.1:6379"
INDEX_NAME = "my_rag_index"

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. Please set your API Key in a .env file or directly in the code."
    )


def train_vector_database(file_path: str, redis_url: str, index_name: str):
    """
    Loads documents, splits them, generates embeddings using Ollama,
    and stores them in a Redis vector database.

    Args:
        file_path (str): The path to the document file (e.g., "langchain_demo/story.txt").
        redis_url (str): The URL for the Redis instance.
        index_name (str): The name for the Redis index.
    """
    print(f"Starting vector database training for file: {file_path}")

    # 1. Load data
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    # 2. Split text
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    print(f"Split {len(docs)} documents into chunks.")

    # 3. Generate embeddings and store in Redis vector database
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = RedisVectorStore.from_documents(
        docs, embeddings, redis_url=redis_url, index_name=index_name
    )
    print(f"Documents loaded and indexed into Redis index: {index_name}")


def ask_question_with_rag(query: str, redis_url: str, index_name: str):
    """
    Answers a question using a RAG (Retrieval-Augmented Generation) chain.

    Args:
        query (str): The question to ask.
        redis_url (str): The URL for the Redis instance.
        index_name (str): The name of the Redis index to retrieve from.

    Returns:
        dict: A dictionary containing the answer and source documents.
    """
    print(f"\nProcessing query: '{query}'")

    # Initialize Ollama Embeddings for retrieval (needs to match the one used for training)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Connect to the existing Redis vector store
    vectorstore = RedisVectorStore(embedding=embeddings, redis_url=redis_url, index_name=index_name)
    print("Connected to Redis vector store.")

    # 4. Create retriever
    retriever = vectorstore.as_retriever()

    # 5. Initialize LLM - Using Gemini
    GEMINI_CHAT_MODEL = "gemini-2.5-flash-preview-04-17"
    llm = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, temperature=0)
    print(f"Initialized Gemini LLM ({GEMINI_CHAT_MODEL}).")

    # 6. Create RAG Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    # 7. Test query
    result = qa_chain.invoke({"query": query})
    return result


# --- Example Usage ---
if __name__ == "__main__":
    # Train the vector database
    try:
        train_vector_database("langchain_demo/story.txt", REDIS_URL, INDEX_NAME)
    except Exception as e:
        print(f"Error during vector database training: {e}")

    # Ask a question based on the vector database
    try:
        query = "提到冰冷的建築段落主要在說什麼"
        response = ask_question_with_rag(query, REDIS_URL, INDEX_NAME)
        print("\n--- Answer ---")
        print(response["result"])
        print("\n--- Source Documents ---")
        for doc in response["source_documents"]:
            print(doc.metadata)
    except Exception as e:
        print(f"Error during RAG query: {e}")
