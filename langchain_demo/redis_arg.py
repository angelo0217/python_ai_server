import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# from langchain_openai import OpenAIEmbeddings # 不再需要導入 OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings  # 導入 OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Redis as RedisVectorStore
from langchain.chains import RetrievalQA

# 移除 OpenAI API Key 的設定，因為我們不再使用 OpenAI 的服務
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# 設置 Redis 連接資訊
REDIS_URL = "redis://127.0.0.1:6379"
INDEX_NAME = "my_rag_index"

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY 環境變數未設置。請在 .env 檔案中或直接在程式碼中設定您的 API Key。"
    )


# 1. 載入資料 (假設你有一份 story.txt 文件)
loader = TextLoader("langchain_demo/story.txt", encoding="utf-8")
documents = loader.load()

# 2. 切割文本
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# --- 關鍵修改點：將嵌入模型切換到 Ollama ---
# 3. 生成嵌入並儲存到 Redis 向量資料庫
embeddings = OllamaEmbeddings(model="nomic-embed-text")  # 使用 Ollama 的 nomic-embed-text 模型

vectorstore = RedisVectorStore.from_documents(
    docs, embeddings, redis_url=REDIS_URL, index_name=INDEX_NAME
)
print(f"Documents loaded and indexed into Redis index: {INDEX_NAME}")


# 4. 創建檢索器
retriever = vectorstore.as_retriever()

# 5. 初始化 LLM - 使用 Ollama
# llm = ChatOllama(model="qwen3:32b", temperature=0) # 確保你的 Ollama 有運行 llama3 模型

GEMINI_CHAT_MODEL = "gemini-2.5-flash-preview-04-17"
llm = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, temperature=0)
print(f"使用 Gemini LLM ({GEMINI_CHAT_MODEL}) 初始化。")


# 6. 創建 RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
)

# 7. 測試查詢
query = "提到冰冷的建築段落主要在說什麼"
result = qa_chain.invoke({"query": query})
print(result["result"])
print("\n--- 參考來源 ---")
for doc in result["source_documents"]:
    print(doc.metadata)
