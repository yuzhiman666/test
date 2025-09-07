import sys
import os
import redis
from redis import Redis
from utils.path_utils import PROJECT_ROOT
# 将项目根目录添加到 Python 搜索路径
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
# 获取当前脚本所在目录的父目录（即项目根目录）
#project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 将项目根目录添加到 Python 搜索路径
#sys.path.append(project_root)
from langgraph.graph import StateGraph, START, END
from langchain_core.language_models import BaseChatModel
from agents.state import LoanApplicationState
from agents.data_collect_agent import DataCollectAgent
from agents.data_review_agents import (
    CreditRatingAgent, ComplianceAgent, FraudDetectionAgent
)
from agents.decision_making_agent import DecisionMakingAgent
from agents.loan_structuring_agents import LoanStructuringAgent
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.redis import RedisSaver
from redisvl.index import SearchIndex

class LoanWorkflow:

    def __init__(self, llm: BaseChatModel):
        # 初始化Agent
        # 设置Redis环境变量，解决REDIS_URL未设置的问题
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
        self.data_collect_agent = DataCollectAgent()
        self.credit_agent = CreditRatingAgent()
        self.compliance_agent = ComplianceAgent()
        self.fraud_agent = FraudDetectionAgent(llm)
        self.decision_agent = DecisionMakingAgent(llm)
        self.structuring_agent = LoanStructuringAgent(llm)
        self.redis_client = Redis.from_url(os.environ["REDIS_URL"])
        # 初始化Redis检查点存储
        redis_context = RedisSaver.from_conn_string(os.environ["REDIS_URL"])
        self.redis_saver = redis_context.__enter__()

        # 检查并创建checkpoints索引
        self._create_index_if_not_exists(
            self.redis_saver.checkpoints_index.name,
            self.redis_saver.checkpoints_index.schema
        )
        
        # 检查并创建checkpoints_blobs索引
        self._create_index_if_not_exists(
            self.redis_saver.checkpoint_blobs_index.name,
            self.redis_saver.checkpoint_blobs_index.schema
        )
        
        # 检查并创建checkpoint_writes索引
        self._create_index_if_not_exists(
            self.redis_saver.checkpoint_writes_index.name,
            self.redis_saver.checkpoint_writes_index.schema
        )

        # 设置检查点
        self.checkpointer = self.redis_saver
        # 配置最大循环次数
        self.max_dialogue_loops = 5
        # 构建工作流图
        self.graph = self._build_graph()
    
    def _create_index_if_not_exists(self, index_name, schema):
        """通用方法：检查并创建索引（如果不存在）"""
        try:
            # 尝试获取索引信息，验证是否存在
            self.redis_client.ft(index_name).info()
            print(f"Redis索引 '{index_name}' 已存在，无需创建")
        except redis.exceptions.ResponseError as e:
            if "Unknown index name" in str(e):
                try:
                    # 创建索引并绑定客户端
                    index = SearchIndex.from_dict(
                        schema,
                        client=self.redis_client  # 直接传入客户端
                    )
                    index.create(overwrite=False)
                    print(f"Redis索引 '{index_name}' 创建成功")
                except Exception as create_err:
                    print(f"创建Redis索引 '{index_name}' 失败: {str(create_err)}")
                    raise
            else:
                print(f"Redis错误: {str(e)}")
                raise

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(LoanApplicationState)
        
        # 添加节点
        graph.add_node("data_collect", self.data_collect_agent.process)  # 用户数据收集与验证节点
        graph.add_node("parallel_start", self.parallel_start)
        graph.add_node("credit_rating", self.credit_agent.process)
        graph.add_node("fraud_detection", self.fraud_agent.process)  # 新增反欺诈节点
        graph.add_node("compliance_check", self.compliance_agent.process)
        graph.add_node("wait_for_checks", self.wait_for_checks)
        graph.add_node("decision_making", self.decision_agent.process)
        graph.add_node("human_review", self.human_review_process)
        graph.add_node("loan_structuring", self.structuring_agent.loan_structuring)
        graph.add_node("contract_generation", self.structuring_agent.contract_generation)
        graph.add_node("regulatory_review", self.structuring_agent.regulatory_review)
        graph.add_node("contract_human_review", self.contract_human_review_process)
        
        # 定义流程
        graph.add_edge(START, "data_collect")
        
        # 数据收集完成后进入并行处理
        graph.add_conditional_edges(
            "data_collect",
            lambda s: s["data_collection_status"],
            {
                "ok": "parallel_start",
                "incomplete": END,
                "invalid": END
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
        graph.add_edge("decision_making", "human_review")

        # 人工审核后路由
        graph.add_conditional_edges(
            "human_review",
            self._check_human_approve,
            {
                "approved": "loan_structuring",
                "rejected": END
            }
        )
        graph.add_edge("loan_structuring", "contract_generation")
        graph.add_edge("contract_generation", "regulatory_review")
        graph.add_edge("regulatory_review", "contract_human_review")
        graph.add_edge("contract_human_review", END)
                
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
        
        # 如果尝试次数过多，强制进入决策阶段（带错误信息）
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

    def _check_human_approve(self, state: LoanApplicationState) -> str:
        """检查人工审核状态"""
        if state.get("human_approval_status") == "approved":
            return "approved"
        elif state.get("human_approval_status") == "rejected":
            return "rejected"
        else:
            return "human_review"

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

    def human_review_process(self, state: LoanApplicationState) -> dict:
        # 提取审核信息
        review_info = {
            "credit_rating": state.get("credit_rating_result", {}).get("rating", "未提供"),
            "fraud_detection": "通过" if state.get("fraud_detection_result", {}).get("pass", False) else "未通过",
            "compliance": "合规" if state.get("compliance_result", {}).get("compliant", False) else "不合规"
        }
        
        response = interrupt(
            f"需要人工审核贷款申请。请审核以下内容并决定是否批准：\n{review_info}"
        )
        
        if response["type"] == "accept":
            return {
                "human_approval_status": "approved",
                "human_feedback": response.get("feedback", "自动批准")
            }
        elif response["type"] == "reject":
            return {
                "human_approval_status": "rejected",
                "human_feedback": response.get("feedback", "自动拒绝")
            }
        elif response["type"] == "edit":
            return {
                "human_approval_status": response.get("status", "rejected"),
                "human_feedback": response.get("feedback", "修改后处理"),
                **response.get("args", {})
            }
        else:
            raise ValueError(f"未知的审核响应类型: {response['type']}")
        

    def contract_human_review_process(self, state: LoanApplicationState) -> dict:
        # 提取审核信息
        review_info = {
            "credit_rating": state.get("credit_rating_result", {}).get("rating", "未提供"),
            "fraud_detection": "通过" if state.get("fraud_detection_result", {}).get("pass", False) else "未通过",
            "compliance": "合规" if state.get("compliance_result", {}).get("compliant", False) else "不合规"
        }
        
        response = interrupt(
            f"需要人工审核贷款合同。请审核以下内容并决定是否批准：\n{review_info}"
        )
        
        if response["type"] == "accept":
            return {
                "human_approval_status": "approved",
                "human_feedback": response.get("feedback", "自动批准")
            }
        elif response["type"] == "reject":
            return {
                "human_approval_status": "rejected",
                "human_feedback": response.get("feedback", "自动拒绝")
            }
        elif response["type"] == "edit":
            return {
                "human_approval_status": response.get("status", "rejected"),
                "human_feedback": response.get("feedback", "修改后处理"),
                **response.get("args", {})
            }
        else:
            raise ValueError(f"未知的审核响应类型: {response['type']}")

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
