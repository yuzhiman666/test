# demo/backend/models.py (新增文件)
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import datetime

class MultiLanguageField(BaseModel):
    """多语言字段模型"""
    zh: str
    en: str
    ja: str

class PersonalInfo(BaseModel):
    full_name: MultiLanguageField
    id_number: str  # 身份证号通常保持原样，不翻译
    phone_number: str
    email: str
    address: MultiLanguageField
    employment_status: MultiLanguageField
    monthly_income: float
    account_holder_name: MultiLanguageField
    account_number: str
    bank_name: MultiLanguageField

class CarSelection(BaseModel):
    car_brand: MultiLanguageField
    car_model: MultiLanguageField
    car_year: int
    car_type: MultiLanguageField
    car_price: float

class LoanDetails(BaseModel):
    down_payment_ratio: float
    down_payment_amount: float
    loan_amount: float
    interest_rate: float
    loan_term_months: int
    loan_start_date: datetime.datetime
    loan_end_date: datetime.datetime
    repayment_frequency: MultiLanguageField
    monthly_payment: float
    repayment_date: int
    repayment_method: MultiLanguageField

class DocumentInfo(BaseModel):
    file_name: str
    file_type: str
    file_extension: str
    file_size: int
    binary_data: bytes
    uploaded_at: datetime.datetime

class LoanApplication(BaseModel):
    application_id: str
    user_id: str
    status: str  # Draft, InReview, Submitted, Approved, Rejected
    personal_info: PersonalInfo
    car_selection: CarSelection
    loan_details: LoanDetails
    documents: List[DocumentInfo]
    ai_suggestion: Optional[MultiLanguageField] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime