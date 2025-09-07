import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

# 加载环境变量
load_dotenv()

# 连接到MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["customer_db"]  # 数据库名称
customers_collection = db["customers"]  # 集合名称

# 示例客户数据
sample_customers = [
    {
        "id": str(ObjectId()),
        "name": "张三",
        "age": 35,
        "idNumber": "110101198801011234",
        "monthlyIncome": 15000,
        "annualIncome": 180000,
        "employmentTenure": 5,
        "employmentPosition": "软件工程师",
        "delinquencies": 0,
        "creditLines": 3,
        "loanAmount": 200000,
        "loanPurpose": "购房",
        "status": "pending",
        "verificationStatus": "待验证"
    },
    {
        "id": str(ObjectId()),
        "name": "李四",
        "age": 28,
        "idNumber": "310101199505055678",
        "monthlyIncome": 8000,
        "annualIncome": 96000,
        "employmentTenure": 2,
        "employmentPosition": "市场营销专员",
        "delinquencies": 1,
        "creditLines": 2,
        "loanAmount": 50000,
        "loanPurpose": "购车",
        "status": "pending",
        "verificationStatus": "部分验证"
    },
    {
        "id": str(ObjectId()),
        "name": "王五",
        "age": 42,
        "idNumber": "440101198110109012",
        "monthlyIncome": 25000,
        "annualIncome": 300000,
        "employmentTenure": 10,
        "employmentPosition": "部门经理",
        "delinquencies": 0,
        "creditLines": 5,
        "loanAmount": 300000,
        "loanPurpose": "创业",
        "status": "approved",
        "verificationStatus": "已验证"
    },
    {
        "id": str(ObjectId()),
        "name": "赵六",
        "age": 25,
        "idNumber": "510101199803034567",
        "monthlyIncome": 6000,
        "annualIncome": 72000,
        "employmentTenure": 1,
        "employmentPosition": "行政助理",
        "delinquencies": 2,
        "creditLines": 1,
        "loanAmount": 30000,
        "loanPurpose": "装修",
        "status": "rejected",
        "verificationStatus": "已验证"
    },
    {
        "id": str(ObjectId()),
        "name": "孙七",
        "age": 38,
        "idNumber": "120101198507078901",
        "monthlyIncome": 18000,
        "annualIncome": 216000,
        "employmentTenure": 8,
        "employmentPosition": "财务主管",
        "delinquencies": 0,
        "creditLines": 4,
        "loanAmount": 150000,
        "loanPurpose": "教育",
        "status": "pending",
        "verificationStatus": "待验证"
    }
]

# 插入数据
try:
    result = customers_collection.insert_many(sample_customers)
    print(f"成功插入 {len(result.inserted_ids)} 条客户数据")
    print("插入的ID列表:", result.inserted_ids)
except Exception as e:
    print(f"插入数据时发生错误: {e}")
    