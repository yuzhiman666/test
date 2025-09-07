from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool, tool
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI(
    title="宝马汽车金融贷款申请分析API",
    description="分析用户的汽车贷款申请信息并提供合理化建议",
    version="1.0.0"
)

# 定义数据模型
class LoanApplication(BaseModel):
    """贷款申请信息模型"""
    name: str = Field(..., description="申请人姓名")
    age: int = Field(..., ge=18, le=70, description="申请人年龄，必须在18-70岁之间")
    phone: str = Field(..., description="申请人手机号码")
    email: Optional[str] = Field(None, description="申请人电子邮箱")
    monthly_income: float = Field(..., gt=0, description="月收入，必须大于0")
    loan_amount: float = Field(..., gt=0, description="贷款金额，必须大于0")
    loan_term: int = Field(..., ge=12, le=60, description="贷款期限(月)，必须在12-60个月之间")
    car_model: str = Field(..., description="意向车型")
    down_payment: float = Field(..., gt=0, description="首付款金额，必须大于0")
    has_credit_card: bool = Field(..., description="是否有信用卡")
    credit_score: Optional[int] = Field(None, ge=300, le=850, description="信用评分，300-850之间")

# 定义工具函数 - 可以根据需要扩展更多工具
@tool
def calculate_debt_to_income(monthly_income: float, loan_amount: float, loan_term: int) -> str:
    """
    计算债务收入比(DTI)，评估贷款偿还能力
    
    参数:
    monthly_income: 月收入
    loan_amount: 贷款金额
    loan_term: 贷款期限(月)
    
    返回:
    债务收入比计算结果和评估
    """
    # 简单计算月供(未考虑利率)
    monthly_payment = loan_amount / loan_term
    dti = (monthly_payment / monthly_income) * 100
    
    assessment = ""
    if dti < 20:
        assessment = "债务收入比非常健康，贷款偿还压力小"
    elif dti < 36:
        assessment = "债务收入比良好，贷款偿还压力适中"
    else:
        assessment = "债务收入比偏高，贷款偿还可能存在压力"
    
    return f"债务收入比: {dti:.2f}%\n评估: {assessment}"

@tool
def evaluate_down_payment(down_payment: float, loan_amount: float) -> str:
    """
    评估首付款比例是否合理
    
    参数:
    down_payment: 首付款金额
    loan_amount: 贷款金额
    
    返回:
    首付款比例评估结果
    """
    total_price = down_payment + loan_amount
    down_payment_ratio = (down_payment / total_price) * 100
    
    assessment = ""
    if down_payment_ratio >= 30:
        assessment = "首付款比例较高，有利于获得更优的贷款利率和审批通过率"
    elif down_payment_ratio >= 20:
        assessment = "首付款比例适中，符合常规贷款要求"
    else:
        assessment = "首付款比例偏低，可能影响贷款审批或导致利率上升"
    
    return f"首付款比例: {down_payment_ratio:.2f}%\n评估: {assessment}"

@tool
def analyze_credit_score(credit_score: Optional[int]) -> str:
    """
    分析信用评分对贷款的影响
    
    参数:
    credit_score: 信用评分，300-850之间，可能为None
    
    返回:
    信用评分评估结果
    """
    if not credit_score:
        return "未提供信用评分。建议补充信用评分信息，这将有助于更准确地评估贷款申请。"
    
    if credit_score >= 700:
        return f"信用评分优秀({credit_score})，很可能获得较低的贷款利率和较高的贷款额度"
    elif credit_score >= 640:
        return f"信用评分良好({credit_score})，一般可以获得常规的贷款利率和额度"
    elif credit_score >= 580:
        return f"信用评分一般({credit_score})，可能会面临稍高的利率或额外的审批要求"
    else:
        return f"信用评分较低({credit_score})，可能会影响贷款审批，建议改善信用状况后再申请"

# 获取工具列表
tools = [calculate_debt_to_income, evaluate_down_payment, analyze_credit_score]

# 初始化语言模型
llm = ChatOpenAI(
    model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    temperature=0.3  # 较低的随机性，确保结果更稳定
)

# 创建AI Agent
agent = create_react_agent(llm, tools)

"""
你是宝马汽车金融贷款的专业顾问，负责分析用户的贷款申请信息并提供合理化建议。

请根据用户提供的申请信息，结合你的专业知识和可用工具，完成以下任务：
1. 评估用户的贷款申请是否合理
2. 分析用户的还款能力
3. 提供关于贷款金额、期限、首付比例等方面的建议
4. 指出申请材料中可能存在的不足或需要补充的信息
5. 给出提高贷款审批通过率的建议

你的建议应当专业、具体、有建设性，并且符合宝马汽车金融的相关政策。
"""

# 定义系统提示
SYSTEM_PROMPT = """You act as a car loan information filling assistant. 
You need to check for input errors based on the user's input content and provide professional suggestions. 
Under the premise of fully complying with regulatory requirements, guide users to avoid potential risks, 
inform them of effective methods that help improve the approval rate, 
and assist customers in passing the loan review more smoothly."""

# 定义API端点
@app.post("/analyze-loan-application", response_model=dict)
async def analyze_loan_application(application: LoanApplication):
    """
    分析用户的汽车贷款申请信息，返回AI生成的合理化建议
    """
    try:
        # 构建用户消息
        user_message = f"""
        贷款申请人信息：
        姓名：{application.name}
        年龄：{application.age}
        电话：{application.phone}
        邮箱：{application.email or '未提供'}
        月收入：{application.monthly_income}元
        贷款金额：{application.loan_amount}元
        贷款期限：{application.loan_term}个月
        意向车型：{application.car_model}
        首付款：{application.down_payment}元
        是否有信用卡：{'是' if application.has_credit_card else '否'}
        信用评分：{application.credit_score or '未提供'}
        
        请分析以上信息并提供贷款申请的合理化建议。
        """
        
        # 准备Agent的输入
        initial_state = {
            "messages": [
                ("system", SYSTEM_PROMPT),
                ("user", user_message)
            ]
        }
        
        # 运行Agent
        result = agent.invoke(initial_state)
        
        # 提取并返回结果
        return {
            "status": "success",
            "applicant_name": application.name,
            "analysis": result["messages"][-1].content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析过程中出现错误: {str(e)}")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bmw-finance-analysis-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
