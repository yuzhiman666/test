from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import uuid
# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI(
    title="Customer Loan API",
    description="API for retrieving customer loan data with pending status",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class State(BaseModel):
    data: Optional[Dict[str, Any]] = None
    contract: Optional[str] = None
    thread_id: Optional[str] = None
    finalized: bool = False
    
    class Config:
        extra = "allow"
memory = MemorySaver()
active_sessions = {}  # thread_id -> state dict

# 修改检查数据节点
def check_data(state: State) -> dict:
    if not state.data or "parties" not in state.data:
        raise HTTPException(status_code=400, detail="Invalid data: missing parties")
    return state.model_dump()  # 改为 model_dump()

# 修改创建合同节点
def create_contract(state: State) -> dict:
    parties = state.data.get("parties", [])
    contract_text = f"Contract Agreement between {', '.join(parties)}\n"
    contract_text += "This is a sample contract generated based on provided data.\n"
    
    new_state = state.model_copy()
    new_state.contract = contract_text
    return new_state.model_dump()  # 改为 model_dump()

def human_review(state: State) -> Command[Literal["finalize_contract", "reject_contract"]]:
    # 直接返回中断和需要人工介入的信息
    is_approved = interrupt({
        "question": "Please review the contract.",
        "contract": state.contract
    })

    if is_approved["type"] == "approve":
        return Command(goto="finalize_contract")
    else:
        return Command(goto="reject_contract")

# 修改最终确认节点
def finalize_contract(state: State) -> dict:
    new_state = state.model_copy()
    new_state.finalized = True
    print(f"✅ Contract finalized for thread: {state.thread_id}")
    # print(f"Finalized Contract: {new_state.model_dump()}")
    return new_state.model_dump()  # 改为 model_dump()

# 修改拒绝节点
def reject_contract(state: State) -> dict:
    new_state = state.model_copy()
    new_state.finalized = False
    print(f"❌ Contract rejected for thread: {state.thread_id}")
    return new_state.model_dump()  # 改为 model_dump()

# 创建工作流图
builder = StateGraph(State)
builder.add_node("check_data", check_data)
builder.add_node("create_contract", create_contract)
builder.add_node("human_review", human_review)
builder.add_node("finalize_contract", finalize_contract)
builder.add_node("reject_contract", reject_contract)
builder.add_node("end", lambda state: state)

# 设置工作流路径
builder.set_entry_point("check_data")
builder.add_edge("check_data", "create_contract")
builder.add_edge("create_contract", "human_review")
builder.add_edge("finalize_contract", "end")
builder.add_edge("reject_contract", "end")

# 编译工作流 - 不再需要指定中断点
graph = builder.compile(checkpointer=memory)

# 连接MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    # 测试连接
    client.admin.command("ping")
    db = client["customer_db"]
    customers_collection = db["customers"]
    print("Successfully connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise

# Pydantic模型定义 - 对应Customer接口
class Customer(BaseModel):
    id: str
    name: str
    age: int
    idNumber: str
    monthlyIncome: float
    annualIncome: float
    employmentTenure: float
    employmentPosition: str
    delinquencies: int
    creditLines: int
    loanAmount: float
    loanPurpose: str
    status: str
    verificationStatus: str

    class Config:
        from_attributes = True  # 替代v1的orm_mode=True

class LoanApprovalRequest(BaseModel):
    user_id: str
    human_reult: str
    thread_id: str
    feedback: Optional[str] = ""

class StartRequest(BaseModel):
    data: Dict[str, Any]

@app.post("/start-workflow")
async def start_workflow(request: StartRequest):
    try:
        thread_id = "a3051992-88ee-4949-ac7c-4795e2f4bf59"
        config = {"configurable": {"thread_id": thread_id}}
        print("*"*100)
        print(thread_id)
        print("*"*100)
        
        initial_state = State(data=request.data, thread_id=thread_id)
        
        # 运行工作流直到第一次中断
        result = await graph.ainvoke(
            initial_state, 
            config=config,
            stream_mode="values"
        )
        
        # 保存当前状态
        active_sessions[thread_id] = result
        
        # 检查是否在human_review节点中断
        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0].value
            return {
                "thread_id": thread_id,
                "status": "waiting_for_review",
                "message": interrupt_data.get("question"),
                "contract": interrupt_data.get("contract")
            }
        else:
            # 如果没有中断，直接返回最终状态
            return {
                "thread_id": thread_id,
                "status": "completed",
                "finalized": result.finalized,
                "message": "Workflow completed without review"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

# API路由
@app.get("/customers/pending", response_model=List[Customer], status_code=status.HTTP_200_OK)
async def get_pending_customers():
    """获取所有状态为pending的客户数据"""
    try:
        pending_customers = list(customers_collection.find({"status": "pending"}))
        # 转换MongoDB的ObjectId为字符串（如果需要）
        for customer in pending_customers:
            if "_id" in customer:
                customer["id"] = str(customer["_id"])
                del customer["_id"]
        return pending_customers
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/customers/pending/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def get_pending_customer(customer_id: str):
    """根据ID获取特定的pending状态客户数据"""
    try:
        customer = customers_collection.find_one({"id": customer_id, "status": "pending"})
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pending customer with ID {customer_id} not found"
            )
        
        # 处理MongoDB的ObjectId
        if "_id" in customer:
            del customer["_id"]
            
        return customer
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/loan/approve")
async def handle_approve_loan(request: LoanApprovalRequest):
    try:
        if request.thread_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        config = {"configurable": {"thread_id": request.thread_id}}
        
        print("#"*100)

        # 根据用户输入创建继续命令
        command = Command(
            resume={"type": request.human_reult.lower()},
            # goto="finalize_contract" if request.approval.lower() == "approve" else "reject_contract"
        )
        print(f"Submitting review for thread {request.thread_id}: {request.human_reult}")
        # 继续执行工作流
        result = await graph.ainvoke(
            command,
            config=config
        )
        print(f"Workflow result for thread {request.thread_id}: {result}")
        return {
            "thread_id": request.thread_id,
            "status": "completed",
            "approval": request.human_reult.lower() == "approve",
            "finalized": result["finalized"],  # 直接从字典获取
            "message": "Workflow completed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="服务器处理请求时发生错误")

# 启动逻辑
if __name__ == "__main__":
    import uvicorn
    # 可以在这里配置host和port
    uvicorn.run(
        "main:app",  # 指向当前模块的app实例
        host="0.0.0.0",  # 允许外部访问
        port=8000,
        reload=True  # 开发模式下自动重载
    )
    