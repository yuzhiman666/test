from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
import redis
# from langchain_redis import RedisConfig, RedisVectorStore
from langchain_redis.vectorstores import RedisConfig, RedisVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv
import os

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# rag_index_name="autofinance-loan-structing-rag"
rag_index_name="german_loan_legal_index"

# add knowledge to RAG
def rag_ingest(file_path):
    #1、加载原始文档    
    # 需要提前安装：pip install python-docx，pip install dashscope
    # loader = TextLoader(file_path)
    loader = UnstructuredWordDocumentLoader(file_path)
    documents = loader.load()
    print(f"成功加载文档： {file_path} ")
    #2、切分文档
    import re
    from langchain_text_splitters import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator="\n\n", keep_separator=True)
    texts = re.split(r"\n\n", documents[0].page_content)
    segments = text_splitter.split_text(documents[0].page_content)
    segment_documents = text_splitter.create_documents(texts)
    #3、将文档向量化，保存到Redis中
    load_dotenv()
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
    embedding_model = DashScopeEmbeddings(model="text-embedding-v1")
    redis_url = "redis://localhost:6379"
    config = RedisConfig(
        index_name=rag_index_name,
        redis_url=redis_url
    )
    vector_store = RedisVectorStore(embedding_model, config=config)
    vector_store.add_documents(segment_documents)
    return f"{len(segment_documents)} documents ingested to RAG Redis."

def rag_delete():
    """
    Delete all documents from the rag_index_name index in Redis vector store.
    """

    # 加载环境变量
    load_dotenv()
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

    # 配置 Redis 连接
    redis_url = "redis://localhost:6379"
    index_name = rag_index_name
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
    
def rag_test():
    """
    向量检索 元数据过滤
    """
    # 加载环境变量
    load_dotenv()
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

    # 配置 Redis 连接
    redis_url = "redis://localhost:6379"
    index_name = rag_index_name
    config = RedisConfig(
        index_name=index_name,
        redis_url=redis_url
    )
    # 连接 Redis 客户端
    r = redis.from_url(redis_url)
    embedding_model = DashScopeEmbeddings(model="text-embedding-v1")

    vector_store = RedisVectorStore(embedding_model, config=config)
    # scenario = "early_repayment"
    scenario = "early_repayment"
    id = "V"
    query = "early repayment"
    try:
        # 2. 检索该场景下的相关法规法规
        # 使用官方方法检索相关条款（支持元数据过滤）
        filter = f'@scenario:{{{scenario}}}'
        # filter = f'@scenario:"{scenario}*"'
        # filter = f'@id:"{id}*"'
        all_clauses = vector_store.similarity_search(
            query=query,  # 用场景核心需求作为查询
            k=5,
            filter=filter
            # filter=f"@scenario:{scenario}"  # 元数据过滤确保只查该场景。但是我们使用的 Redis 未加载 RediSearch 模块，无法直接为现有索引追加 scenario 字段，也无法创建支持元数据过滤的索引。
        )
        # 手动筛选选出 metadata.scenario 等于目标 scenario 的结果
        relevant_clauses = [
            clause for clause in all_clauses 
            if clause.metadata.get('scenario') == scenario
         ]
        return relevant_clauses
    except Exception as e:
        return f"索引不存在或查询失败: {e}"

def check_specific_metadata_index(target_fields=["scenario", "id"]):
    """
    检查指定Redis索引中，目标元数据字段（如scenario、id）是否已创建索引
    :param redis_url: Redis连接地址
    :param index_name: 索引名（如german_loan_legal_index，无需加idx:）
    :param target_fields: 要检查的元数据字段列表
    """

    # 加载环境变量
    load_dotenv()
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

    # 配置 Redis 连接
    redis_url = "redis://localhost:6379"
    index_name = rag_index_name
    config = RedisConfig(
        index_name=index_name,
        redis_url=redis_url
    )
    # 连接 Redis 客户端
    r = redis.from_url(redis_url)
    try:
        # 执行FT.INFO命令，获取原始结果（列表格式）
        info_raw = r.execute_command(f"FT.INFO {index_name}")
    except Exception as e:
        print(f"执行FT.INFO失败：{e}")
        return

    # 1. 解析原始结果，找到"fields"对应的内容（存储所有索引字段）
    fields_info = None
    for i in range(len(info_raw)):
        # Redis返回的键是字节类型，需解码为字符串
        key = info_raw[i].decode("utf-8") if isinstance(info_raw[i], bytes) else str(info_raw[i])
        if key == "fields":
            # "fields"的下一个元素就是所有字段的详细信息
            fields_info = info_raw[i + 1]
            break

    if not fields_info:
        print(f"索引 {index_name} 中未找到任何字段信息，可能索引结构异常")
        return

    # 2. 遍历fields_info，筛选目标字段（scenario、id）
    found_fields = {}  # 存储找到的目标字段：{字段名: 类型}
    for field in fields_info:
        # 每个field是一个列表，格式：[b'字段名', b'type', b'类型', ...]
        field_name = field[0].decode("utf-8") if isinstance(field[0], bytes) else str(field[0])
        # 找到"type"对应的value（字段类型）
        field_type = None
        for j in range(len(field)):
            attr_key = field[j].decode("utf-8") if isinstance(field[j], bytes) else str(field[j])
            if attr_key == "type":
                field_type = field[j + 1].decode("utf-8") if isinstance(field[j + 1], bytes) else str(field[j + 1])
                break
        # 若当前字段是目标字段，记录下来
        if field_name in target_fields:
            found_fields[field_name] = field_type

    # 3. 输出检查结果
    print(f"=== 索引 {index_name} 的元数据字段检查结果 ===")
    for target in target_fields:
        if target in found_fields:
            print(f"✅ {target}：已创建索引，类型为 {found_fields[target]}")
        else:
            print(f"❌ {target}：未找到对应的索引（可能未创建或字段名拼写错误）")


# Delete All knowledge from RAG, then add base knowledge
def rag_recovery(file_path):
    # 1.Delete all documents from the vector store
    rag_delete()
    # # 2.Add base knowledge to RAG 
    # rag_ingest(file_path)
    # return "RAG Redis recovery， only includes basic knowledge."


if __name__ == "__main__":
    # add base knowledge to RAG
    # 拼接文件路径
    # file_path = os.path.join(current_dir, "Reviewing_a_Loan_Contract.docx")
    # print(rag_recovery(file_path))

    # add additional knowledge to RAG
    # print(rag_ingest())
    # print(rag_test())
    # print(check_specific_metadata_index())
    print(rag_delete())
