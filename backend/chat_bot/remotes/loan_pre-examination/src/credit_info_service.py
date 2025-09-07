from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pymongo import MongoClient
from datetime import datetime
import random

# 定义返回结果的数据模型
class CreditInfoResult(BaseModel):
    id_number: str
    credit_report: List[str] = Field(default_factory=list)
    error: Optional[str] = None

# 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bmw_credit_db']
credit_collection = db['credit_information']

# def get_credit_info(id_number: str) -> Dict:
#     """
#     根据身份证号查询用户征信信息，并返回CreditInfoResult模型
#     :param id_number: 身份证号
#     :return: CreditInfoResult对象
#     """
#     try:
#         if not id_number:
#             return CreditInfoResult(
#                 id_number="",
#                 error="身份证号不能为空"
#             ).model_dump()
        
#         # 从MongoDB查询数据
#         credit_info = credit_collection.find_one({"id_number": id_number})
        
#         if not credit_info:
#             return CreditInfoResult(
#                 id_number=id_number,
#                 error="未查询到该身份证号的征信信息"
#             ).model_dump()
        
#         # 构建征信报告内容列表
#         credit_report = []
        
#         # 添加基本信息
#         credit_report.append(f"用户姓名: {credit_info.get('user_name', '未知')}")
#         credit_report.append(f"联系电话: {credit_info.get('phone_number', '未知')}")
#         credit_report.append(f"征信状态: {'良好' if credit_info.get('credit_status') == 'good' else '不良'}")
#         credit_report.append("--- 信用记录详情 ---")
        
#         # 遍历信用记录
#         for idx, record in enumerate(credit_info.get('credit_records', []), 1):
#             record_type = "信用卡" if record['type'] == 'credit_card' else "贷款"
#             status = "正常" if not record['overdue_records'] else "存在逾期"
            
#             record_str = (f"{idx}. {record_type} - {record['institution']}\n"
#                           f"   起止日期: {record['start_date']} 至 {record['end_date'] or '至今'}\n"
#                           f"   状态: {status}")
#             credit_report.append(record_str)
            
#             # 添加逾期记录详情
#             if record['overdue_records']:
#                 for overdue in record['overdue_records']:
#                     overdue_str = (f"   逾期记录: {overdue['date']}，逾期{overdue['days']}天，"
#                                   f"金额{overdue['amount']}元")
#                     credit_report.append(overdue_str)
        
#         return CreditInfoResult(
#             id_number=id_number,
#             credit_report=credit_report
#         ).model_dump()
        
#     except Exception as e:
#         return CreditInfoResult(
#             id_number=id_number if id_number else "",
#             error=f"查询失败: {str(e)}"
#         ).model_dump()

def create_mock_data(count=20):
    """
    Create mock credit information data
    :param count: Number of data entries to create
    """
    # Mock data templates
    institutions = ["Industrial and Commercial Bank of China", "China Construction Bank", "Bank of China", "China Merchants Bank", "Agricultural Bank of China"]
    mock_users = [
        {"name": "John Doe", "id": "110101199001011234", "phone": "13800138000"},
        {"name": "Jane Smith", "id": "310101199203154567", "phone": "13900139000"},
        {"name": "Michael Johnson", "id": "440101198805207890", "phone": "13700137000"},
        {"name": "Emily Davis", "id": "510101199507252345", "phone": "13600136000"},
        {"name": "David Wilson", "id": "120101199309306789", "phone": "13500135000"},
        {"name": "Sarah Brown", "id": "320101199110158901", "phone": "13400134000"},
        {"name": "James Lee", "id": "430101198902203456", "phone": "13300133000"},
        {"name": "Linda Wang", "id": "520101199404056789", "phone": "13200132000"},
        {"name": "Robert Chen", "id": "130101199606101234", "phone": "13100131000"},
        {"name": "Patricia Zhang", "id": "330101198708155678", "phone": "13000130000"},
        {"name": "John Miller", "id": "450101199709208901", "phone": "18900189000"},
        {"name": "Jennifer Liu", "id": "530101199011252345", "phone": "18800188000"},
        {"name": "William Zhao", "id": "140101198601306789", "phone": "18700187000"},
        {"name": "Elizabeth Zhu", "id": "340101199803051234", "phone": "18600186000"},
        {"name": "Richard Wu", "id": "460101198505104567", "phone": "18500185000"},
        {"name": "Barbara Xu", "id": "540101199907157890", "phone": "18400184000"},
        {"name": "Joseph He", "id": "150101198409202345", "phone": "18300183000"},
        {"name": "Susan Guo", "id": "350101200010256789", "phone": "18200182000"},
        {"name": "Thomas Yang", "id": "470101198312301234", "phone": "18100181000"},
        {"name": "Jessica Huang", "id": "550101199102054567", "phone": "18001800000"}
    ]
    
    for i in range(min(count, len(mock_users))):
        user = mock_users[i]
        # Randomly determine if there are overdue records (30% probability)
        has_overdue = random.random() < 0.3
        credit_status = "bad" if has_overdue else "good"
        
        # Generate 2-3 credit records
        credit_records = []
        record_count = random.randint(2, 3)
        
        for j in range(record_count):
            record_type = "credit_card" if j % 2 == 0 else "loan"
            institution = random.choice(institutions)
            start_year = random.randint(2018, 2022)
            start_month = random.randint(1, 12)
            start_date = f"{start_year}-{start_month:02d}-{random.randint(1, 28):02d}"
            
            end_date = None
            if record_type == "loan":
                end_year = start_year + 5 + random.randint(0, 5)
                end_date = f"{end_year}-{start_month:02d}-{random.randint(1, 28):02d}"
            
            # Generate overdue records
            overdue_records = []
            if has_overdue and random.random() < 0.7:
                overdue_count = random.randint(1, 3)
                for k in range(overdue_count):
                    overdue_year = random.randint(start_year, 2023)
                    overdue_month = random.randint(1, 12)
                    overdue_records.append({
                        "date": f"{overdue_year}-{overdue_month:02d}-{random.randint(1, 28):02d}",
                        "days": random.randint(1, 90),
                        "amount": round(random.uniform(1000, 50000), 2)
                    })
            
            credit_records.append({
                "type": record_type,
                "institution": institution,
                "start_date": start_date,
                "end_date": end_date,
                "overdue_records": overdue_records
            })
        
        # Insert data
        credit_collection.insert_one({
            "id_number": user["id"],
            "user_name": user["name"],
            "phone_number": user["phone"],
            "credit_status": credit_status,
            "credit_records": credit_records,
            "query_time": datetime.utcnow()
        })
    
    print(f"Created {min(count, len(mock_users))} mock credit records")

# 使用示例
if __name__ == "__main__":
    # 创建模拟数据
    create_mock_data()
    
    # 查询示例
    # test_id = "310101199203154567"  # 张三的身份证号
    # result = get_credit_info(test_id)
    
    # if result['error']:
    #     print(f"错误: {result['error']}")
    # else:
    #     print(f"身份证号: {result['id_number']}")
    #     print("征信报告:")
    #     for item in result['credit_report']:
    #         print(f"- {item}")
