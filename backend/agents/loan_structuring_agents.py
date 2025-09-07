# ------------------------------
# 3. 合同检查以及共通引用
# ------------------------------
import os
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_redis.vectorstores import RedisVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
# from langchain.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
# from dashscope import TextEmbedding
from langchain.schema import Document
from dotenv import load_dotenv
from pathlib import Path
# 获取上级目录的路径并添加到系统路径
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.load_key import load_key

# ------------------------------
# 2. 生成合同使用 
# ------------------------------
import math
import num2words
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from typing import List, Dict
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from bson import Binary

# ------------------------------
# 3. 合同合规检查使用 
# ------------------------------
from langchain_core.language_models import BaseChatModel

# ------------------------------
# 4. 合同模板修改使用
# ------------------------------
import shutil
from datetime import datetime
from langchain.schema import AIMessage  # 引入AIMessage类型

# ------------------------------
# 1. 合同所需数据准备时使用
# ------------------------------
import numpy as np
from datetime import timedelta

# ------------------------------
# 引入项目文件
# ------------------------------
from agents.state import LoanApplicationState

# ------------------------------
# 全局变量 各机能共用
# ------------------------------
# 加载环境变量
load_dotenv()
# 加载API密钥并初始化LLM
DASHSCOPE_API_KEY = load_key("DASHSCOPE_API_KEY")
llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=DASHSCOPE_API_KEY,
    model="qwen-plus-latest",
)

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 合同检查基础条款目录
basic_clauses_file_path = os.path.join(
        os.path.dirname(current_dir),  # 上级目录
        "init_data", 
        "loan_contract_review_criteria", 
        "basic_clauses.json"
)

# 合同检查特殊场景条款目录
advanced_clauses_file_path = os.path.join(
        os.path.dirname(current_dir),  # 上级目录
        "init_data", 
        "loan_contract_review_criteria", 
        "advanced_scenarios.json"
)

# 合同检查特殊场景条款目录
advanced_clauses_file_path = os.path.join(
        os.path.dirname(current_dir),  # 上级目录
        "init_data", 
        "loan_contract_review_criteria", 
        "advanced_scenarios.json"
)

# 合同模板的目录。先获取上级目录，再拼接 init_data/loan_template 和文件名
# 根目录/init_data/loan_template
contract_template_dir = os.path.join(
    os.path.dirname(current_dir),  # 上级目录
    "init_data", 
    "loan_template"
)
contract_template_name = "loan_contract_template.jinja2"
contract_template_path = os.path.join(
    os.path.dirname(current_dir),  # 上级目录
    "init_data", 
    "loan_template", 
    contract_template_name
)
# 合同模板备份的目录。
contract_template_backup_dir = os.path.join(
    os.path.dirname(current_dir),  # 上级目录
    "init_data", 
    "loan_template_backup"
)

# 生成的合同文件PDF的目录。
# 根目录/init_data/loan_contract
contract_pdf_path_dir = os.path.join(
    os.path.dirname(current_dir),  # 上级目录
    "init_data", 
    "loan_contract"
)


# ------------------------------
# 数据模型定义
# ------------------------------
# 2.合同检查时使用 Start
# 汉语版description。会做成提示词。
# class ContractCheckResult(BaseModel):
#     """合同单个合规检查项的结果"""
#     check_id: str = Field(description="检查项的唯一ID，需与LEGAL REQUIREMENTS中对应条款的ID一致，比如：BASIC-01")
#     check_title: str =  Field(description="检查项的概要标题，需与LEGAL REQUIREMENTS中对应条款的Title一致，比如：Total & Monthly Payment")
#     compliant: bool = Field(description="是否合规 (True/False)")
#     check_process_chinese: str = Field(description="中文的检查过程说明")
#     check_process_english: str = Field(description="英文的检查过程说明")
#     english_revision: Optional[str] = Field(None, description="英文的精确修改建议；合规则为None")
#     location: Optional[str] = Field(None, description="合同中问题位置的描述")

# class ContractComplianceCheckResponse(BaseModel):
#     """合同合规检查的整体结果"""
#     overall_compliant: bool = Field(description="合同整体是否合规 (True/False)")
#     results: List[ContractCheckResult] = Field(description="所有检查项的结果列表")
#     summary: str = Field(description="英文的检查结果摘要")

# 英语版description。会做成提示词。
class ContractCheckResult(BaseModel):
    """Result of a single compliance check item for the contract"""
    check_id: str = Field(description="Unique ID of the check item, which must match the ID of the corresponding clause in LEGAL REQUIREMENTS (e.g., BASIC-01, CHECK-01)")
    check_title: str =  Field(description="Summary title of the check item, which must match the Title of the corresponding clause in LEGAL REQUIREMENTS (e.g., Total & Monthly Payment)")
    compliant: bool = Field(description="Whether it is compliant (True/False)")
    check_process_chinese: str = Field(description="Chinese description of the check process")
    check_process_english: str = Field(description="English description of the check process")
    english_revision: Optional[str] = Field(None, description="Precise English revision suggestions; None if compliant")
    location: Optional[str] = Field(None, description="Description of the location of the issue in the contract")

class ContractComplianceCheckResponse(BaseModel):
    """Overall result of the contract compliance check"""
    overall_compliant: bool = Field(description="Whether the contract is overall compliant (True/False)")
    results: List[ContractCheckResult] = Field(description="List of results for all check items")
    summary: str = Field(description="English summary of the check results")
#-------------
class ContractBusinessContext(BaseModel):
    """合同检查用。定义外部业务信息的数据模型，为判断合同是否为特殊场景服务。True的话触发特殊场景"""
    is_foreign_resident: bool = Field(description="贷款申请人是否为外籍居民 (True/False)")  # 是否为外籍居民。
    is_vehicle_old: bool = Field(description="车辆是否为二手车 (True/False)") # 车辆是不是二手车
    is_vehicle_registration_cross_border: bool = Field(description="车辆注册国家是否为外国 (True/False)") # 车辆注册国家是否为外国
    is_early_repayment: bool = Field(description="是否提前还款 (True/False)") # 是否提前还款

class RevisionItem(BaseModel):
    """单条英文修改建议的结构化数据"""
    check_id: str = Field(description="对应的检查项ID，如：BASIC-01, CHECK-01")
    check_title: str = Field(description="对应的检查项标题，如：Total & Monthly Payment")
    compliant_result: str = Field(description="是否通过了合规检查（PASS/FAIL）")
    english_explanation: str = Field(description="英文的检查过程说明（为什么需要修改）")
    revision_content: str = Field(description="英文的精确修改建议内容")

class ContractCheckFinalResult(BaseModel):
    """定义合同检查的最终返回结果"""
    overall_result: str = Field(description="合同检查结果是否通过 (Approved/Rejected)")
    detail_results: str = Field(description="所有的检查说明按顺序合并，用换行符分割") 
    summary: str = Field(description="英文的检查结果摘要")
    revisions: Optional[List[RevisionItem]] = Field(
        None, 
        description="所有的英文修改建议，每条建议为一个字典；如果合同通过则为None"
    )

# 2.合同检查时使用 End


# 3.合同修改时使用。其实没有用到。先留着。
class ModifyLogItem(BaseModel):
    """定义单条英文修内容的结构化数据"""
    issue_title: str = Field(description="Title of the modification item, MUST match the 'Issue Title' in REVISION REQUIREMENTS. Example: 1 (BASIC-03: 14-Day Cancellation)")
    problem_details: str = Field(description="Detailed explanation of the non-compliant issue, MUST match the 'Problem Details' in REVISION REQUIREMENTS. Example: Article 9a grants a 4-day withdrawal period, violating German law's mandatory 14-day requirement for consumer credit contracts.")
    required_changes: str = Field(description="Detailed modification requirements, MUST match the 'Required Changes' in REVISION REQUIREMENTS. Example: Revise Article 9a.2 to state: 'The withdrawal period expires 14 days after Party B signs this contract.'")
    modify_log: str = Field(description="Specific changes made to the ORIGINAL TEMPLATE (MUST be in English, no Chinese). Example: Changed '4 days' to '14 days' in Article 9a; adjusted no other references.")

class ContractModifyResponse(BaseModel):
    """定义合同修改的最终返回结果"""
    overall_result: str = Field(description="Whether all modifications are completed. Only two options: 'Done' (all requirements addressed) or 'UnDone' (partial/failed).")
    summary: str = Field(description="English summary of all modifications (1-2 concise sentences, no Chinese). Example: Revised 2 clauses to comply with German law: adjusted withdrawal period and clarified interest rate.")
    modified_template_content: str = Field(description="Full content of the modified contract template. MUST preserve original HTML structure, CSS, and Jinja2 variables; no content omission.")
    modify_logs: List[ModifyLogItem] = Field(description="List of all modifications. Each item MUST correspond to one requirement in REVISION REQUIREMENTS (one-to-one match).")

class ContractModifierResponse(BaseModel):
    """定义合同模板修改的最终返回结果"""
    contract_check_status: str = Field(description="是否所有修改都完成 (Done/UnDone)")
    summary: str = Field(description="英文的检查结果摘要")
    modified_template_content: str = Field(description="修改后的合同模板内容。MUST preserve original HTML structure, CSS, and Jinja2 variables; no content omission.")
    modify_logs: List[ModifyLogItem] = Field(description="所有的修改建议，每条建议为一个字典；如果合同通过则为None")

# ------------------------------
# 方法类定义
# ------------------------------
# 1 合同所需数据准备用
class ContractData:
    """合同数据类，支持分步构建和数据验证"""
    
    def __init__(self):
        # 初始化所有字段为None或空结构，确保结构完整性
        self.contract_number: Optional[str] = None
        self.signing_date: Optional[str] = None
        self.currency: Optional[str] = None
        
        # 嵌套结构初始化为空字典
        self.lender: Dict[str, Optional[str]] = {
            "name": None,
            "reg_number": None,
            "address": None,
            "phone": None,
            "email": None,
            "authorized_rep": None,
            "rep_sign_date": None
        }
        
        self.borrower: Dict[str, Optional[str]] = {
            "full_name": None,
            "id_number": None,
            "address": None,
            "phone": None,
            "iban": None,
            "sign_date": None
        }
        
        self.loan_amount: Optional[float] = None
        self.annual_interest_rate: Optional[float] = None
        self.apr: Optional[float] = None
        self.loan_term_months: Optional[int] = None
        self.disbursement_date: Optional[str] = None
        
        self.german_resident_personal_use: Optional[bool] = None
        
        self.vehicle: Dict[str, Optional[str]] = {
            "make": None,
            "model": None,
            "chassis_number": None
        }
        
        self.dealer: Dict[str, Optional[str]] = {
            "name": None,
            "iban": None
        }
    
    def set_basic_info(self, contract_number: str, signing_date: str, currency: str = "EUR"):
        """设置基本合同信息"""
        self.contract_number = contract_number
        self.signing_date = signing_date
        self.currency = currency
        return self  # 支持链式调用
    
    def set_lender_info(self, **kwargs):
        """设置贷款方信息，支持部分字段更新"""
        for key, value in kwargs.items():
            if key in self.lender:
                self.lender[key] = value
        return self
    
    def set_borrower_info(self,** kwargs):
        """设置借款方信息，支持部分字段更新"""
        for key, value in kwargs.items():
            if key in self.borrower:
                self.borrower[key] = value
        return self
    
    def set_loan_terms(self, loan_amount: float, annual_interest_rate: float, 
                       loan_term_months: int, disbursement_date: str, apr: Optional[float] = None):
        """设置贷款核心条款"""
        self.loan_amount = loan_amount
        self.annual_interest_rate = annual_interest_rate
        self.loan_term_months = loan_term_months
        self.disbursement_date = disbursement_date
        if apr:
            self.apr = apr
        return self
    
    def set_vehicle_info(self, **kwargs):
        """设置车辆信息"""
        for key, value in kwargs.items():
            if key in self.vehicle:
                self.vehicle[key] = value
        return self
    
    def set_dealer_info(self,** kwargs):
        """设置经销商信息"""
        for key, value in kwargs.items():
            if key in self.dealer:
                self.dealer[key] = value
        return self
    
    def set_residency_status(self, status: bool):
        """设置德国居民及个人使用状态"""
        self.german_resident_personal_use = status
        return self
    
    def validate(self) -> bool:
        """验证是否所有必填字段都已填写"""
        required_fields = [
            self.contract_number, self.signing_date, self.currency,
            self.lender["name"], self.lender["address"],
            self.borrower["full_name"], self.borrower["iban"],
            self.loan_amount, self.annual_interest_rate,
            self.loan_term_months, self.disbursement_date,
            self.vehicle["make"], self.vehicle["chassis_number"]
        ]
        
        # 检查是否有必填字段为空
        has_empty = any(field is None for field in required_fields)
        if has_empty:
            missing = [name for name, field in zip([
                "contract_number", "signing_date", "currency",
                "lender.name", "lender.address",
                "borrower.full_name", "borrower.iban",
                "loan_amount", "annual_interest_rate",
                "loan_term_months", "disbursement_date",
                "vehicle.make", "vehicle.chassis_number"
            ], required_fields) if field is None]
            print(f"验证失败：缺少必填字段 - {', '.join(missing)}")
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于后续操作或存储"""
        return {
            "contract_number": self.contract_number,
            "signing_date": self.signing_date,
            "currency": self.currency,
            "lender": self.lender.copy(),
            "borrower": self.borrower.copy(),
            "loan_amount": self.loan_amount,
            "annual_interest_rate": self.annual_interest_rate,
            "apr": self.apr,
            "loan_term_months": self.loan_term_months,
            "disbursement_date": self.disbursement_date,
            "german_resident_personal_use": self.german_resident_personal_use,
            "vehicle": self.vehicle.copy(),
            "dealer": self.dealer.copy()
        }

# 2 生成合同用
# NumberConverter是生成合同用的。
class NumberConverter:
    @staticmethod
    def convert_currency(amount: float, currency: str = "EUR") -> str:
        """将金额转换为英文文字表述（带货币单位）"""
        currency_map = {
            "EUR": "Euro",
            "USD": "Dollar",
            "GBP": "Pound",
            "JPY": "Yen"  # 单复数同形
        }

        currency_decimal_map = {
            "EUR": "Cent",
            "USD": "Cent",
            "GBP": "Pence",
            "JPY": "Sen"  # 单复数同形
        }
        
        currency_code = currency.upper()
        currency_name = currency_map.get(currency_code, currency)
        currency_decimal_name = currency_decimal_map.get(currency_code, currency)
        
        # 处理货币复数形式
        if currency_code in ["JPY"]:
            currency_plural = currency_name
        else:
            currency_plural = f"{currency_name}s" if abs(amount) != 1 else currency_name
        
        if currency_code in ["JPY"]:
            currency_decimal_plural = currency_decimal_name
        else:
            currency_decimal_plural = f"{currency_decimal_name}s" if abs(amount) != 1 else currency_decimal_name

        # 处理小数部分
        amount_rounded = round(amount, 2)
        integer_part = int(math.floor(amount_rounded))
        decimal_part = int(round((amount_rounded - integer_part) * 100))
        
        # 转换整数部分
        integer_words = num2words.num2words(integer_part, to='cardinal', lang='en')
        integer_words = integer_words.title().replace(' And ', ' and ')
        
        # 处理小数部分
        if decimal_part > 0:
            decimal_words = num2words.num2words(decimal_part, to='cardinal', lang='en').title()
            full_words = f"{integer_words} {currency_plural} and {decimal_words} {currency_decimal_plural} only"
        else:
            full_words = f"{integer_words} {currency_plural} only"
        
        return full_words
    
    @staticmethod
    def convert_percentage(percentage: float) -> str:
        """将百分比转换为英文文字表述"""
        percentage_str = f"{percentage:.10f}".rstrip('0').rstrip('.') if '.' in f"{percentage}" else f"{percentage}"
        
        if "." in percentage_str:
            integer_part, decimal_part = percentage_str.split(".", 1)
            integer_words = num2words.num2words(int(integer_part), lang='en').lower()
            decimal_words = " ".join([num2words.num2words(int(digit), lang='en').lower() for digit in decimal_part])
            return f"{integer_words} point {decimal_words} percent"
        
        return num2words.num2words(int(percentage_str), lang='en').lower() + " percent"
    
    @staticmethod
    def convert_number(number: int) -> str:
        """将整数转换为英文文字表述"""
        if not isinstance(number, int):
            raise TypeError("Input must be an integer")
        return num2words.num2words(number, lang='en').lower()
    
    # 2 生成合同用End

# ------------------------------
# 以下为核心逻辑代码
# ------------------------------

# ------------------------------
# 1. 合同所需数据准备，结构化 核心逻辑
# ------------------------------
class LoanStructuringAgent:
    """合同所需数据准备，结构化Agent"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

        # 合同数据类
        self.contract_data = ContractData()
    
    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """处理贷款申请，生成合同数据 外部调用入口"""
        try:
            # 生成合同数据 self.contract_data
            self._set_contract_data(state)

            contract_structed_data = self.contract_data.to_dict()

            return {
                "loan_structuring_data":contract_structed_data,
                "loan_structuring_status": "Success",
                "loan_structuring_result": "Loan structuring completed. All key parameters are generated.",
                "status": "success"
            }
        except Exception as e:
            print(f"合同所需数据准备过程出错: {str(e)}")
            return {
                "loan_structuring_data":"",
                "loan_structuring_status": "Fail",
                "loan_structuring_result": f"Loan structuring aborted: {str(e)}",
                "status": str(e)
            }

    
    def _set_contract_data(self, state: LoanApplicationState):
        """生成合同数据"""
        # 取得基本数据
        # 取得今天的日期，DD/MM/YYYY 15/09/2025 string
        today_ddmmyyyy = self._get_today_ddmmyyyy()

        #-------------------------------------

        # 1. 设置基本信息（从表单数据提取）    
        application_id = state.get("raw_data", {}).get("application_id","APPL_00000000")
        # 确保申请ID是字符串类型
        if not isinstance(application_id, str):
            application_id = str(application_id)
        # 处理申请ID：如果有下划线，取后半部分；否则取完整ID
        if "_" in application_id:
            # 分割后取最后一部分（处理多个下划线的情况）
            id_suffix = application_id.split("_")[-1]
        else:
            id_suffix = application_id

        self.contract_data.set_basic_info(
            contract_number = f"APX-FIN-2025-{id_suffix}",
            signing_date = today_ddmmyyyy,
            currency = "EUR"
        )
        
        # 2. 设置借款方信息（从表单数据提取）
        self.contract_data.set_borrower_info(
            full_name = state.get("raw_data", {}).get("personal_info", {}).get("fullName", "Max Schmidt"),
            id_number = state.get("idNumber", "DE1234567890"),
            address = state.get("raw_data", {}).get("personal_info", {}).get("address","Musterstraße 15, 76137 Karlsruhe, Germany"),
            phone = state.get("raw_data", {}).get("personal_info", {}).get("phoneNumber", "+49 176 5432 1098"),
            iban = state.get("raw_data", {}).get("personal_info", {}).get("accountNumber", "DE89 3704 0044 0532 0130 00"),
        )
        
        # 3. 设置贷款条款（从系统数据提取）
        loan_amount_cyn = state.get("raw_data", {}).get("loan_details", {}).get("loanAmount", 35000.00)
        loan_amount = self._cny_to_eur(loan_amount_cyn)
        annual_interest_rate = state.get("raw_data", {}).get("loan_details", {}).get("interestRate", 4.25)
        loan_term_months = state.get("raw_data", {}).get("loan_details", {}).get("loanTerm", 60)
        # 有效年利率（Annual Percentage Rate)
        apr = self._calculate_apr_from_interest(
            loan_amount = loan_amount,
            annual_interest_rate = annual_interest_rate,
            loan_term_months = loan_term_months,
            fees = 0
        )
        self.contract_data.set_loan_terms(
            loan_amount = loan_amount,
            annual_interest_rate = annual_interest_rate,
            loan_term_months = loan_term_months,
            disbursement_date = today_ddmmyyyy,
            apr = apr
        )
        
        # 4. 设置车辆信息（从系统数据提取）
        self.contract_data.set_vehicle_info(
            make = state.get("raw_data", {}).get("car_selection", {}).get("carBrand", "Apex"),
            model = state.get("raw_data", {}).get("car_selection", {}).get("carModel", "Nova X"),
            chassis_number = "WBA123456789012345",
        )
        
        # 5. 设置贷款方信息（从邮件提取）
        self.contract_data.set_lender_info(
            name = "Apex Auto Finance GmbH",
            reg_number = "HRB 123456 Karlsruhe",
            address = "Industriestraße 38, 76135 Karlsruhe, Germany",
            phone = "+49 721 897 6543",
            email = "service@apexautofinance.de",
            authorized_rep = "Anna Müller",
            rep_sign_date = today_ddmmyyyy
        )
        
        # 6. 设置其他信息
        self.contract_data.set_residency_status(False)
        self.contract_data.set_dealer_info(
            name="AutoVision GmbH",
            iban="DE78 3705 0055 0643 0240 00"
        )
        
    def _calculate_apr_from_interest(self, loan_amount, annual_interest_rate, loan_term_months,
        fees=0, start_date=None):
        """
        根据贷款本金、年化利率和手续费计算APR
        
        参数:
        loan_amount: 贷款本金金额(欧元)
        annual_interest_rate: 年化利率(百分比，如4.25表示4.25%)
        loan_term_months: 贷款期限(月)
        fees: 贷款相关手续费(欧元)
        start_date: 贷款开始日期，默认为当前日期
        
        返回:
        apr: 年化利率(百分比，保留2位小数)
        """
        if start_date is None:
            start_date = datetime.now()
        
        # 计算每月还款额
        monthly_interest_rate = annual_interest_rate / 100 / 12
        monthly_payment = (loan_amount * monthly_interest_rate * 
                        (1 + monthly_interest_rate) ** loan_term_months) / \
                        ((1 + monthly_interest_rate) ** loan_term_months - 1)
        
        # 生成现金流
        # 初始现金流：收到的贷款金额减去手续费
        cash_flows = [-(loan_amount - fees)]
        dates = [start_date]
        
        # 生成每月还款的现金流
        for i in range(1, loan_term_months + 1):
            # 计算还款日期（按自然月计算）
            year = start_date.year
            month = start_date.month + i
            
            # 处理月份进位
            while month > 12:
                month -= 12
                year += 1
                
            # 确保日期有效（取当月最后一天如果原日期超过当月天数）
            try:
                payment_date = datetime(year, month, start_date.day)
            except ValueError:
                # 如果日期无效（如2月30日），使用当月最后一天
                if month == 2:
                    # 处理2月特殊情况
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        payment_date = datetime(year, month, 29)
                    else:
                        payment_date = datetime(year, month, 28)
                else:
                    # 其他月份取最后一天
                    payment_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            dates.append(payment_date)
            cash_flows.append(monthly_payment)
        
        # 计算各期现金流的天数差
        days = [(date - start_date).days for date in dates]
        
        # 定义净现值函数
        def npv(rate):
            total = 0.0
            for d, cf in zip(days, cash_flows):
                # 按天计算复利
                total += cf / (1 + rate/100) ** (d/365)
            return total
        
        # 使用二分法寻找使净现值为0的利率(APR)
        def find_apr():
            low = 0.0
            high = 100.0  # 合理的利率上限
            
            # 迭代计算以提高精度
            for _ in range(100):
                mid = (low + high) / 2
                current_npv = npv(mid)
                
                if abs(current_npv) < 1e-6:  # 足够接近0
                    return mid
                elif current_npv > 0:
                    low = mid
                else:
                    high = mid
            return mid
        
        apr = find_apr()
        return round(apr, 2)

    def _cny_to_eur(self, cny_amount, exchange_rate=8.00):
        """
        将人民币转换为欧元
        
        参数:
        cny_amount: 人民币金额
        exchange_rate: 汇率（1欧元可兑换的人民币数量），默认7.85
        
        返回:
        转换后的欧元金额（保留两位小数）
        """
        if cny_amount < 0:
            raise ValueError("金额不能为负数")
        if exchange_rate <= 0:
            raise ValueError("汇率必须大于0")
        
        eur_amount = cny_amount / exchange_rate
        return round(eur_amount, 2)

    def _unify_interest_rate(self, interest_rate):
        """
        统一利率格式，将可能的小数形式（如0.0425）转换为百分比数值形式（如4.25）
        
        参数:
        interest_rate: 输入的利率，可以是float或str类型（如4.25, 0.0425）
        
        返回:
        统一后的利率（保留两位小数的float类型，如4.25）
        """
        # 处理字符串类型的输入
        if isinstance(interest_rate, str):
            try:
                interest_rate = float(interest_rate.strip())
            except ValueError:
                raise ValueError(f"无效的利率格式: {interest_rate}")
        
        # 检查是否为有效的数字
        if not isinstance(interest_rate, (int, float)):
            raise TypeError("利率必须是数字或可转换为数字的字符串")
        
        # 区分小数形式和百分比数值形式
        if 0 < interest_rate < 1:  # 小数形式（如0.0425）
            unified = round(interest_rate * 100, 2)
        else:  # 百分比数值形式（如4.25）或0/1等特殊值
            unified = round(interest_rate, 2)
        
        return unified

    def _get_today_ddmmyyyy(self):
        """
        获取今天的日期，并格式化为DD/MM/YYYY的字符串格式
        
        返回:
            str: 格式为DD/MM/YYYY的日期字符串
        """
        # 获取当前日期
        today = datetime.today()
        
        # 格式化日期: 
        # %d - 两位数的日 (01-31)
        # %m - 两位数的月 (01-12)
        # %Y - 四位数的年份 (例如：2025)
        formatted_date = today.strftime("%d/%m/%Y")
        
        return formatted_date

# ------------------------------
# 2. 合同生成 核心逻辑
# ------------------------------
class LoanContractGenerater:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        print("LoanContractGenerater init complate.")

    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """生成汽车贷款合同（PDF和纯文本） 外部调用入口"""
        try:
            # 生成的合同文件PDF的目录。
            # 根目录/init_data/loan_contract
            contract_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            contract_filename = f"AUTOLOAN-{contract_timestamp}.pdf"
            contract_pdf_path = os.path.join(
                contract_pdf_path_dir, 
                contract_filename
            )
            # 生成的合同文件txt的目录。
            # 根目录/init_data/loan_contract
            contract_filename_txt = f"AUTOLOAN-{contract_timestamp}.txt"
            contract_txt_path = os.path.join(
                contract_pdf_path_dir, 
                contract_filename_txt
            )

            contract_text = self.generate_loan_contract(state.get("loan_structuring_data"), contract_pdf_path, contract_txt_path)
            contract_pdf_metadata = self.get_file_metadata(contract_pdf_path)
            contract_pdf_binary_data = self.read_file_as_binary(contract_pdf_path)
            return {
                "contract_draft": contract_text,
                "contract_file_path": contract_pdf_path,
                "contract_file_metadata": {
                    "binary_data": contract_pdf_binary_data,
                    **contract_pdf_metadata
                },
                "contract_generation_status": "Success",
                "contract_generation_result": "Contract Generation completed. All key parameters are integrated into the contract draft.",
                "status": "Success"
            }
        except Exception as e:
            print(f"合同生成过程出错: {str(e)}")
            return {
                "contract_draft":"",
                "contract_file_path": "",
                "contract_file_metadata": {},
                "contract_generation_status": "Fail",
                "contract_generation_result": f"Contract Generationg aborted: {str(e)}",
                "status": str(e)
            }
    
    # 生成合同 Start
    # 主入口是 contract_generation
    # 二级入口是 generate_loan_contract
    # 以下是生成合同用的方法
    # 生成合同 Start
    def _generate_repayment_schedule(self,
        loan_amount: float, 
        annual_rate: float, 
        term_months: int, 
        start_date: str
    ) -> List[Dict]:
        """生成等额本息还款计划"""
        repayment_schedule = []
        monthly_rate = (annual_rate / 100) / 12  # 月利率
        remaining_principal = loan_amount  # 剩余本金
        
        # 计算每月还款额
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                        ((1 + monthly_rate) ** term_months - 1)
        
        # 解析放款日期
        try:
            day, month, year = map(int, start_date.split('/'))
            current_date = datetime(year, month, day)
        except ValueError as e:
            raise ValueError(f"无效日期格式（需为DD/MM/YYYY）: {start_date}") from e
        
        # 生成每月还款计划
        for month_idx in range(1, term_months + 1):
            # 计算当月利息和本金
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            # 最后一期处理（确保剩余本金为0）
            if month_idx == term_months:
                principal_payment = remaining_principal
                monthly_payment = interest_payment + principal_payment
                remaining_principal = 0.0
            else:
                remaining_principal = max(remaining_principal - principal_payment, 0.0)
            
            # 计算下月还款日期
            try:
                next_date = current_date.replace(month=current_date.month + 1)
            except ValueError:
                if current_date.month == 12:
                    next_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_date = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
            
            # 添加到还款计划
            repayment_schedule.append({
                "month": month_idx,
                "date": next_date.strftime("%d/%m/%Y"),
                "payment_amount": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "remaining_principal": round(remaining_principal, 2)
            })
            
            current_date = next_date
        
        return repayment_schedule


    def _convert_html_to_pdf(self, html_content: str, output_pdf_path: str) -> bool:
        """将HTML内容转换为PDF"""
        try:
            with open(output_pdf_path, "wb") as pdf_file:
                status = pisa.CreatePDF(
                    src=html_content,
                    dest=pdf_file,
                    encoding="utf-8",
                    enable_local_file_access=True
                )
            return not status.err
        except Exception as e:
            raise RuntimeError(f"PDF生成失败: {str(e)}") from e




    # 生成合同的二级入口
    def generate_loan_contract(self, contract_data: Dict, output_pdf_path: str, contract_txt_path:str) -> str:
        """生成汽车贷款合同（PDF和纯文本）"""
        # 验证模板文件
        # template_dir = os.path.dirname(os.path.abspath(__file__))
        # template_filename = "loan_contract_template.jinja2"
        # template_path = os.path.join(template_dir, template_filename)
        # 合同模板文件的目录（不带文件名）
        template_dir = contract_template_dir
        template_path = contract_template_path
        template_filename = contract_template_name
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"合同模板未找到: {template_path}")
        
        # 加载Jinja2模板
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = env.get_template(template_filename)
        
        # 处理数字转换
        converter = NumberConverter
        contract_data["loan_amount_words"] = converter.convert_currency(
            amount=contract_data["loan_amount"],
            currency=contract_data.get("currency", "EUR")
        )
        contract_data["interest_rate_words"] = converter.convert_percentage(contract_data["annual_interest_rate"])
        contract_data["loan_term_words"] = converter.convert_number(contract_data["loan_term_months"])
        
        # 生成还款计划
        contract_data["repayment_schedule"] = self._generate_repayment_schedule(
            loan_amount=contract_data["loan_amount"],
            annual_rate=contract_data["annual_interest_rate"],
            term_months=contract_data["loan_term_months"],
            start_date=contract_data["disbursement_date"]
        )

        # 计算总还款额并保留两位小数
        total_repayment = round(sum(item["payment_amount"] for item in contract_data["repayment_schedule"]), 2)
        contract_data["total_repayment"] = total_repayment
        
        # 计算每月还款额（用于模板显示）
        monthly_rate = (contract_data["annual_interest_rate"] / 100) / 12
        term_months = contract_data["loan_term_months"]
        contract_data["monthly_payment"] = round(
            contract_data["loan_amount"] * (monthly_rate * (1 + monthly_rate) ** term_months) / 
            ((1 + monthly_rate) ** term_months - 1), 2
        )
        
        # 定义兼容xhtml2pdf的CSS样式
        font_config = """
            @page {
                size: A4;
                margin: 2.5cm;
            }
            body {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #000000;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 10px;
            }
            .contract-title {
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .contract-subtitle {
                font-size: 12pt;
                margin-bottom: 15px;
            }
            .contract-info {
                text-align: right;
                margin-bottom: 30px;
                font-size: 11pt;
            }
            .party-title, .article-title, .appendix-title {
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .party-title {
                font-size: 14pt;
                text-decoration: underline;
            }
            .article-title {
                font-size: 13pt;
            }
            .appendix-title {
                font-size: 14pt;
                text-align: center;
                margin-top: 40px;
            }
            .signature-section {
                margin-top: 160px;
                display: flex;
                justify-content: space-between;
            }
            .signature-block {
                width: 45%;
            }
            ul, ol {
                margin: 10px 0 15px 25px;
            }
            li {
                margin-bottom: 8px;
            }
            p {
                margin: 12px 0;
            }
            table.repayment-schedule {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 10pt;
            }
            table.repayment-schedule th, 
            table.repayment-schedule td {
                border: 1px solid #000;
                padding: 6px 4px;
                text-align: center;
            }
            table.repayment-schedule th {
                background-color: #f0f0f0;
            }
            
            /* 下划线样式 - 关键修复 */
            .underline {
                text-decoration: underline !important;
                text-underline-offset: 3px !important;
                text-decoration-thickness: 1px !important;
                padding: 0 2px !important;
                margin: 0 3px !important;
                white-space: nowrap;
            }
            .underline-short {
                min-width: 80px;
                display: inline-block;
            }
            .underline-medium {
                min-width: 150px;
                display: inline-block;
            }
            .underline-long {
                min-width: 250px;
                display: inline-block;
            }
            .underline-amount {
                min-width: 180px;
                display: inline-block;
                text-align: right;
            }
            .underline-signature {
                text-decoration: underline;
                text-underline-offset: 4px;
                padding-bottom: 1px;
                /* 确保下划线连续且清晰，不被字符打断 */
                white-space: nowrap;
            }
        """
        
        # 渲染HTML
        html_content = template.render(data=contract_data, font_config=font_config)
        
        # 生成PDF
        if not self._convert_html_to_pdf(html_content, output_pdf_path):
            raise RuntimeError("PDF Generation Failed (Unknown Error)")

        """将HTML转换为纯文本"""
        soup = BeautifulSoup(html_content, 'html.parser')
        plain_text = soup.get_text()
        
        # 清理文本
        plain_text = re.sub(r'\n+', '\n', plain_text)
        plain_text = re.sub(r' +', ' ', plain_text)
        plain_text = '\n'.join([line.strip() for line in plain_text.split('\n')])
        
        contract_text = plain_text.strip()
    
        with open(contract_txt_path, "w", encoding="utf-8") as f:
            f.write(contract_text)
        
        return contract_text
    
    def read_file_as_binary(self, file_path):
        """将文件读取为二进制数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        try:
            with open(file_path, 'rb') as file:
                binary_data = Binary(file.read())
            return binary_data
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            raise
    
    def get_file_metadata(self, file_path):
        """获取文件的元数据"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件扩展名确定文件类型
        file_type = ""
        if file_ext == ".jpg" or file_ext == ".jpeg":
            file_type = "image/jpeg"
        elif file_ext == ".pdf":
            file_type = "application/pdf"
        elif file_ext == ".docx":
            file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_ext == ".doc":
            file_type = "application/msword"
            
        return {
            "file_name": file_name,
            "file_type": file_type,
            "file_extension": file_ext,
            "file_size": os.path.getsize(file_path)  # 文件大小（字节）
        }

# 生成合同 End


# ------------------------------
# 3. 合同合规检查 核心逻辑（使用官方RedisVectorStore）
# ------------------------------
class LoanComplianceChecker:
    def __init__(self, llm: BaseChatModel):
        # 初始化DashScope嵌入模型
        DASHSCOPE_API_KEY = load_key("DASHSCOPE_API_KEY")
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=DASHSCOPE_API_KEY
        )
        
        # Redis配置（本地Redis）
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.index_name = "german_loan_legal_index"  # 索引名称
        
        # 加载基础条款
        self.basic_clauses = self._load_basic_clauses()
        
        # 初始化官方RedisVectorStore并加载特殊场景条款
        self.vector_store = self._initialize_vector_store()
        
        # 初始化大模型
        self.llm = llm
        
        # 初始化解析器
        self.parser = PydanticOutputParser(pydantic_object=ContractComplianceCheckResponse)

    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """执行合同合规检查 外部调用入口"""
        try:
            business_context = ContractBusinessContext(
                is_early_repayment=False,
                is_foreign_resident=False, 
                is_vehicle_old=False, 
                is_vehicle_registration_cross_border=False
            )
            result = self.check_compliance(
                state.get("contract_draft",""), 
                business_context
                )
        
            # 新增：转换为FinalResult
            final_result = self._format_final_result(result)
            
            # 可选择转换为字典返回。Pydantic v2 正确用法
            final_result_dict = final_result.model_dump()

            self._print_structured_result(final_result_dict)

            return {
                "contract_review_status": final_result_dict.get("overall_result"), # Approved/Rejected
                "contract_review_result": "Contract review completed.",
                "contract_review_result_details": final_result_dict,
                "status": final_result_dict.get("overall_result") # Approved/Rejected
            }
        except Exception as e:
            print(f"合同检查过程出错: {str(e)}")
            return {
                "contract_review_status": "Fail",
                "contract_review_result": f"Contract review aborted: {str(e)}",
                "contract_review_result_details": {},
                "status": str(e)
            }
    def check_compliance(self, contract_content: str, business_context: ContractBusinessContext) -> ContractComplianceCheckResponse:
        """执行合同合规检查（基础条款 + 官方RAG增强）"""
        # 1. 创建基础条款检查提示词
        all_clauses_text = ""
        basic_clauses_text = "\n".join([
            f"- Check ID: {clause['id']}"
            f" | Check Title: {clause['title']}"
            f" | Check Requirement: {clause['content']}"
            f" | Check Points: {', '.join(clause['check_points'])}"
            for clause in self.basic_clauses
        ])
        # 2. 识别特殊场景，并将特殊场景的检查规范加到提示词里
        scenarios = self._identify_scenarios(contract_content,business_context)
        formatted_clauses = []
        if not scenarios:
            # 无特殊场景
            all_clauses_text = basic_clauses_text
        else:
            # 有特殊场景
            # 特殊场景RAG增强检查（使用官方向量存储的检索功能）
            # 定义场景与核心查询词的映射（明确每个场景的合规需求）
            scenario_queries = {
                "used_vehicle": "Legal clauses for used vehicle loan scenarios, including vehicle valuation and accident history disclosure requirements",
                "foreign_borrower": "Regulations related to identity verification and cross-border credit checks for foreign borrower loans",
                "early_repayment": "Legal provisions on penalty restrictions and application procedures for early loan repayment",
                "cross_border": "Legal requirements for registration and insurance in cross-border vehicle loans"
            }

            # 特殊场景RAG增强检查
            for scenario in scenarios:
                
                # 1. 获取该场景的精准查询词（而非用合同全文）
                query = scenario_queries.get(scenario, scenario)  # 默认用场景名称
                
                # 2. 检索该场景下的相关法规法规
                # 使用官方方法检索相关条款（支持元数据过滤）
                filter = f'@scenario:{{{scenario}}}'
                relevant_clauses = self.vector_store.similarity_search(
                    query=query,  # 用场景核心需求作为查询
                    k=3,
                    filter=filter # 元数据过滤
                )

                # # 如果元数据过滤不好用，那就注释掉上面的filter=filter，用下面的手动筛选选出 metadata.scenario 等于目标 scenario 的结果
                # # 把relevant_clauses和all_clauses 变量名调整一下
                # relevant_clauses = [
                #     clause for clause in all_clauses 
                #     if clause.metadata.get('scenario') == scenario
                # ]

                # 3. 格式化当前场景的检索结果，并追加到总列表中
                current_scenario_clauses = [
                    {
                        "id": doc.metadata["id"],
                        "scenario": doc.metadata["scenario"],
                        "title": doc.metadata["title"],
                        "content": doc.page_content,
                        "score": 1.0  # 官方库未直接返回分数，可通过其他方式获取
                    }
                    for doc in relevant_clauses
                ]
                # 关键修改：用extend追加当前场景的结果，而非覆盖
                formatted_clauses.extend(current_scenario_clauses)

            """创建特殊场景检查提示词"""
            specific_clauses_text = "\n".join([
                f"- Check ID: {clause['id']}"
                f" | Check Title: {clause['title']}"
                f" | Check Requirement: {clause['content']}"
                # 特殊场景条款无check_points，无需额外拼接，保持格式简洁
                for clause in formatted_clauses
            ])
            # 用join拼接：列表中的元素会被"\n"连接，自动在两者之间添加换行符
            all_clauses_text = "\n".join([basic_clauses_text, specific_clauses_text])

        # 3. 执行条款检查
        # 生成提示词
        check_prompt = self._create_check_prompt(
            clauses_text = all_clauses_text,
            contract_content=contract_content
        )
        print("提示词：")
        print(check_prompt.messages)

        check_response = self.llm.invoke(check_prompt)
        check_results = self.parser.parse(check_response.content)
        print("合同检查结果 check_results:")
        print(check_results)
        all_results = check_results.results
       
        # 4. 生成最终结果
        overall_compliant = all(c.compliant for c in all_results)
        return ContractComplianceCheckResponse(
            overall_compliant=overall_compliant,
            results=all_results,
            summary=f"Checked {len(all_results)} items. {len([c for c in all_results if not c.compliant])} non-compliant issues found."
        )

    def _load_basic_clauses(self) -> List[Dict]:
        """加载基础条款（直接读取文档）"""
        with open(basic_clauses_file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _initialize_vector_store(self) -> RedisVectorStore:
        """初始化官方RedisVectorStore，加载特殊场景条款"""
        # 检查向量存储是否已存在（避免重复创建）
        try:
            # 尝试连接现有索引
            vector_store = RedisVectorStore.from_existing_index(
                embedding=self.embeddings,
                redis_url=self.redis_url,
                index_name=self.index_name
            )
            print(f"已加载现有向量存储，索引名称: {self.index_name}")
            return vector_store
        except:
            # 不存在则创建新索引并加载文档
            print(f"创建新向量存储，索引名称: {self.index_name}")
            return self._load_advanced_scenarios_to_vector_store()

    def _load_advanced_scenarios_to_vector_store(self) -> RedisVectorStore:
        """将特殊场景条款加载到官方RedisVectorStore"""
        with open(advanced_clauses_file_path, "r", encoding="utf-8") as f:
            scenarios = json.load(f)
        
        # 格式化文档为LangChain的Document格式（带元数据）
        documents = []
        for scenario in scenarios:
            for item in scenario["legal_items"]:
                content = f"{item['title']}\n{item['content']}\nApplication: {item['application']}"
                # 添加元数据（支持后续过滤）
                metadata = {
                    "scenario": scenario["scenario"],
                    "id": item["id"],
                    "title": item["title"],
                    "description": scenario["description"]
                }
                documents.append(Document(page_content=content, metadata=metadata))
        
        # 若仍报错，尝试完全移除索引控制参数（部分版本默认索引所有字段）
        metadata_schema = [
            {"name": "scenario", "type": "tag"},
            {"name": "id", "type": "tag"},
            {"name": "title", "type": "text"},
            {"name": "description", "type": "text"},
        ]

        # 2. 计算嵌入维度（与模型一致）
        vector_size = len(self.embeddings.embed_query("test"))  # 用测试查询获取维度
        print(f"嵌入维度：{vector_size}，准备创建索引...")
        
        # 使用官方方法创建向量存储
        return RedisVectorStore.from_documents(
            documents=documents,
            embedding=self.embeddings,
            redis_url=self.redis_url,
            index_name=self.index_name,
            # 自定义索引配置（使用HNSW提升大规模数据检索性能）
            index_type="HNSW",  # 支持FLAT/HNSW/IVF，HNSW适合后续扩展
            distance_metric="COSINE",
            metadata_schema=metadata_schema,  # 传入字典格式的元数据配置
            vector_size=vector_size  # 强制指定向量维度，避免自动检测误差
        )

    def _identify_scenarios(self, contract_content: str, business_context: ContractBusinessContext) -> List[str]:
        """
        双维度场景识别：
        1. 法定必查场景：无条件检查（如提前还款）
        2. 事实驱动场景：基于外部业务信息强制检查（如实际是外籍借款人，二手车）
        """        
        # --------------------------
        # 1. 法定必查场景（强制检查）
        # 提前还款场景应该强制检查。但是先做成可选。
        # --------------------------
        # mandatory_scenarios = ["early_repayment"]
        mandatory_scenarios = []
        
        # --------------------------
        # 2. 事实驱动场景（基于外部信息强制检查）
        # 核心逻辑：如果实际情况符合场景，无论合同是否提及，都必须检查
        # --------------------------
        fact_based_scenarios = []
        
        # 提前还款场景：实际是提前还款 → 强制检查
        if business_context.is_early_repayment:
            fact_based_scenarios.append("early_repayment")

        # 外籍借款人场景：实际是外籍居民 → 强制检查
        if business_context.is_foreign_resident:
            fact_based_scenarios.append("foreign_borrower")
        
        # 二手车场景：实际是二手车 → 强制检查
        if business_context.is_vehicle_old:
            fact_based_scenarios.append("used_vehicle")
        
        # 跨境场景：车辆在国外注册 → 强制检查
        if business_context.is_vehicle_registration_cross_border:
            fact_based_scenarios.append("cross_border")
        
        # --------------------------
        # 合并所有场景（去重）
        # --------------------------
        all_scenarios = list(set(mandatory_scenarios + fact_based_scenarios))
        return all_scenarios


    def _create_check_prompt(self, clauses_text:str, contract_content: str) -> ChatPromptTemplate:
        """创建检查提示词（包含中英文检查过程说明）"""
        # 如果涉及到特殊场景，那么{basic_clauses}里面就包含了通用条款和特殊场景条款。
        # 如果没涉及到特殊场景条款，{basic_clauses}就只包含了通用条款。
       
        prompt = ChatPromptTemplate.from_template("""
You are a legal expert legal expert specializing in German loan contracts. Please check the following contract against all legal requirements provided in the "LEGAL REQUIREMENTS" section below.

CONTRACT CONTENT:
{contract_content}

LEGAL REQUIREMENTS:
This section includes two types of requirements:
1. General mandatory requirements (applicable to all loan contracts)
2. Special scenario requirements (clearly related to specific situations, e.g., used vehicles, foreign borrowers, early repayment, cross border)

Each requirement follows this format: "- Check ID: [ID] | Check Title: [Title] | Check Requirement: [Rule]"
{clauses_text}

CRITICAL NOTE ON SPECIAL SCENARIO REQUIREMENTS:
If "LEGAL REQUIREMENTS" contains any special scenario requirements, this CONFIRMS that the contract has already been verified (through other channels) to apply to those specific scenarios. These requirements MUST be checked for compliance without any further verification of scenario applicability. You are obligated to evaluate the contract against these special scenario requirements as mandatory items.                                              

INSTRUCTIONS:
For each requirement in "LEGAL REQUIREMENTS", do the followings:
- 1. Extract content after "Check Title: " as "check_title", content after "Check ID: " as "check_id".
- 2. Determine if the contract complies with the requirement (set "compliant" to True/False). For special scenario requirements, enforce the check as the contract's applicability to the scenario has already been confirmed through other channels.
- 3. Provide Chinese check process explanation for "check_process_chinese".
- 4. Provide English check process explanation for "check_process_english".
- 5. If non-compliant, give precise English revision suggestions for "english_revision" (None if compliant).
- 6. Note the location of issues if applicable for the "location" field.

{format_instructions}
        """)
        
        return prompt.format_prompt(
            contract_content=contract_content,
            clauses_text=clauses_text,
            format_instructions=self.parser.get_format_instructions()
        )
    
    def _format_final_result(self, check_response: ContractComplianceCheckResponse) -> ContractCheckFinalResult:
        """将合规检查结果转换为ContractCheckFinalResult格式"""
        # 1. 整体结果（Approved/Rejected）
        overall_result = "Approved" if check_response.overall_compliant else "Rejected"
        
        # 2. 合并所有检查项的详情（按顺序，换行分隔）
        detail_results = "\n".join([
            f"[{item.check_id} {item.check_title}] {'PASS' if item.compliant else 'FAIL'}\n"
            f"Chinese Explanation: {item.check_process_chinese}\n"
            f"English Explanation: {item.check_process_english}\n"
            + (f"Revision: {item.english_revision}\n" if not item.compliant and item.english_revision is not None else "")
            for item in check_response.results
        ])
        
        # 3. 提取摘要（直接复用原摘要）
        summary = check_response.summary
        
        # 4. 合并所有修改建议（仅非合规项，换行分隔）
        revisions = [
            {
                "check_id": item.check_id,
                "check_title": item.check_title,
                "compliant_result": "PASS" if item.compliant else "FAIL",
                "english_explanation": item.check_process_english,
                "revision_content": item.english_revision  # 仅包含非合规且有修改建议的项
            }
            for item in check_response.results
            # 筛选条件：不合规 且 存在修改建议
            if not item.compliant and item.english_revision is not None
        ]
        
        # 返回FinalResult对象（或转换为字典）
        return ContractCheckFinalResult(
            overall_result=overall_result,
            detail_results=detail_results,
            summary=summary,
            revisions=revisions
        )
    
    def _print_structured_result(self, result_dict: dict):
        """结构化打印结果，易确认格式"""
        print("=" * 60)
        print("📋 德国车贷合同检查最终结果")
        print("=" * 60)

        # 整体结论
        print(f"\n【1】整体检查结论")
        print("-" * 30)
        print(f"检查结果：{result_dict['overall_result']}")

        # 详细检查项
        print(f"\n【2】所有检查项详情")
        print("-" * 30)
        # 保留换行符，优化显示
        detail_content = result_dict['detail_results'].replace("\n", "\n  ")
        print(f"  {detail_content}")

        # 英文摘要
        print(f"\n【3】检查结果英文摘要")
        print("-" * 30)
        print(f"Summary: {result_dict['summary']}")

        # 修改建议
        print(f"\n【4】英文修改建议")
        print("-" * 30)
        revisions = result_dict['revisions']  # 现在是字典列表，变量名改为复数更准确
        
        if revisions and len(revisions) > 0:  # 确认列表非空
            # 循环遍历每个修改建议字典，逐条打印字段
            for idx, rev in enumerate(revisions, start=1):  # idx用于标记建议序号
                print(f"\n  建议{idx}（对应检查项：{rev['check_id']} - {rev['check_title']}）")
                print(f"    • 合规检查结果：{rev['compliant_result']}")
                print(f"    • 修改原因：{rev['english_explanation']}")
                print(f"    • 具体建议：{rev['revision_content']}")
        else:
            print(f"  ✅ 无修改建议（所有检查项合规）")

        print("\n" + "=" * 60)


# ------------------------------
# 4. 合同修改核心逻辑
#    先改合同模板，再生成合同
# ------------------------------
class ContractTempAndContentModifier:
    def __init__(self, llm: BaseChatModel):
        # 初始化大模型客户端（可根据需要替换为其他模型）
        self.llm = llm
    
    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """执行合同合规检查 外部调用入口"""
        try:
            # 生成的合同文件PDF的目录。
            # 根目录/init_data/loan_contract
            contract_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            contract_filename = f"AUTOLOAN-{contract_timestamp}.pdf"
            contract_pdf_path = os.path.join(
                contract_pdf_path_dir, 
                contract_filename
            )
            # 生成的合同文件txt的目录。
            # 根目录/init_data/loan_contract
            contract_filename_txt = f"AUTOLOAN-{contract_timestamp}.txt"
            contract_txt_path = os.path.join(
                contract_pdf_path_dir, 
                contract_filename_txt
            )

            # 修改合同模板
            revisions = state.get("contract_review_result_details",{}).get("revisions",[])
            self.modify_template(revisions)
            # 再次生成合同
            generater = LoanContractGenerater(self.llm)
            contract_text = generater.generate_loan_contract(state.get("loan_structuring_data"), contract_pdf_path, contract_txt_path)

            contract_pdf_metadata = generater.get_file_metadata(contract_pdf_path)
            contract_pdf_binary_data = generater.read_file_as_binary(contract_pdf_path)

            return {
                "contract_draft":contract_text,
                "contract_file_path": contract_pdf_path,
                "contract_file_metadata": {
                    "binary_data": contract_pdf_binary_data,
                    **contract_pdf_metadata
                },
                "contract_modify_status": "Success",
                "contract_modify_result": "Contract modifycompleted.",
                "status": "Success"
            }

        except Exception as e:
            print(f"合同修改过程出错: {str(e)}")
            return {
                "contract_draft": "",
                "contract_file_path": "",
                "contract_file_metadata": {},
                "contract_modify_status": "Fail",
                "contract_modify_result":  f"Contract modify aborted: {str(e)}",
                "status": str(e)
            }

    def _create_prompt(self, original_template: str, revisions_text: str) -> ChatPromptTemplate:
        """生成用于修改模板的大模型提示词"""
        prompt = ChatPromptTemplate.from_template("""
You are a senior expert specializing in German loan contract modification, with deep experience in HTML/Jinja2 template editing. 
Your task is to fix all non-compliant issues in the template based on the provided revision suggestions.

CRITICAL CONSTRAINTS (MUST OBEY)
- DO NOT modify any CSS styles (including <style> tags, class attribute values like "contract-clause", style attributes like "color: #333").
- DO NOT remove or alter existing Jinja2 variables (e.g., {{ data.lender.name }}, {{ font_config }}, {{ loan_amount }}).
- DO NOT change the overall HTML structure (MUST keep all original tags like <span>, <div>, <p>, <h3>, <table> and their layout).
- All modifications must maintain valid HTML syntax (all tags must be properly closed, and nesting must be correct (e.g., <p> inside <div>, not vice versa).)

REVISION REQUIREMENTS
Each requirement follows the format: "- Issue: [content] | Problem: [content] | Required changes: [content]"
{revisions_text}

ORIGINAL TEMPLATE
{original_template}

OUTPUT INSTRUCTIONS
Return ONLY the modified template content. Do not include any explanations, comments, or additional text.
Ensure the modified template retains all original functionality and formatting except for the required changes.
        """)


        return prompt.format_prompt(
            revisions_text=revisions_text,
            original_template=original_template
        )

    def _backup_original_template(self, template_path: str, backup_dir: str) -> str:
        """备份原始模板文件"""
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成带时间戳的备份文件名
        # 生成带毫秒的时间戳（格式：YYYYMMDD_HHMMSSfff，其中fff为毫秒）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]  # %f是微秒，取前3位作为毫秒
        filename = os.path.basename(template_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制文件进行备份
        shutil.copy2(template_path, backup_path)
        print(f"已备份原始模板至: {backup_path}")
        return backup_path

    def modify_template(self, revisions:List[dict]) :
        """修改合同模板的主方法"""
        # 1. 获取需要修改的不合规项
        if not revisions:
            print("没有需要修改的不合规项，直接返回原始模板")
            with open(contract_template_path, "r", encoding="utf-8") as f:
                return f.read()

        # 2. 备份原始模板
        self._backup_original_template(contract_template_path, contract_template_backup_dir)

        # 3. 读取原始模板内容
        with open(contract_template_path, "r", encoding="utf-8") as f:
            original_template = f.read()

        # 4. 生成提示词
        revisions_text = "\n".join([
            # 使用enumerate获取索引（start=1表示从1开始计数）
            f"- Issue: {idx} ({item['check_id']}: {item['check_title']})"
            f" | Problem: {item['english_explanation']}"
            f" | Required changes: {item['revision_content']}"
            for idx, item in enumerate(revisions, start=1)  # 关键：enumerate获取索引
        ])

        prompt = self._create_prompt(original_template, revisions_text)

        # 5. 调用大模型进行修改
        print(f"正在调用大模型修改模板，共需处理 {len(revisions)} 项修改...")
        check_response = self.llm.invoke(prompt)
        modified_template = ""
        # 处理响应：确认类型并提取内容
        if isinstance(check_response, AIMessage):
            # 提取大模型返回的文本内容（核心操作）
            modified_template = check_response.content.strip()
            print("模型返回内容:", modified_template)
        else:
            raise TypeError(f"预期AIMessage类型，实际得到{type(check_response)}")


        # 6. 保存修改后的模板
        with open(contract_template_path, "w", encoding="utf-8") as f:
            f.write(modified_template)
        print(f"模板修改完成，已更新文件: {contract_template_path}")



# ------------------------------
# 6. 使用示例
# ------------------------------
""" if __name__ == "__main__":

    # ------------------------------
    # 1. 合同所需数据准备，结构化
    # ------------------------------
    # 假数据
    # raw_data = state_V03
    state={
        "user_id" : "68b1386d1a6e3977aeab96e5",
        "fullName" : "Zhang San",
        "idNumber" : "110105200001010000",
        "missing_fields": [],
        "contract_draft": "",
        "contract_discussion": [],
        "contract_discussion_round": 0,
        "contract_structured": "",
        "check_attempts": 0,
        "dialogue_loop_count": 0,

        "raw_data": {
            "application_id": "APPL_372F03A6",  # 申请ID
            "user_id": "68b1386d1a6e3977aeab96e5",
            "personal_info": {
                "fullName": "Zhang San",    # 合同里借款人名用这个
                "idNumber": "21112120000101000Y",
                "phoneNumber": "19112345678",
                "email": "applicient000001@example.com",
                "address": "No. 001, Beifang Street, Chaoyang District, Beijing 100020, P.R. China",
                "accountNumber": "281738000001111122222",
            },
            "car_selection": {
                "carBrand": "BMW",
                "carModel": "2025 3.0T Luxury"

            },
            "loan_details": {
                "loanAmount": 102900,
                "interestRate": 3,
                "loanTerm": 24
            },
        }
    }

    # 验证state类型（确保是类实例而非字典）
    print(f"state类型: {type(state)}")  

    structor = LoanStructuringAgent()
    result_structor = structor.process(state)
    state["loan_structuring_data"] = result_structor.get("loan_structuring_data")
    state["loan_structuring_status"] = result_structor.get("loan_structuring_status")
    state["loan_structuring_result"] = result_structor.get("loan_structuring_result")

    # --------------------------------        
    # 2. 生成合同
    # --------------------------------  

    if state["loan_structuring_status"] == "Success":
        generater = LoanContractGenerater()
        result_generater = generater.process(state)
        state["contract_draft"] = result_generater.get("contract_draft")
        state["contract_generation_status"] = result_generater.get("contract_generation_status")
        state["contract_generation_result"] = result_generater.get("contract_generation_result")
        state["contract_file_path"] = result_generater.get("contract_file_path")
        state["contract_file_metadata"] = result_generater.get("contract_file_metadata")
        print(f"✅ 合同生成成功！")
        print(f"PDF文件路径：{state['contract_file_path']}")
    else:
        state["contract_generation_status"] = ""


    # --------------------------------        
    # 3. 执行合规检查
    # --------------------------------    
    if state["contract_generation_status"] == "Success":
        checker = LoanComplianceChecker(llm)
        result_checker = checker.process(state)
        state["contract_review_status"] = result_checker.get("contract_review_status")
        state["contract_review_result"] = result_checker.get("contract_review_result")
        state["contract_review_result_details"] = result_checker.get("contract_review_result_details")
    else:
        state["contract_review_status"] = ""


    # --------------------------------        
    # 4. 合规模板修改
    # revisions = final_result_dict.get("revisions", [])  # 获取不合规项列表
    # modified_template = modifier.modify_template(revisions)
    # --------------------------------      
    if state["contract_review_status"] == "Rejected":
        modifier = ContractTempAndContentModifier(llm)
        result_modifier = modifier.process(state)
        state["contract_draft"] = result_modifier.get("contract_draft")
        state["contract_modify_status"] = result_modifier.get("contract_modify_status")
        state["contract_modify_result"] = result_modifier.get("contract_modify_result")
        state["contract_file_path"] = result_modifier.get("contract_file_path")
        state["contract_file_metadata"] = result_modifier.get("contract_file_metadata")
        print(f"✅ 合同生成成功！")
        print(f"PDF文件路径：{state['contract_file_path']}")
    else:
        state["contract_modify_status"] = ""


    # 再次review合同
    if state["contract_modify_status"] == "Success":
        checker = LoanComplianceChecker(llm)
        result_checker = checker.process(state)
        state["contract_review_status"] = result_checker.get("contract_review_status")
        state["contract_generation_status"] = result_checker.get("contract_review_result")
        state["contract_generation_result"] = result_checker.get("contract_review_result_details") """




