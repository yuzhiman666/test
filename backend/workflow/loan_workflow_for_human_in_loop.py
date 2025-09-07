import sys
import os
import redis
from redis import Redis
# 将项目根目录添加到 Python 搜索路径
from utils.path_utils import PROJECT_ROOT
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
from langgraph.graph import StateGraph, START, END
from langchain_core.language_models import BaseChatModel
from agents.state import LoanApplicationState
from agents.data_collect_agent import DataCollectAgent
from agents.data_review_agents import (
    CreditRatingAgent, ComplianceAgent, FraudDetectionAgent
)
from agents.decision_making_agent import DecisionMakingAgent
from agents.loan_structuring_agents import LoanStructuringAgent, LoanContractGenerater, LoanComplianceChecker, ContractTempAndContentModifier
from langgraph.types import interrupt
from langgraph.checkpoint.redis import RedisSaver
from redisvl.index import SearchIndex
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from config.load_key import load_key
from langchain_core.runnables.config import RunnableConfig 

class LoanWorkflow:

    def __init__(self, llm: BaseChatModel, mongoClient):
        """ 初始化Agent"""
        # 设置Redis环境变量
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
        # 为三类检查点索引分别设置过期时间（均为1天，86400秒）
        ttl_config = {
            "checkpoints": 86400,
            "checkpoint_blobs": 86400,
            "checkpoint_writes": 86400
        }
        # 初始化Redis检查点存储
        with RedisSaver.from_conn_string(os.environ["REDIS_URL"], ttl=ttl_config) as redis_saver:
                self.checkpointer = redis_saver

        # redis client初始化
        self.redis_client = Redis.from_url(os.environ["REDIS_URL"])
        # 向量化模型初始化
        embedding_model = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=load_key("DASHSCOPE_API_KEY")
        )
        config = RedisConfig(
            index_name="auto-rag",
            redis_url=os.environ.get('REDIS_URL')
        )
        # 向量数据库初始化
        self.redis_vector_store = RedisVectorStore(embedding_model, config=config)
        self.mongoClient = mongoClient
        self.data_collect_agent = DataCollectAgent()
        self.credit_agent = CreditRatingAgent()
        self.compliance_agent = ComplianceAgent(self.redis_vector_store, llm)
        self.fraud_agent = FraudDetectionAgent(llm, self.mongoClient)
        self.decision_agent = DecisionMakingAgent(llm)
        self.structuring_agent = LoanStructuringAgent(llm)
        self.contract_generater_agent = LoanContractGenerater(llm)
        self.contract_compliance_agent = LoanComplianceChecker(llm)
        self.contract_modify_agent = ContractTempAndContentModifier(llm)
        # 配置最大循环次数
        self.max_dialogue_loops = 5
        # 构建工作流图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(LoanApplicationState)
        
        # 添加节点
        graph.add_node("data_collect", self.data_collect_agent.process)
        graph.add_node("parallel_start", self.parallel_start)
        graph.add_node("credit_rating", self.credit_agent.process)
        graph.add_node("fraud_detection", self.fraud_agent.process)
        graph.add_node("compliance_check", self.compliance_agent.process)
        graph.add_node("wait_for_checks", self.wait_for_checks)
        graph.add_node("decision_making", self.decision_agent.process)
        graph.add_node("human_review", self.human_review_process)
        graph.add_node("loan_structuring", self.structuring_agent.process)
        graph.add_node("contract_generation", self.contract_generater_agent.process)
        graph.add_node("regulatory_review", self.contract_compliance_agent.process)
        graph.add_node("contract_modify", self.contract_modify_agent.process)
        graph.add_node("contract_completed", self.contract_completed)
        
        # 定义流程
        graph.add_edge(START, "data_collect")
        
        # 数据收集完成后进入并行处理
        graph.add_conditional_edges(
            "data_collect",
            lambda s: s["data_collection_status"],
            {
                "completed": "parallel_start",
                "failed": END
            }
        )
        
        # 并行处理起点 - 连接三个并行Agent
        graph.add_edge("parallel_start", "credit_rating")
        graph.add_edge("parallel_start", "compliance_check")
        graph.add_edge("parallel_start", "fraud_detection")
        
        # 所有检查完成后进入等待节点
        graph.add_edge("credit_rating", "wait_for_checks")
        graph.add_edge("compliance_check", "wait_for_checks")
        graph.add_edge("fraud_detection", "wait_for_checks")
        
        # 等待节点判断是否所有检查完成
        graph.add_conditional_edges(
            "wait_for_checks",
            self._check_parallel_result,
            {
                "decision_making": "decision_making",
                "wait_for_checks": "wait_for_checks"
            }
        )
        
        # 决策节点路由
        graph.add_conditional_edges(
            "decision_making",
            self._check_decision_result,
            {
                "approved": "loan_structuring",
                "human_review": "human_review",
                "rejected": END
            }
        )

        # 人工审核后路由
        graph.add_conditional_edges(
            "human_review",
            self._check_human_approve,
            {
                "approved": "loan_structuring",
                "rejected": END,
                "human_review": "human_review"  # 异常情况 → 继续等待
            }
        )
        graph.add_edge("loan_structuring", "contract_generation")
        graph.add_edge("contract_generation", "regulatory_review")
        graph.add_conditional_edges(
            "regulatory_review",
            self._check_regulatory_review_result,
            {
                "approved": "contract_completed",
                "rejected": "contract_modify",
                "fail": END
            }
        )
        graph.add_conditional_edges(
            "contract_modify",
            self._check_contract_modify_result,
            {
                "success": "regulatory_review",
                "fail": END
            }
        )
        graph.add_edge("contract_completed", END)
                
        # 编译图
        auto_finance_app = graph.compile(checkpointer=self.checkpointer)
        # 生成流程图
        graph_png = auto_finance_app.get_graph().draw_mermaid_png()
        with open("Auto_Finance_POC.png", "wb") as f:
            f.write(graph_png)

        return auto_finance_app

    def _check_parallel_result(self, state: LoanApplicationState) -> str:
        """检查并行任务是否完成"""
        # 检查是否所有必要结果都已生成
        required_results = [
            state.get("credit_rating_result"),
            state.get("fraud_detection_result"),
            state.get("compliance_result")
        ]
        
        # 检查是否有未完成的结果
        if all(result is not None for result in required_results):
            return "decision_making"
            
        # 检查是否有结果生成失败（超过一定时间或次数）
        check_attempts = state.get("check_attempts", 0) + 1
        state["check_attempts"] = check_attempts
        
        # 如果尝试次数过多，强制进入决策阶段
        if check_attempts > 10:
            # 为缺失的结果设置默认值
            if state.get("credit_rating_result") is None:
                state["credit_rating_result"] = {"score": 0, "error": "信用评级未完成"}
            if state.get("fraud_detection_result") is None:
                state["fraud_detection_result"] = {"pass": False, "error": "反欺诈检测未完成"}
            if state.get("compliance_result") is None:
                state["compliance_result"] = {"pass": False, "error": "合规检查未完成"}
            return "decision_making"
            
        return "wait_for_checks"

    def _check_decision_result(self, state: LoanApplicationState) -> str:
        """检查决策状态"""
        if state.get("decision_result") == "approved":
            # 直接批准
            return "approved"
        elif state.get("decision_result") == "human_review":
            # 需要人工审核
            return "human_review"
        else:
            # 拒绝申请
            return "rejected"
        
    def _check_human_approve(self, state: LoanApplicationState) -> str:
        """检查人工审核状态"""
        return state.get("human_approval_status", "human_review")

    def parallel_start(self, state: LoanApplicationState) -> dict:
        return {"status": "并行处理开始"}

    def wait_for_checks(self, state: LoanApplicationState) -> dict:
        if self.check_all_completed(state):
            return {"status": "所有检查已完成，准备进入决策阶段"}
        return {"status": "等待所有检查完成"}

    def check_all_completed(self, state: LoanApplicationState) -> bool:
        return all([
            state.get("credit_rating_result") is not None,
            state.get("fraud_detection_result") is not None,
            state.get("compliance_result") is not None
        ])

    def check_dialogue_loop(self, state: LoanApplicationState) -> dict:
        current_count = state.get("dialogue_loop_count", 0)
        new_count = current_count + 1
        
        if new_count >= self.max_dialogue_loops:
            return {
                "dialogue_loop_count": new_count,
                "status": f"对话循环已达到最大次数({self.max_dialogue_loops})，准备进入合同结构化阶段"
            }
            
        return {
            "dialogue_loop_count": new_count,
            "status": f"对话循环计数更新为 {new_count}"
        }

    def human_review_process(self, state: LoanApplicationState, config: RunnableConfig) -> dict:
        """人工审核贷款申请"""
        print("进入人工审核阶段:::")
        # 从状态中获取当前流程的thread_id
        current_thread_id = config.get("configurable", {}).get("thread_id")
        if not current_thread_id:
            raise ValueError("无法获取当前流程的thread_id，无法触发中断")
        print(f"显式传入中断的thread_id: {current_thread_id}")

        # 构造中断信息
        interrupt_info = {
            "application_id": state["raw_data"]["application_id"],
            "data_collection_status": state["data_collection_status"],
            "credit_rating_result": state["credit_rating_result"],
            "fraud_detection_status": state["fraud_detection_status"],
            "fraud_detection_result": state["fraud_detection_result"],
            "compliance_check_status": state["compliance_check_status"],
            "compliance_result": state["compliance_result"],
            "decision_result": state["decision_result"],
            "thread_id": current_thread_id
        }

        # 触发中断，暂停工作流，触发中断时显式保存检查点
        response = interrupt(interrupt_info)
        print(f"respone::: {response}")
        human_status = response["human_approval_status"]
        human_feedback = response["feedback"]

        if human_status  == "approved":
            return {
                "human_approval_status": "approved",
                "human_feedback": human_feedback
            }
        elif human_status == "rejected":
            return {
                "human_approval_status": "rejected",
                "human_feedback": human_feedback
            }
        else:
            raise ValueError(f"未知的审核响应类型: {human_status}")
        
    def contract_completed(self, state: LoanApplicationState) -> dict:
        """贷款合同生成完了后，数据库保存更新：：："""
        print("进入款合同生成完了，数据库保存更新阶段:::")
        
        # 返回需要更新的数据
        return {
            "loan_structuring_status": state["loan_structuring_status"],
            "loan_structuring_result": state["loan_structuring_result"],
            "contract_generation_status": state["contract_generation_status"],
            "contract_generation_result": state["contract_generation_result"],
            "contract_review_status": state["contract_review_status"],
            "contract_review_result": state["contract_review_result"],
            "contract_modify_status": state["contract_modify_status"],
            "contract_modify_result": state["contract_modify_result"],
            "contract_file_name":state["contract_file_metadata"]["file_name"],
            "contract_file_type":state["contract_file_metadata"]["file_type"],
            "contract_binary_data":state["contract_file_metadata"]["binary_data"],
            "status": "contract_completed"
        }

    def get_graph(self):
        return self.graph

    def run(self, input_data: dict, thread_id: str = "default_thread"):
        config = {
            "configurable": {
                "thread_id": thread_id,
                "recursion_limit": 50
            }
        }
        return self.graph.invoke(input_data, config)

    def _check_regulatory_review_result(self, state: LoanApplicationState) -> str:
            """检查regulatory_review状态"""
            if state.get("contract_review_status") == "Approved":
                # 合同审核通过
                return "approved"
            elif state.get("contract_review_status") == "Rejected":
                # 需要修改合同
                return "rejected"
            elif state.get("contract_review_status") == "Fail":
                # 合同审核失败
                return "fail"
    def _check_contract_modify_result(self, state: LoanApplicationState) -> str:
        """检查contract_modify状态"""
        if state.get("contract_modify_status") == "Success":
            # 合同修改成功
            return "success"
        elif state.get("contract_modify_status") == "Fail":
            # 合同修改失败
            return "fail"