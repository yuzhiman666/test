from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import uuid

class State(BaseModel):
    data: Optional[Dict[str, Any]] = None
    contract: Optional[str] = None
    thread_id: Optional[str] = None
    finalized: bool = False
    
    class Config:
        extra = "allow"

app = FastAPI(title="Human-in-Loop Contract Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class StartRequest(BaseModel):
    data: Dict[str, Any]

class ReviewRequest(BaseModel):
    thread_id: str
    approval: str

@app.post("/start-workflow")
async def start_workflow(request: StartRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
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

@app.post("/submit-review")
async def submit_review(request: ReviewRequest):
    try:
        if request.thread_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # 根据用户输入创建继续命令
        command = Command(
            resume={"type": request.approval.lower()},
            # goto="finalize_contract" if request.approval.lower() == "approve" else "reject_contract"
        )
        print(f"Submitting review for thread {request.thread_id}: {request.approval}")
        # 继续执行工作流
        result = await graph.ainvoke(
            command,
            config=config
        )
        print(f"Workflow result for thread {request.thread_id}: {result}")
        return {
            "thread_id": request.thread_id,
            "status": "completed",
            "approval": request.approval.lower() == "approve",
            "finalized": result["finalized"],  # 直接从字典获取
            "message": "Workflow completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit review: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)