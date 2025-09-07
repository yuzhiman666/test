from langchain_community.document_loaders import TextLoader
import redis
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
parent_parent_dir = current_file.parent.parent
sys.path.append(str(parent_parent_dir))
from config.load_key import load_key

# add knowledge to RAG
def rag_ingest(file_path):
    #1、加载原始文档
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    #2、切分文档
    import re
    from langchain_text_splitters import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator="\n\n", keep_separator=True)
    texts = re.split(r"\n\n", documents[0].page_content)
    segment_documents = text_splitter.create_documents(texts)
    #3、将文档向量化，保存到Redis中
    DASHSCOPE_API_KEY = load_key("DASHSCOPE_API_KEY")
    embedding_model = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=DASHSCOPE_API_KEY
        )

    redis_url = "redis://localhost:6379"
    config = RedisConfig(
        index_name="auto-rag",
        redis_url=redis_url
    )
    vector_store = RedisVectorStore(embedding_model, config=config)
    vector_store.add_documents(segment_documents)
    return f"{len(segment_documents)} documents ingested to RAG Redis."

def rag_delete():
    """
    Delete all documents from the 'auto-rag' index in Redis vector store.
    """
    # 配置 Redis 连接
    redis_url = "redis://localhost:6379"
    index_name = "auto-rag"
    config = RedisConfig(
        index_name=index_name,
        redis_url=redis_url
    )

    # 通过 Redis 客户端直接删除索引（推荐，彻底清除）
    try:
        # 连接 Redis 客户端
        r = redis.from_url(redis_url)
        # 删除向量索引（Redis 向量存储的索引本质是一个哈希表，删除索引即删除所有文档）
        r.ft(index_name).dropindex(delete_documents=True)  # delete_documents=True 同时删除关联的文档
        return f"Successfully deleted all documents from RAG Redis index '{index_name}'."
    except Exception as e:
        return f"Error deleting index: {str(e)}"

# Delete All knowledge from RAG, then add base knowledge
def rag_recovery(file_path="汽车贷款管理办法(2017).txt"):
    # 1.Delete all documents from the vector store
    rag_delete()
    # 2.Add base knowledge to RAG 
    rag_ingest(file_path)
    return "RAG Redis recovery， only includes basic rule."


if __name__ == "__main__":
    # add base knowledge to RAG
    print(rag_recovery())