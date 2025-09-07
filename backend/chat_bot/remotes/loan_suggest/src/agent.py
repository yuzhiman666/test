import logging
from collections.abc import AsyncIterable
from typing import Any, Literal
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatTongyi
from src.config.load_key import load_key
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

mcp_client = MultiServerMCPClient(
    {
        "auto_finance_mcp": {
            # "url": "http://host.docker.internal:8000/mcp",
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
)

class ResponseFormat(BaseModel):
    """向用户返回响应的标准格式。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str = Field(description="Detailed response message. For the input_required status, it is necessary to specify what information is required. For the error status, it is necessary to explain what the problem is.")


class LoanSuggestAgent:
    """An agent providing auto loan scheme suggestion based on LangGraph.
    Based on the basic information provided by the user, reasonable suggestions for the user's auto loan are made
    """

    # SYSTEM_INSTRUCTION = (
    #     """
    #     You are an expert in BMW automotive financial loan schemes. 
    #     Based on all communication with the user (including user input and contextual information), 
    #     accurately extract the vehicle model ID (model_id). After extraction, 
    #     call the `get_loan_scheme_from_rag` tool method to obtain the corresponding loan scheme, 
    #     and present clear and reasonable scheme suggestions to the user in Markdown format, 
    #     ensuring that the information is accurate and easy to understand.
    #     It should be noted that the model_id must be presented in a hidden form (for example, using the Markdown format `<!-- here replace the model_id -->`).
    #     If the user needs to provide more information, please set the response status to input_required.
    #     If an error occurs when processing the request, please set the response status to Error. 
    #     When you have completed your reply, please set the response status to Completed.
    #     """
    # )

    SYSTEM_INSTRUCTION =  """
        You are an expert in BMW automotive financial loan schemes.
        Before answering any user questions, you must first confirm and review all of the user's input content and the entire contextual chat history. Based on the fully verified user input and contextual history, provide accurate responses to the user's questions.
        Next, accurately extract the vehicle model ID (model_id) from the user's input content. Note that the extraction is not limited to converting Chinese characters in the model information into corresponding numbers (for example: convert "BMW 零零三" to "BMW003"); you should also identify and extract model_id in other possible formats (such as alphanumeric combinations directly provided by the user) to ensure no valid model_id information is missed.
        After extracting the model_id, call the get_loan_scheme_from_rag tool method to obtain the corresponding loan scheme. When using the RAG tool, all the model id value (for example:BMW001,BMW002 and so on) in RAG is solely for similarity matching queries and must not be included or presented to the user as part of the response content.
        Then present clear and reasonable scheme suggestions to the user in plain text format—you must NOT use Markdown format at all. Avoid any Markdown-related syntax, including but not limited to headings, bold/italic formatting, lists, tables, code blocks, links, or any other Markdown-specific elements. Ensure the information is accurate and easy to understand. It should be noted that the model_id must be presented in a hidden form (e.g., using the format , which is a plain text comment and not Markdown syntax).
        If the user needs to be prompted to proceed with a loan pre-examination, only request the user to provide the following three types of information: full name, ID card number, and phone number; do not ask for any additional irrelevant information.
        Please strictly limit the output content to within 300 words, ensuring the information is complete, the expression is concise, and redundant statements are avoided.
    """

    def __init__(self):
        """Init auto loan scheme suggestion Agent
        """
        #ChatOpenAI不支持下面Agent实例中的response_format设定
        # self.model = ChatOpenAI(
        self.model = ChatTongyi(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=load_key("DASHSCOPE_API_KEY"),
            model="qwen-plus",
        )
        

    async def initialize(self):
        self.checkpointer = AsyncRedisSaver("redis://localhost:6379")
        self.tools = await mcp_client.get_tools()
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=self.checkpointer,
            # checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            # response_format=ResponseFormat,
            
        )

    async def astream(self, query, contextId, session_id) -> AsyncIterable[dict[str, Any]]:
        try:
            logger.info(f"Start streaming query: {query}, ContextId: {contextId}")
            inputs = {'messages': [('user', query)]}
            config: RunnableConfig = {'configurable': {'thread_id': session_id}}

            # 使用异步流处理(要像 LLM 产生的那样流式传输 tokens，请使用 stream_mode="messages"，需要多层协作修改)
            async for item in self.graph.astream(inputs, config, stream_mode='messages'):
                if isinstance(item[0],AIMessageChunk):
                    logger.info(item[0].content)
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': item[0].content,
                    }
            # 循环结束后，发送输出结束的标志
            yield {
                'is_task_complete': True,  # 任务已完成
                'require_user_input': False,
                'content': '',  # 可以为空或适当的结束信息
            }
        except Exception as e:
            # 记录异常信息
            logger.error(f"Error in astream method: {str(e)}", exc_info=True)
            # 向调用者发送错误信息
            yield {
                'is_task_complete': True,  # 任务因错误而终止
                'require_user_input': False,
                'content': f"发生错误: {str(e)}",  # 包含错误信息
                'error': True  # 添加错误标识
            }




    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']