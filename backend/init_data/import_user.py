import pymongo
from pymongo import MongoClient
import os
import datetime
import uuid

class UserManager:
    def __init__(self, db_name="Auto_Finance_poc", collection_name="user"):
        """初始化MongoDB连接和集合"""
        try:
            # 连接本地MongoDB，默认端口27017
            self.client = MongoClient('mongodb://localhost:27017/')
            # 获取数据库
            self.db = self.client['Auto_Finance_poc']
            # 获取集合
            self.collection = self.db['user']
            print(f"成功连接到MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            print(f"连接MongoDB失败: {str(e)}")
            raise

if __name__ == "__main__":
    manager = UserManager() # 该类默认使用"user"集合
    # 初始化用户表并插入用户，使用与UserManager一致的集合
    users_collection = manager.collection  # 使用正确的集合名称
    # 初始化用户表（users collection）并插入一个普通用户和一个管理员
    # users_collection = manager.db["users"]

    now = datetime.datetime.utcnow()

    sample_users = [
        {  
            "username": "test_user",
            "password": "user123",   #  实际使用时建议存储hash
            "phone": "13800000001",
            "email": "user@gmail.com", # 与前端默认登录邮箱一致
            "userid": "user@gmail.com".split('@')[0],  # 新增：从邮箱提取userid
            "role": "user",
            "status": "active",
            "first_login_at": now,
            "last_login_at": now,
            "last_login_ip": "127.0.0.1",
            "login_count": 1,
            "prefer_language": "zh-CN", # 确保有默认语言设置，解决国际化问题
            "created_at": now,
            "updated_at": now
        },
        {
            "username": "admin_user",
            "password": "admin123",  #  实际使用时建议存储hash
            "phone": "13800000002",
            "email": "admin@gmail.com",
            "userid": "admin@gmail.com".split('@')[0],  # 新增：从邮箱提取userid
            "role": "admin",
            "status": "active",
            "first_login_at": now,
            "last_login_at": now,
            "last_login_ip": "127.0.0.1",
            "login_count": 1,
            "prefer_language": "en-US",
            "created_at": now,
            "updated_at": now
        }
    ]

    # 插入数据前清理旧数据，避免重复
    # users_collection.delete_many({})
    result = users_collection.insert_many(sample_users)
    print(f"成功插入 {len(result.inserted_ids)} 个用户到 users 表")