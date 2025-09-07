from typing import Dict, Any
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
import requests
import json
import re
import datetime
from pymongo import MongoClient
from typing import Dict, Tuple, List
from langchain_redis import RedisVectorStore

load_dotenv()
def extract_text_from_pdf(pdf_path: str) -> str:
    """提取PDF文本"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def build_prompt(pdf_text: str) -> str:
    """生成提示词"""
    prompt = (
        "请从以下征信报告文本中，提取以下字段并以JSON格式输出\n"
        "- 近2年逾期次数\n"
        "- 是否有90天以上逾期\n"
        "- 信用卡总额度\n"
        "- 信用卡已用额度\n"
        "- 其他贷款余额\n"
        "- 信贷账户总数\n"
        "- 是否有法院/欠税/失信等记录\n"
        "- 近3月征信查询次数\n\n"
        "征信报告原文如下：\n"
        f"{pdf_text}"
    )
    return prompt

def call_llm(prompt: str) -> Dict[str, Any]:
    """
    调用阿里大模型API解析结构化数据
    """
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {dashscope_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-turbo",  # 可根据实际模型调整
        "input": {
            "prompt": prompt
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        # 假设返回内容在 result['output']['text']，需根据实际API返回结构调整
        text = result.get('output', {}).get('text', '')
        try:
            # 尝试提取JSON结构
            data = json.loads(text)
        except Exception:
            # 如果不是标准JSON，做简单清洗
            import re
            json_str = re.search(r'\{.*\}', text, re.DOTALL)
            if json_str:
                data = json.loads(json_str.group())
            else:
                data = {}
        return data
    else:
        print("API调用失败:", response.text)
        return {}
    
def calculate_credit_rating(data: Dict[str, Any]) -> Dict[str, Any]:
    """根据评分标准计算信用分"""
    score = 0
    # 还款历史
    overdue_count_2y = data.get("近2年逾期次数", 0)
    if overdue_count_2y == 0:
        score += 30
    elif overdue_count_2y == 1:
        score += 10
    elif overdue_count_2y == 2:
        score -= 10
    elif overdue_count_2y > 2:
        score -= 30
    overdue_60plus_flag = data.get("是否有60天以上逾期", "无")
    if overdue_60plus_flag == "有":
        score -= 50
    else:
        score += 20
    # 负债水平
    card_total = data.get("信用卡总额度", 1)
    card_used = data.get("信用卡已用额度", 0)
    card_ratio = card_used / card_total if card_total else 0
    if card_ratio < 0.5:
        score += 10
    elif 0.5 <= card_ratio <= 0.8:
        score += 0
    else:
        score -= 10
    loan_balance = data.get("其他贷款余额", 0)
    if loan_balance < 100000:
        score += 10
    elif 100000 <= loan_balance <= 300000:
        score += 0
    else:
        score -= 10
    # 账户数量
    account_num = data.get("信贷账户总数", 1)
    if 1 <= account_num <= 5:
        score += 10
    elif account_num > 5:
        score += 0
    # 公共记录
    public_record = data.get("是否有法院/欠税/失信等记录", "无")
    if public_record == "有":
        score -= 50
    else:
        score += 10
    # 查询记录
    query_count_3m = data.get("近3月征信查询次数", 0)
    if query_count_3m < 3:
        score += 10
    elif 3 <= query_count_3m <= 6:
        score += 0
    else:
        score -= 10
    # # 评级
    # if score >= 80:
    #     level = "A"
    # elif score >= 40:
    #     level = "B"
    # else:
    #     level = "C"
    return {"score": score}

def credit_rating_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """一站式完成PDF信用评分流程"""
    pdf_text = extract_text_from_pdf(pdf_path)
    prompt = build_prompt(pdf_text)
    parsed_data = call_llm(prompt)
    result = calculate_credit_rating(parsed_data)
    return {
        "pdf_text": pdf_text,
        "prompt": prompt,
        "parsed_data": parsed_data,
        "credit_rating": result
    }

def search_regulations(redis_store: RedisVectorStore, query: str) -> List[str]:
     """从Redis中搜索相关法规"""
     docs = redis_store.similarity_search(query, k=4)
     return [doc.page_content for doc in docs]

def check_id_integrity(id_number: str, full_name: str) -> Tuple[bool, str]:
    """检查身份证信息完整性"""
    # 身份证格式校验
    if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$', id_number):
        return True, "身份证号码格式无效"
    
    # 姓名校验
    if len(full_name) < 2:
        return True, "姓名信息不完整"
    
    # 提取出生日期验证年龄格式
    if len(id_number) >= 18:
        try:
            birth_date_str = id_number[6:14]
            birth_date = datetime.datetime.strptime(birth_date_str, "%Y%m%d")
            if birth_date > datetime.datetime.now():
                return True, "身份证出生日期无效"
        except ValueError:
            return True, "身份证出生日期格式错误"
    
    return False, "身份证信息格式验证通过"

def verify_income_authenticity(monthly_income: float, salary: float, company_name: str) -> Tuple[bool, str]:
    """验证收入真实性"""
    # 工作证明与银行流水比对
    if monthly_income > 0:
        income_diff_ratio = abs(monthly_income - salary) / monthly_income
        if income_diff_ratio > 0.3:  # 差异超过30%
            return True, f"工作证明月薪（{monthly_income}元）与银行流水（{salary}元）差异超30%"
    
    # 行业收入水平校验
    industry_benchmark = {
        "科技": (8000, 50000),
        "制造": (5000, 20000),
        "金融": (10000, 60000),
        "服务": (4000, 15000),
        "教育": (6000, 25000)
    }
    
    # 从公司名称推断行业
    inferred_industry = None
    for industry in industry_benchmark:
        if industry in company_name:
            inferred_industry = industry
            break
    
    if inferred_industry:
        min_inc, max_inc = industry_benchmark[inferred_industry]
        if not (min_inc * 0.8 <= monthly_income <= max_inc * 1.2):
            return True, f"月薪与{inferred_industry}行业水平不符（合理范围{min_inc}-{max_inc}元）"
    
    return False, "收入信息验证通过"

def detect_abnormal_transactions(salary: float) -> Tuple[bool, str]:
    """检测异常交易"""
    # 实际应用中应传入完整交易记录进行分析
    # 这里简化处理，假设没有检测到异常
    return False, "暂时没有检测到大额异常流入/流出，及频繁小额贷款。"

def check_blacklist_from_mongo(mongo_client: MongoClient, id_number: str) -> Tuple[bool, str]:
    """从MongoDB查询身份证号是否在黑名单中"""
    try:
        # 访问Auto_Finance数据库中的BlackNameList集合
        collection = mongo_client["Auto_Finance"]["BlackNameList"]
        
        # 查询身份证号是否存在于黑名单
        result = collection.find_one({"idNumber": id_number})
        
        if result:
            # 从黑名单记录中获取原因，默认为"存在欺诈历史记录"
            reason = result.get("reason", "存在欺诈历史记录")
            return True, reason
        return False, "未在黑名单中查询到该身份信息"
    
    except Exception as e:
        # 处理数据库查询异常
        return True, f"黑名单检查失败：{str(e)}"