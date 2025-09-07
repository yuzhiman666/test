# services/agent_services.py
import asyncio
from typing import Dict, List, Optional
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, Message, Part, Role, TextPart, Task
from config.settings import REMOTE_AGENTS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from config.load_key import load_key
import base64
import json
import os
import subprocess
import time
import signal
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4
import asyncclick as click
from a2a.types import (
    AgentCard,
    FilePart,
    FileWithBytes,
    GetTaskRequest,
    JSONRPCErrorResponse,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendStreamingMessageRequest,
    Task,
    TaskArtifactUpdateEvent,
    TaskQueryParams,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
    Role
)
from typing import AsyncGenerator
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.redis import RedisSaver
from langchain_core.runnables import RunnableConfig

class AgentProcessManager:
    """管理远程Agent进程的生命周期"""
    def __init__(self):
        self.processes: Dict[str, 'RemoteAgentProcess'] = {}
    
    async def start_all(self) -> bool:
        success = True
        for agent_type, config in REMOTE_AGENTS.items():
            process = RemoteAgentProcess(
                agent_type, 
                config['port'],
                host="localhost"  # 明确传递host参数
            )
            if await process.start():
                self.processes[agent_type] = process
            else:
                success = False
        return success
    
    async def stop_all(self):
        for process in self.processes.values():
            process.stop()
        self.processes.clear()

class RemoteAgentProcess:
    """单个远程Agent进程管理"""
    def __init__(self, agent_type: str, port: int,host: str = "localhost"):
        self.agent_type = agent_type
        self.port = port
        self.host = host
        self.process = None
        self.url = f"http://{self.host}:{self.port}"
    
    async def start(self) -> bool:
        # 实现启动逻辑
        """Start the agent process"""
        try:
            print(f"🚀 Starting {self.agent_type} agent on port {self.port}...")

            # Build command
            cmd = [
                sys.executable, '-m', f'remotes.{self.agent_type}',
                '--host', self.host,
                '--port', str(self.port)
            ]

            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for startup (check if agent is responding)
            for attempt in range(30):  # 30 second timeout
                try:
                    async with httpx.AsyncClient(timeout=2) as client:
                        response = await client.get(f"{self.url}/.well-known/agent-card")
                        if response.status_code == 200:
                            print(f"✅ {self.agent_type} agent started successfully")
                            return True
                except:
                    pass
                await asyncio.sleep(1)

            print(f"❌ Failed to start {self.agent_type} agent")
            return False

        except Exception as e:
            print(f"❌ Error starting {self.agent_type}: {e}")
            return False
    
    def stop(self):
        # 实现停止逻辑
        """Stop the agent process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print(f"🛑 Stopped {self.agent_type} agent")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print(f"🔥 Killed {self.agent_type} agent")
            except Exception as e:
                print(f"⚠️ Error stopping {self.agent_type}: {e}")

class AgentRegistry:
    """Agent注册和发现服务"""
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.agents: Dict[str, AgentCard] = {}
        self.clients: Dict[str, A2AClient] = {}
    
    async def register_agent(self, url: str) -> Optional[AgentCard]:
        # 实现注册逻辑
        """Register an agent by resolving its card"""
        try:
            resolver = A2ACardResolver(self.http_client, url)
            card = await resolver.get_agent_card()
            card.url = url

            # Create A2A client for this agent
            client = A2AClient(self.http_client, agent_card=card)

            self.agents[card.name] = card
            self.clients[card.name] = client

            print(f"📋 Registered agent: {card.name}")
            print(f"   Description: {card.description}")
            print(f"   URL: {url}")

            return card

        except Exception as e:
            print(f"❌ Failed to register agent at {url}: {e}")
            return None
    
    def list_agents(self) -> List[Dict[str, str]]:
        return [
            {'name': card.name, 'description': card.description, 'url': card.url}
            for card in self.agents.values()
        ]

class AgentSelector:
    """Agent选择服务"""
    def __init__(self):
        """Init selection Agent
        """
        self.llm = ChatOpenAI(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=load_key("DASHSCOPE_API_KEY"),
                model="qwen-plus",
            )
        

    def initialize(self):
        self.checkpointer = RedisSaver("redis://localhost:6379")
        self.agent = create_react_agent(
            self.llm,
            tools=[],
            checkpointer=self.checkpointer,
            # checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            
        )

    async def select_agent(self, user_query: str, available_agents: List[Dict[str, str]], config: RunnableConfig) -> Optional[str]:
        """Select the best agent for the user query using LLM with langgraph react agent"""

        if not available_agents:
            return None

        # 构建可用Agent列表字符串
        agent_list = "\n".join([
            f"- {agent['name']}: {agent['description']}"
            for agent in available_agents
        ])

        # 构建系统提示词
        system_prompt = f"""
        You are an agent selector. Your core task is to analyze both the user's input content and the historical context of your interaction with the user, 
        and based on this comprehensive analysis, select the most suitable agent to handle the user's request.
        
        Available agents:
        {agent_list}
        
        Selection Rules:
        1. For automobile recommendation → Automobile Recommendation Agent
        2. For loan scheme suggestion → Loan Scheme Suggestion Agent
        3. For loan pre-examination → Loan Pre-examination Agent
        
        Instructions:
        - Only return the exact name of the agent from the available agents list
        - Do not provide any explanations or additional text
        - If no suitable agent is found, return "None"
        """

        try:
            self.SYSTEM_INSTRUCTION = system_prompt
            # Agent选择器初始化
            self.initialize()
            result = self.agent.invoke({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ]
            },config=config)
            
            selected_agent_name = result["messages"][-1].content.strip()
            
            # 验证返回结果是否有效
            if selected_agent_name == "None":
                return None
                
            valid_agent_names = [agent["name"] for agent in available_agents]
            if selected_agent_name in valid_agent_names:
                return selected_agent_name
            else:
                print(f"❌ Agent {selected_agent_name} is not in available agents list")
                return None

        except Exception as e:
            print(f"❌ Error selecting agent with langgraph react agent: {e}")
            return None

class AgentQueryService:
    """统一查询处理服务"""
    def __init__(self, registry: AgentRegistry, selector: AgentSelector):
        self.registry = registry
        self.selector = selector

#流式处理方法
    async def handle_stream_query(self, query: str,session_id: str) -> AsyncGenerator[Dict, None]:
        """统一处理流式查询，返回异步生成器"""
        try:
            # 1. 获取可用Agent列表
            available_agents = self.registry.list_agents()
            if not available_agents:
                yield {"type": "error", "message": "No agents available"}
                return

            # 2. 选择Agent
            config: RunnableConfig = {'configurable': {'thread_id': session_id}}

            selected_agent_name = await self.selector.select_agent(query, available_agents, config)
            if not selected_agent_name:
                yield {"type": "error", "message": "No suitable agent found"}
                return

            # 3. 获取Agent客户端
            client = self.registry.clients.get(selected_agent_name)
            if not client:
                yield {"type": "error", "message": f"Agent client not found: {selected_agent_name}"}
                return

            # 4. 构建消息
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text=query))],
                messageId=str(uuid4()),
            )
            payload = MessageSendParams(
                id=str(uuid4()),
                message=message,
                configuration=MessageSendConfiguration(
                    acceptedOutputModes=['text', 'text/plain'],
                ),
                metadata={"session_id": session_id}
            )

            # 5. 流式处理响应(流式传输需要每一层（Remote → Host → Client）都支持逐字/分片处理,代码需要修改)
            async for chunk in self._process_streaming_response(client, payload, selected_agent_name):
                if chunk.get("type") == "status":
                    text = chunk["text"][0]
                    yield text

        except Exception as e:
            yield {"type": "error", "message": str(e)}

    async def _process_streaming_response(self, client, payload, agent_name) -> AsyncGenerator[Dict, None]:
        """处理流式响应，确保提取消息内容"""
        async for event in client.send_message_streaming(SendStreamingMessageRequest(id=str(uuid4()), params=payload)):
            if isinstance(event.root, JSONRPCErrorResponse):
                yield {"type": "error", "message": f"Agent error: {event.root.error}"}
                continue

            result = event.root.result
            if isinstance(result, Message):
                yield {
                    "type": "message",
                    "content": self._extract_message_content(result),
                    "agent_name": agent_name
                }
            # elif isinstance(result, TaskStatusUpdateEvent):
            elif isinstance(result, TaskStatusUpdateEvent) and not result.final:
                yield {
                    "type": "status",
                    "task_id": result.taskId,
                    "status": result.status.state,
                    "agent_name": agent_name,
                    "text": result.status.message.parts#Remote端流式输出的内容
                }
                if result.status.state == "completed":
                    task_result = await client.get_task(GetTaskRequest(
                        id=str(uuid4()),
                        params=TaskQueryParams(id=result.taskId)
                    ))
                    if isinstance(task_result.root.result, Task):
                        async for item in self._extract_task_result(task_result.root.result, agent_name):
                            yield item  # 使用 async for 替代 yield from
            elif isinstance(result, TaskArtifactUpdateEvent):
                yield {
                    "type": "artifact",
                    "task_id": result.taskId,
                    "artifact": {
                        "name": result.artifact.name,
                        "content": [part.root.text for part in result.artifact.parts 
                                if hasattr(part, 'root') and hasattr(part.root, 'text')]
                    },
                    "agent_name": agent_name
                }

    async def _extract_task_result(self, task: Task, agent_name: str) -> AsyncGenerator[Dict, None]:
        """从已完成的任务中提取消息历史"""
        if hasattr(task, 'history') and task.history:
            for msg in task.history:
                # 修改为兼容字符串或枚举的写法
                if getattr(msg, 'role', None) == 'assistant' or (
                    hasattr(Role, 'assistant') and msg.role == Role.assistant
                ):
                    yield {
                        "type": "message",
                        "content": self._extract_message_content(msg),
                        "agent_name": agent_name
                    }


    def _extract_message_content(self, message: Message) -> str:
        """Extract text content from Message object"""
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                text_parts.append(part.root.text)
            elif hasattr(part, 'text'):
                text_parts.append(part.text)
        return " ".join(text_parts)
