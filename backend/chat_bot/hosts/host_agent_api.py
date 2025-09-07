# host_agent_cli_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import httpx
from typing import Dict, List, Optional
from config.settings import API_CONFIG,REMOTE_AGENTS
from services.agent_services import (
    AgentProcessManager,
    AgentRegistry,
    AgentSelector,
    AgentQueryService
)

from typing import Dict, List, Optional
import httpx
from config.settings import REMOTE_AGENTS
import json
from typing import Dict, List, Optional
from fastapi.responses import StreamingResponse
import json
from a2a.types import TextPart
import re

class QueryRequest(BaseModel):
    query: str
    session_id: str
    auto_start: bool = False

class AgentInfo(BaseModel):
    name: str
    description: str
    url: str

class QueryResponse(BaseModel):
    success: bool
    message: str
    agent_name: str
    response: str
    task_id: Optional[str] = None
    artifacts: List[Dict] = []
    status: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化服务
    http_client = httpx.AsyncClient(timeout=API_CONFIG['timeout'])
    process_manager = AgentProcessManager()
    registry = AgentRegistry(http_client)
    selector = AgentSelector()
    query_service = AgentQueryService(registry, selector)
    
    # 注入到app state
    app.state.services = {
        'http_client': http_client,
        'process_manager': process_manager,
        'registry': registry,
        'query_service': query_service,
        'selector': selector
    }
    
    yield
    
    # 清理资源
    await process_manager.stop_all()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 流式API端点
@app.post("/stream-query")
async def handle_stream_query(request: QueryRequest):
    services = app.state.services
    
    async def generate():
        # 1. 自动启动Agent（逻辑复用自原/query接口）
        if request.auto_start and not services['process_manager'].processes:
            if not await services['process_manager'].start_all():
                yield json.dumps({"type": "error", "message": "Failed to start agents"}, ensure_ascii=False) + "\n"
                return
        elif not request.auto_start:
            print("🔧 Manual mode: Agents should be started separately")
            for agent_type, config in REMOTE_AGENTS.items():
                url = f"http://localhost:{config['port']}"
                card = await services['registry'].register_agent(url)
                
        # 2. 直接调用AgentQueryService的流式方法
        async for content in services['query_service'].handle_stream_query(request.query,request.session_id):
            # 检查是否为错误字典格式
            if isinstance(content, dict) and 'type' in content and content['type'] == 'error':
                # 从错误信息中提取文本（如果需要）
                error_text = content['message'].split(': ')[-1] if ': ' in content['message'] else content['message']
                yield error_text
                # return {"root": TextPart(kind='text', metadata=None, text=error_text)}
            # 检查是否为TextPart格式
            elif hasattr(content, 'root') and isinstance(content.root, TextPart):
                yield remove_asterisks(content.root.text)
            # 处理未知格式
            else:
                # return {"root": TextPart(kind='text', metadata=None, text="无法识别的内容格式")}
                yield "无法识别的内容格式"
            # text = content.root.text
            # yield text

    def remove_asterisks(text: str) -> str:
        """
        移除文本中所有的星号（*）
        
        参数:
            text: 包含星号的原始文本
            
        返回:
            移除所有星号后的文本
        """
        return text.replace('*', '')
            

    return StreamingResponse(generate(), media_type="text/event-stream",headers={"Cache-Control": "no-cache"})

@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    services = app.state.services
    registry = services['query_service'].registry
    return registry.list_agents()


if __name__ == '__main__':
    uvicorn.run(app, host=API_CONFIG['host'], port=API_CONFIG['port'])