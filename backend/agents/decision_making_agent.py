from agents.state import LoanApplicationState
from langchain_core.language_models import BaseChatModel
from typing import Dict

class DecisionMakingAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def process(self, state: LoanApplicationState) -> Dict:
        """根据各检查结果做出决策"""
        if not all([
            # 检查信用评级结果：必须存在、是字典且非空
            state.get("credit_rating_result") is not None and 
            isinstance(state["credit_rating_result"], dict) and 
            state["credit_rating_result"],
            
            # 检查反欺诈状态：必须存在、是字符串且非空（排除纯空白）
            state.get("fraud_detection_status") is not None and 
            isinstance(state["fraud_detection_status"], str) and 
            state["fraud_detection_status"].strip(),
            
            # 检查合规检查状态：必须存在、是字符串且非空（排除纯空白）
            state.get("compliance_check_status") is not None and 
            isinstance(state["compliance_check_status"], str) and 
            state["compliance_check_status"].strip()
        ]):
            return {
                "status": "决策失败：缺少必要的检查结果（信用评级、反欺诈状态、合规检查状态必须全部存在且有效）",
                "decision_result": "rejected"
            }
        credit_rating_result = state.get("credit_rating_result")
        credit_score = credit_rating_result.get("score", 0) if credit_rating_result is not None else 0
        print(f"credit_score::: {credit_score}")

        fraud_pass = state.get("fraud_detection_status") or "UNKNOWN"
        print(f"fraud_pass::: {fraud_pass}")

        compliance_pass = state.get("compliance_check_status") or "UNKNOWN"
        print(f"compliance_pass::: {compliance_pass}")

        # 决策逻辑
        # 初始化为拒绝状态
        decision = "rejected"
        decision1 = "human_review" # for test
        # 首先检查合规性，不合规直接拒绝
        if compliance_pass == "approved":
            # 合规的情况下再检查其他条件
            if fraud_pass == "approved":
                # 欺诈检查通过时，根据信用分决定
                if credit_score >= 90:
                    decision = "approved"  # 高信用分直接批准
                elif credit_score >= 60:
                    decision = "human_review"  # 中等信用分需要人工审核
            elif fraud_pass == "human_review" and credit_score >= 60:
                # 欺诈检查需要人工审核且信用分达标时
                decision = "human_review"
        
        return {
            "status": f"决策完成：{decision1}",
            "decision_result": decision1  # 确保总是返回明确的决策结果
        }
