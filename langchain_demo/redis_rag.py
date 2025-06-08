import os
import redis
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Redis as RedisVectorStore
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# from langchain.tools import Tool # This import was in your original code but not used in the final version of rag_query_tool


# Set Redis connection information
REDIS_URL = "redis://127.0.0.1:6379"

# Define different index names
STORY_INDEX_NAME = "story_rag_index"
TECH_DOC_INDEX_NAME = "tech_doc_rag_index"


# It's good practice to ensure API keys are set, but for this RAG
# example, GOOGLE_API_KEY isn't directly used by Ollama or Redis.
# I'll keep the check for robustness if you integrate other Langchain
# components later that might require it.
if not os.getenv("GOOGLE_API_KEY"):
    print(
        "Warning: GOOGLE_API_KEY environment variable not set. "
        "This may be required for other Langchain components but "
        "is not directly used by Ollama or Redis in this RAG setup."
    )


def _clear_redis_index(redis_url: str, index_name: str):
    """
    Clears an existing Redis index if it exists.
    This is an internal helper function.
    """
    try:
        r = redis.from_url(redis_url)
        print(f"Existing index '{index_name}' found. Deleting associated keys...")
        keys_to_delete = r.keys(f"doc:{index_name}:*")
        if keys_to_delete:
            r.delete(*keys_to_delete)
            print(
                f"Successfully deleted {len(keys_to_delete)} keys associated with '{index_name}'."
            )
        else:
            print(f"No keys found for index '{index_name}' despite _extra_data key existing.")
    except Exception as e:
        print(f"Could not connect to Redis or clear existing index '{index_name}': {e}")
        print("Please ensure Redis is running and accessible.")
        raise  # Re-raise the exception to indicate failure


class RAGService:
    """
    A service class to manage RAG (Retrieval-Augmented Generation) operations,
    including training vector databases and answering queries.
    """

    def __init__(
        self,
        redis_url: str = REDIS_URL,
        llm_model: str = "llama3.1:latest",
        embedding_model: str = "nomic-embed-text",
    ):
        self.redis_url = redis_url
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.embeddings = OllamaEmbeddings(model=self.embedding_model)
        self.llm = ChatOllama(model=self.llm_model, temperature=0)
        self.vectorstores = {}  # To store active vector store connections

    def train_vector_database(self, file_path: str, index_name: str):
        """
        Loads documents, splits them, generates embeddings using Ollama,
        and stores them in a Redis vector database.

        Args:
            file_path (str): The path to the document file.
            index_name (str): The name for the Redis index.
        """
        print(f"Starting vector database training for file: {file_path} into index: {index_name}")

        # Clear existing index before training
        _clear_redis_index(self.redis_url, index_name)

        # 1. Load data
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        # 2. Split text
        # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 試著調整這個值
            chunk_overlap=100,  # 試著調整這個值
            separators=["\n\n", "\n", " ", ""],  # 優先按段落、然後按行、再按詞語切分
            length_function=len,
            is_separator_regex=False,
        )
        docs = text_splitter.split_documents(documents)
        print(f"Split {len(docs)} documents into chunks for index '{index_name}'.")

        # 3. Generate embeddings and store in Redis vector database
        vectorstore = RedisVectorStore.from_documents(
            docs, self.embeddings, redis_url=self.redis_url, index_name=index_name
        )
        self.vectorstores[index_name] = vectorstore  # Store the active vector store
        print(f"Documents loaded and indexed into Redis index: {index_name}")

    def query(self, query_text: str, index_name: str):
        """
        Answers a question using a RAG (Retrieval-Augmented Generation) chain
        for a specific Redis index.

        Args:
            query_text (str): The question to ask.
            index_name (str): The name of the Redis index to retrieve from.

        Returns:
            dict: A dictionary containing the 'result' (answer) and
                  'source_documents' (list of relevant documents).
        """
        print(f"\nProcessing query: '{query_text}' using index: '{index_name}'")

        if index_name not in self.vectorstores:
            # If not already connected, establish connection to the vector store
            print(f"Connecting to Redis vector store for index '{index_name}'.")
            self.vectorstores[index_name] = RedisVectorStore(
                embedding=self.embeddings, redis_url=self.redis_url, index_name=index_name
            )
        else:
            print(f"Using existing connection for Redis vector store for index '{index_name}'.")

        retriever = self.vectorstores[index_name].as_retriever(search_kwargs={"k": 2})

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=retriever, return_source_documents=True
        )

        try:
            result = qa_chain.invoke({"query": query_text})
            return result
        except Exception as e:
            print(f"An error occurred during RAG query for index '{index_name}': {e}")
            return {"result": f"Error: {e}", "source_documents": []}

    def multi_index_query(self, query_text: str, index_names: list[str]):
        """
        Queries multiple Redis indexes and combines results using EnsembleRetriever.

        Args:
            query_text (str): The question to ask.
            index_names (list[str]): A list of Redis index names to query from.

        Returns:
            dict: A dictionary containing the 'result' (answer) and
                  'source_documents' (list of relevant documents from all sources).
        """
        from langchain.retrievers import EnsembleRetriever

        print(f"\nProcessing multi-index query: '{query_text}' using indexes: {index_names}")

        retrievers = []
        for index_name in index_names:
            if index_name not in self.vectorstores:
                print(f"Connecting to Redis vector store for index '{index_name}' for multi-query.")
                self.vectorstores[index_name] = RedisVectorStore(
                    embedding=self.embeddings, redis_url=self.redis_url, index_name=index_name
                )
            retrievers.append(self.vectorstores[index_name].as_retriever())

        if not retrievers:
            return {
                "result": "No valid indexes provided for multi-index query.",
                "source_documents": [],
            }

        # Weights can be adjusted based on the importance of each index
        # For simplicity, using equal weights here.
        weights = [1.0 / len(retrievers)] * len(retrievers)

        combined_retriever = EnsembleRetriever(retrievers=retrievers, weights=weights)

        qa_chain_combined = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=combined_retriever,
            return_source_documents=True,
        )

        try:
            combined_result = qa_chain_combined.invoke({"query": query_text})
            return combined_result
        except Exception as e:
            print(f"An error occurred during multi-index RAG query: {e}")
            return {"result": f"Error: {e}", "source_documents": []}


# --- Example Usage (similar to API calls) ---
if __name__ == "__main__":
    rag_service = RAGService(redis_url=REDIS_URL)

    # Assume 'langchain_demo/story.txt' and 'langchain_demo/tech_doc.txt' exist.
    # If not, create them for testing.
    # Example:
    # echo "There once was a lonely house on a cold, unforgiving hill." > langchain_demo/story.txt
    # echo "Kubernetes is an open-source container orchestration system." > langchain_demo/tech_doc.txt
    os.makedirs("langchain_demo", exist_ok=True)
    with open("langchain_demo/tech_doc.txt", "w", encoding="utf-8") as f:
        f.write(
            "Kubernetes 是一個開源的容器編排系統，用於自動化應用程式的部署、擴展和管理。它最初由 Google 設計。"
        )

    # --- 1. Train Vector Databases ---
    print("\n--- Training Vector Databases ---")
    try:
        rag_service.train_vector_database("langchain_demo/story.txt", STORY_INDEX_NAME)
        rag_service.train_vector_database("langchain_demo/tech_doc.txt", TECH_DOC_INDEX_NAME)
    except Exception as e:
        print(f"Error during vector database training: {e}")
        # Exit if training fails, as subsequent queries will likely fail too
        exit(1)

    # --- 2. Make Queries like API Calls ---

    # Query the story index
    print("\n--- Querying Story Index ---")
    query_story = "提到冰冷的建築段落主要在說什麼"
    response_story = rag_service.query(query_story, STORY_INDEX_NAME)
    print("Answer:", response_story["result"])
    print(
        "Source Documents:",
        [doc.metadata.get("source", "Unknown") for doc in response_story["source_documents"]],
    )

    # Query the tech document index
    print("\n--- Querying Tech Document Index ---")
    query_tech = "Kubernetes 是什麼？"
    response_tech = rag_service.query(query_tech, TECH_DOC_INDEX_NAME)
    print("Answer:", response_tech["result"])
    print(
        "Source Documents:",
        [doc.metadata.get("source", "Unknown") for doc in response_tech["source_documents"]],
    )

    # Example of a multi-index query
    print("\n--- Performing Multi-Index Query ---")
    multi_query = "請問冰冷的建築和 Kubernetes 分別是什麼？"
    response_multi = rag_service.multi_index_query(
        multi_query, [STORY_INDEX_NAME, TECH_DOC_INDEX_NAME]
    )
    print("Answer:", response_multi["result"])
    print(
        "Source Documents:",
        [doc.metadata.get("source", "Unknown") for doc in response_multi["source_documents"]],
    )
