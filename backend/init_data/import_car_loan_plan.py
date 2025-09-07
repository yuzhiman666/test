import pymongo
from pymongo import MongoClient
import os
import datetime
import uuid

class CarLoanPlanManager:
    def __init__(self, db_name="Auto_Finance_poc", collection_name="car_loan_plan"):
        """初始化MongoDB连接和集合"""
        try:
            # 连接本地MongoDB，默认端口27017
            self.client = MongoClient('mongodb://localhost:27017/')
            # 获取数据库
            self.db = self.client['Auto_Finance_poc']
            # 获取集合
            self.collection = self.db['car_loan_plan']
            print(f"成功连接到MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            print(f"连接MongoDB失败: {str(e)}")
            raise

if __name__ == "__main__":
    manager = CarLoanPlanManager()

    # 初始化一些 BMW 车贷计划数据
    car_loan_plans = [
        {
            "car_brand": "BMW",
            "car_model": "BMW 3系 320Li",
            "total_price": 320000,  # 总车款（人民币，元）
            "down_payment_ratio_min": 0.2,
            "down_payment_ratio_max": 0.5,
            "loan_plans": [
                {
                    "interest_rate": 0.035,  # 年利率 3.5%
                    "loan_term_months": 36,
                    "repayment_frequency": "monthly"
                },
                {
                    "interest_rate": 0.038,  # 年利率 3.8%
                    "loan_term_months": 60,
                    "repayment_frequency": "monthly"
                }
            ]
        },
        {
            "car_brand": "BMW",
            "car_model": "BMW 5系 530Li",
            "total_price": 480000,
            "down_payment_ratio_min": 0.25,
            "down_payment_ratio_max": 0.5,
            "loan_plans": [
                {
                    "interest_rate": 0.032,
                    "loan_term_months": 36,
                    "repayment_frequency": "monthly"
                },
                {
                    "interest_rate": 0.036,
                    "loan_term_months": 60,
                    "repayment_frequency": "monthly"
                }
            ]
        },
        {
            "car_brand": "BMW",
            "car_model": "BMW X3 xDrive30i",
            "total_price": 420000,
            "down_payment_ratio_min": 0.2,
            "down_payment_ratio_max": 0.5,
            "loan_plans": [
                {
                    "interest_rate": 0.034,
                    "loan_term_months": 36,
                    "repayment_frequency": "monthly"
                },
                {
                    "interest_rate": 0.037,
                    "loan_term_months": 48,
                    "repayment_frequency": "monthly"
                }
            ]
        },
        {
            "car_brand": "BMW",
            "car_model": "BMW X5 xDrive40Li",
            "total_price": 720000,
            "down_payment_ratio_min": 0.3,
            "down_payment_ratio_max": 0.6,
            "loan_plans": [
                {
                    "interest_rate": 0.031,
                    "loan_term_months": 36,
                    "repayment_frequency": "monthly"
                },
                {
                    "interest_rate": 0.034,
                    "loan_term_months": 60,
                    "repayment_frequency": "monthly"
                }
            ]
        }
    ]

    # 插入数据
    try:
        result = manager.collection.insert_many(car_loan_plans)
        print(f"成功插入 {len(result.inserted_ids)} 条BMW车贷计划数据")
    except Exception as e:
        print(f"插入数据失败: {str(e)}")    
    
