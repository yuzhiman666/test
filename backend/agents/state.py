from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from bson import Binary, Decimal128
from pydantic_core import core_schema

# 为 bson.Binary 类型添加 Pydantic 支持
def binary_schema(handler) -> core_schema.CoreSchema:
    return core_schema.no_info_wrap_validator_function(
        validate_binary,
        core_schema.bytes_schema(),
    )

def validate_binary(v: Binary, _: core_schema.ValidatorFunctionWrapHandler) -> bytes:
    return v.read() if isinstance(v, Binary) else v


# 为 Decimal128 类型添加 Pydantic 支持
def decimal128_schema(handler) -> core_schema.CoreSchema:
    return core_schema.no_info_wrap_validator_function(
        validate_decimal128,
        core_schema.float_schema(),
    )

def validate_decimal128(v: Decimal128, _: core_schema.ValidatorFunctionWrapHandler) -> float:
    return float(v.to_decimal()) if isinstance(v, Decimal128) else v


class LoanApplicationState(TypedDict):

    """全局状态定义，管理全流程数据（无message字段）"""
    # 基础信息字段
    user_id: str
    raw_data: Dict
    collected_data: Optional[Dict]
    data_collection_status: Optional[str]  # 状态：completed/failed
    missing_fields: List[str]
    status: Optional[str]  # 整体流程状态：processing/success/failed
    
    # 身份证信息
    fullName: Optional[str]
    idNumber: Optional[str]
    
    # 征信/收入/工作信息
    creditInfo: Optional[bytes]  # 征信报告二进制
    salary: Optional[float]       # 工资流水金额（float）
    companyName: Optional[str]    # 公司名称
    onboardDate: Optional[datetime]  # 入职时间（datetime）
    position: Optional[str]       # 职位
    monthlyIncome: Optional[float]  # 月薪（float）
    
    # 信用评级
    credit_rating_result: Optional[Dict]

    # 反欺诈
    fraud_detection_status: Optional[str] # 决策结果 approved/human_review/rejected
    fraud_detection_result: Optional[Dict]

    # 合规检查
    compliance_check_status: Optional[str] # 决策结果 approved/rejected
    compliance_result: Optional[Dict]

    # 决策结果
    decision_result: Optional[str] # 决策结果 approved/human_review/rejected

    # human接入结果
    thread_id: Optional[str] = None  # 流程唯一标识
    human_approval_status: Optional[str] = None # 决策结果 approved/rejected
    human_feedback: Optional[str]
    human_contract_approval_status: Optional[str] = None # 决策结果 approved/rejected
    human_contract_feedback: Optional[str]
    
    # 其他流程字段
    check_attempts: int = 0  # 并行检查尝试次数
    dialogue_loop_count: int = 0  # 对话循环计数
    contract_draft: str  # loan_structuring_agents 会设置，合同文本内容
    # 合同需要的结构化数据生成agent 执行结果
    loan_structuring_status: Optional[str] = None # 执行状态 Success/Fail
    loan_structuring_result: Optional[str] = None # 执行结果 Contract structuring completed/aborted
    loan_structuring_data: Optional[Dict] = None # 合同需要的结构化数据
    # 合同生成agent 执行结果
    contract_generation_status: Optional[str] = None # 执行状态 Success/Fail
    contract_generation_result: Optional[str] = None # 执行结果 Contract structuringn completed/aborted
    contract_file_path: Optional[str] = None # 生成的合同文件的绝对路径
    contract_file_metadata: Optional[Dict] = None # 合同文件的信息：binary_data，file_name，file_type，file_extension，file_size
    contract_file_name: Optional[str] = None # file_name
    contract_file_type: Optional[str] = None # file_type
    contract_binary_data: Optional[str] = None # binary_data的base64编码字符串
    # 合同生成agent 执行结果
    contract_review_status: Optional[str] = None # 合同检查结果是否通过 (Approved/Rejected/Fail，Fail是发生Error)
    contract_review_result: Optional[str] = None # 执行结果 Contract generation completed/aborted
    contract_review_result_details: Optional[Dict] = None # 执行结果详细：overall_result，detail_results，summary，revisions。参考loan_structuring_agents.py的class ContractCheckFinalResult
    # 合同修改agent 执行结果
    contract_modify_status: Optional[str] = None # 执行状态 Success/Fail
    contract_modify_result: Optional[str] = None # 执行结果 Contract modify completed/aborted


# 注册自定义类型的 Pydantic 验证逻辑
Binary.__get_pydantic_core_schema__ = lambda cls, handler: binary_schema(handler)
Decimal128.__get_pydantic_core_schema__ = lambda cls, handler: decimal128_schema(handler)