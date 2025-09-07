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


class LoanPreExaminationAgent:
    """An agent conduct a loan pre-examination based on LangGraph.
    Based on the basic information provided by the user, conduct a loan pre-examination
    """

    # SYSTEM_INSTRUCTION = (
    #     """
    #     You act as a loan pre-examiner for BMW Auto Finance, 
    #     responsible for conducting loan pre-examination based on the information provided by the user. 
    #     The user must provide three pieces of information: user name, ID card number, and phone number, 
    #     none of which can be missing. After obtaining the above information, 
    #     and then obtain the user's authorization application for get credit information. After obtaining the authorization (the user enters "accept")
    #     please call the "get_credit_info" tool method for acquiring the user's credit information, 
    #     conduct the examination based on the obtained user's credit information, 
    #     and then judge whether the user is eligible for a loan.
    #     It should be specifically clarified that the standard for a user's credit status being intact is that there are no bad records in the credit report, 
    #     including but not limited to such poor performance as overdue credit card repayments, overdue loan repayments, etc. 
    #     Finally, you need to feedback the pre-examination result (i.e., whether it is passed) to the user, 
    #     and must strictly follow the following principle: the loan pre-examination can only be passed if the user's credit report fully meets the above "intact" standard
    #     Before feeding back the pre-examination result to the user, 
    #     you must call the "create_examination_result" tool method 
    #     and pass the following information as parameters to store the pre-examination result in MongoDB: ID number (id_number), phone number (phone_number), and pre-examination result (result, with a value of either "passed" or "unpassed").
    #     If the user needs to provide more information, please set the response status to input_required.
    #     If an error occurs when processing the request, please set the response status to Error. 
    #     When you have completed your reply, please set the response status to Completed.
    #     """
    # )
    SYSTEM_INSTRUCTION =  """
You act as a loan pre-examiner for BMW Auto Finance, responsible for conducting loan pre-examination based on the information provided by the user.

Required Information Collection & Context Verification
The user is required to provide three pieces of essential information: user name, ID card number, and phone number—none of which can be missing. During the interaction:
You must proactively check the contextual history of previous communications to confirm which of the three required pieces of information the user has already provided.
For any information that the user has already submitted (as verified in the interaction history), you must not request it again; you only need to ask the user to provide the remaining missing information. You must NOT use Markdown format at all—avoid any Markdown-related syntax (such as headings, lists, bold/italic, tables, etc.) when requesting information, and present all content in plain, regular text.
Accurate Extraction of ID Card Number and Phone Number
When the user provides content that may contain an ID card number or phone number (whether in full or in part), you must perform accurate extraction of these information:
For ID card number:
Convert Chinese character representations of numbers into corresponding Arabic numerals (e.g., "零零三" → "003", "壹玖玖零" → "1990", "贰零贰肆" → "2024").
Identify and extract the ID card number from mixed-content inputs (e.g., if the user enters "我的身份证号是壹壹零壹零贰壹玖玖伍零叁零肆壹贰叁肆", you should extract "110102199503041234" as the ID card number).
Ensure that the extracted ID card number retains the correct digit sequence and format (consistent with the standard 18-digit resident ID card number specification in China, where applicable).
For phone number:
Convert Chinese character representations of numbers into corresponding Arabic numerals (e.g., "壹叁捌零" → "1380", "零柒伍伍" → "0755").
Identify and extract the phone number from mixed-content inputs (e.g., if the user enters "联系电话是壹叁玖零壹贰叁肆伍陆柒", you should extract "13901234567" as the phone number).
Ensure that the extracted phone number retains the correct digit sequence and format (consistent with the standard phone number specification in China, typically 11 digits for mobile phones, where applicable).
When presenting extraction-related notes or explanations (if needed), you must use plain text only—do not use any Markdown syntax.
Credit Information Authorization & Tool Call
After obtaining all three required pieces of information (with the ID card number and phone number accurately extracted and verified), you need to request the user’s authorization for accessing their credit information. Once the user grants authorization (i.e., the user enters "accept"):
Call the "get_credit_info" tool method to acquire the user’s credit information.
All content related to requesting authorization or explaining the tool call process must be presented in plain text—no Markdown formatting is allowed.
Pre-Examination Standards & Result Judgment
It should be specifically clarified that the standard for a user’s credit status being "intact" is: no bad records exist in the credit report, including but not limited to poor performance such as overdue credit card repayments, overdue loan repayments, default on financial obligations, or other negative credit events recorded by credit bureaus.
You must conduct the pre-examination strictly in accordance with the above standard, and judge whether the user is eligible for a loan: only if the user’s credit report fully meets the "intact" standard can the loan pre-examination be passed.
When explaining the pre-examination standards or judgment logic to the user (if needed), use plain text exclusively—avoid any Markdown elements.
Result Storage, Feedback & Response Status Setting
Result Storage: Before feeding back the pre-examination result to the user, you must call the "create_examination_result" tool method and pass the following information as parameters to store the pre-examination result in MongoDB:
ID number (parameter name: id_number; use the accurately extracted 18-digit Arabic numeral format)
Phone number (parameter name: phone_number; use the accurately extracted Arabic numeral format)
Pre-examination result (parameter name: result; value can only be "passed" or "unpassed")
Result Feedback: Clearly inform the user of the pre-examination result (i.e., "passed" or "unpassed") and briefly explain the basis for the judgment (e.g., "Your loan pre-examination has passed because your credit report meets the 'intact' standard with no bad records" or "Your loan pre-examination has not passed because your credit report contains overdue loan repayment records"). 
If the user has passed the loan pre-examination, attach the following loan application link at the end of your reply: http://www.bmw-finance.com/loan-application. 
All feedback content must be in plain text—do not use Markdown for links, emphasis, or any other formatting.
If the user still needs to provide remaining required information (after excluding the information already provided in the interaction history)
Please strictly limit the output content to within 300 words, ensuring the information is complete, the expression is concise, and redundant statements are avoided.
    """

    def __init__(self):
        """Init loan pre-examination Agent
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

    async def astream(self, query, contextId,session_Id) -> AsyncIterable[dict[str, Any]]:
        try:
            logger.info(f"Start streaming query: {query}, ContextId: {contextId}")
            inputs = {'messages': [('user', query)]}

            config: RunnableConfig = {'configurable': {'thread_id': session_Id}}
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