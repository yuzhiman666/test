import logging
from collections.abc import AsyncIterable
from typing import Any, Literal
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatTongyi
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
from src.config.load_key import load_key
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
# memory = MemorySaver()
DATABASE_URL = "mysql+mysqlconnector://root:123456@localhost:3306/bmw_automobile"

class ResponseFormat(BaseModel):
    """向用户返回响应的标准格式。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str = Field(description="Detailed response message. For the input_required status, it is necessary to specify what information is required. For the error status, it is necessary to explain what the problem is.")


class AutoRecommendAgent:
    """Auto Recommend Agent

    Recommend automobile to users according to their requirements
    """

#     SYSTEM_PROMPT_TEMPLATE = """You are an agent designed to interact with a SQL database.
# Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
# Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
# You have access to tools for interacting with the database.
# Only use the below tools. Only use the information returned by the below tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

# To start you should ALWAYS look at the tables in the database to see what you can query.
# DO NOT skip this step.
# Then you should query the schema of the most relevant tables.
# If the user needs to provide more information, please set the response status to input_required.
# If an error occurs when processing the request, please set the response status to Error. 
# When you have completed your reply, please set the response status to Completed.

# ### Core Constraints (Must be strictly followed in all interaction rounds):
# 1. You may only construct, debug, and execute SQL statements within your **pure internal thinking process**. This process must never appear in any form of output content.
# 2. **All content in the streaming output** (including but not limited to intermediate analysis, logical reasoning, conclusion summaries, format markers, etc.) must **not contain SQL statements in any form**. This includes prohibitions on code blocks, comments, or natural language descriptions of SQL operations (e.g., phrases like "I queried with SELECT * FROM..." are not allowed).
# 3. Output content may only include natural language interpretations, analyses, and conclusions of query results, and must be presented in **pure Markdown format** (prohibiting any code block syntax such as ```sql or `SELECT`).
# 4. In multi-turn conversations, regardless of whether the user's question requires adjusting query logic, the above constraints must be strictly maintained. Do not relax the restrictions due to increasing conversation rounds.

# ### Additional Requirements:
# - To facilitate subsequent interactions, recommended content must be accompanied by a model_id, presented in a hidden format (e.g., `<!-- model_id:123 -->`).
# - Visual content should be clearly presented via Markdown formats (such as tables, lists), avoiding any expressions that might imply SQL.
# """
    SYSTEM_PROMPT_TEMPLATE = """
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Critical Data Constraint
    You must only invoke the designated tools to query the database's existing data. All recommendations provided must be strictly based on the actual data retrieved from the database—under no circumstances should you fabricate or invent any data that is not present in the database.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table; only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer and recommendations.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at the tables in the database to see what you can query.
    DO NOT skip this step.
    Then you should query the schema of the most relevant tables.
    If the user needs to provide more information, please set the response status to input_required.
    If an error occurs when processing the request, please set the response status to Error.
    When you have completed your reply, please set the response status to Completed.
    ### Core Constraints (Must be strictly followed in all interaction rounds):
    You may only construct, debug, and execute SQL statements within your pure internal thinking process. This process must never appear in any form of output content.
    All content in the streaming output (including but not limited to intermediate analysis, logical reasoning, conclusion summaries, format markers, etc.) must not contain SQL statements in any form. This includes prohibitions on code blocks, comments, or natural language descriptions of SQL operations (e.g., phrases like "I queried with SELECT * FROM..." are not allowed).
    Output content may only include natural language interpretations, analyses, conclusions, and recommendations derived from query results, and must be presented in pure Markdown format (prohibiting any code block syntax such as ```sql or SELECT).
    In multi-turn conversations, regardless of whether the user's question requires adjusting query logic, the above constraints must be strictly maintained. Do not relax the restrictions due to increasing conversation rounds.
    IMPORTANT: 
    Only recommend the car models included in the database; it is forbidden to recommend any car models outside the database.
    and under no circumstances should the output include the SQL query itself. Do not mention, display, or describe any SQL statements at any point in your response. Only output the final natural language answer derived from the query results.
    and please strictly limit the output content to within 300 words, ensuring the information is complete, the expression is concise, and redundant statements are avoided.
    ### Additional Requirements:
    - To facilitate subsequent interactions, all recommended content must be accompanied by a complete and valid model_id. The model_id must not be missing, truncated, or in an invalid format, and it must be presented in a hidden format (e.g., <!-- model_id:123456 -->). Ensure the integrity of the model_id value is preserved in every instance where recommendations are provided.
    - Visual content should be clearly presented via Markdown formats (such as tables, lists), avoiding any expressions that might imply SQL.
    """
    def __init__(self):
        """Init Automobile Recommendation Agent
        """
        #ChatOpenAI不支持下面Agent实例中的response_format设定
        # self.model = ChatOpenAI(
        self.model = ChatTongyi(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=load_key("DASHSCOPE_API_KEY"),
            model="qwen-plus",
        )
        self.engine = create_engine(DATABASE_URL)
        self.db = SQLDatabase(self.engine)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.model)
        self.tools = self.toolkit.get_tools()
        self.prompt_template = self.SYSTEM_PROMPT_TEMPLATE
        self.system_message = self.prompt_template.format(dialect="MySQL", top_k=1)
        
        
    async def initialize(self):
        self.checkpointer = AsyncRedisSaver("redis://localhost:6379")
        self.graph = create_react_agent(
            model = self.model, 
            tools=self.tools, 
            prompt=self.system_message,
            checkpointer=self.checkpointer
            # checkpointer=memory
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