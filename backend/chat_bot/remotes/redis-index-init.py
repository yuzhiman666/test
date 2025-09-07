from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import asyncio

DB_URI = "redis://localhost:6379"

async def index_init():
    async with AsyncRedisSaver.from_conn_string(DB_URI) as checkpointer:
        # 初始化Redis存储结构（如必要的键空间等）
        await checkpointer.asetup()
        print("Redis checkpointer 初始化完成")

if __name__ == "__main__":
    # 运行异步初始化函数
    asyncio.run(index_init())