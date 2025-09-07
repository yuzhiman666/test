import pymongo
from pymongo import MongoClient
from bson import Binary
import os
import datetime
import uuid
import sys
# from utils.path_utils import PROJECT_ROOT
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.append(str(PROJECT_ROOT))

class CarLoanApplicationManager:
    def __init__(self, db_name="Auto_Finance_poc", collection_name="car_loan_applications"):
        """初始化MongoDB连接和集合"""
        try:
            # 连接本地MongoDB，默认端口27017
            self.client = MongoClient('mongodb://localhost:27017/')
            # 获取数据库
            self.db = self.client['Auto_Finance_poc']
            # 获取集合
            self.collection = self.db['car_loan_applications']
            print(f"成功连接到MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            print(f"连接MongoDB失败: {str(e)}")
            raise
    
    def _read_file_as_binary(self, file_path):
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
    
    def _get_file_metadata(self, file_path):
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
    
    def create_application(self, 
                          phone,
                          email,
                          userid,  # 新增参数
                          current_address, 
                          car_brand,
                          car_model,
                          id_card_path, 
                          credit_report_path, 
                          salary_slip_path, 
                          employment_proof_path,
                          repayment_account,
                          loan_info,
                          loan_status):
        """
        创建汽车贷款申请表单并保存到MongoDB
        
        参数:
            phone: 申请人电话号码
            email: 申请人邮箱
            current_address: 申请人当前地址
            car_brand: 汽车品牌
            car_model: 汽车型号
            id_card_path: 身份证图片路径
            credit_report_path: 个人征信报告PDF路径
            salary_slip_path: 工资流水图片路径
            employment_proof_path: 在职证明Word文档路径
            repayment_account: 还款账号信息字典
            loan_info: 贷款信息字典
            loan_status: 贷款处理状况字典
        """
        try:
            # 生成唯一申请编号
            application_id = f"APPL-{uuid.uuid4().hex[:8].upper()}"
            
            # 处理身份证信息
            id_card_binary = self._read_file_as_binary(id_card_path)
            id_card_metadata = self._get_file_metadata(id_card_path)
            id_card_info = {
                "binary_data": id_card_binary,
                **id_card_metadata
            }
            
            # 处理个人征信报告
            credit_report_binary = self._read_file_as_binary(credit_report_path)
            credit_report_metadata = self._get_file_metadata(credit_report_path)
            credit_report_info = {
                "binary_data": credit_report_binary,** credit_report_metadata
            }
            
            # 处理工资流水
            salary_slip_binary = self._read_file_as_binary(salary_slip_path)
            salary_slip_metadata = self._get_file_metadata(salary_slip_path)
            salary_slip_info = {
                "binary_data": salary_slip_binary,
                **salary_slip_metadata
            }
            
            # 处理在职证明
            employment_proof_binary = self._read_file_as_binary(employment_proof_path)
            employment_proof_metadata = self._get_file_metadata(employment_proof_path)
            employment_proof_info = {
                "binary_data": employment_proof_binary,** employment_proof_metadata
            }
            
            # 构建完整的申请表单文档
            application_document = {
                "application_id": application_id,
                "userid": userid,  # 新增
                "phone" : phone,
                "email" : email,
                "current_address" : current_address,
                "car_brand": car_brand,
                "car_model": car_model,
                "id_card": id_card_info,
                "credit_report": credit_report_info,
                "salary_slip": salary_slip_info,
                "employment_proof": employment_proof_info,
                "repayment_account": repayment_account,
                "loan_info": loan_info,
                "loan_status": loan_status,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            
            # 插入文档到集合
            result = self.collection.insert_one(application_document)
            print(f"成功创建贷款申请，ID: {result.inserted_id}")
            print(f"申请编号: {application_id}")
            
            return {
                "success": True,
                "application_id": application_id,
                "mongo_id": str(result.inserted_id)
            }
            
        except Exception as e:
            print(f"创建贷款申请失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# 使用示例
if __name__ == "__main__":
    # 初始化管理器
    manager = CarLoanApplicationManager()   

    # 还款账号
    repayment_account = {
        "account_name": "张三",
        "account_number": "6222021234567890123",
        "bank_name": "中国工商银行北京朝阳支行"
    }
    
    # 贷款信息
    loan_info = {
        "total_price": 200000.0,           # 总车款（车辆价格）
        "down_payment": 50000.0,           # 首付款
        "loan_amount": 150000.0,           # 贷款总额
        "interest_rate": 0.045,            # 贷款利率（4.5%）
        "loan_term_months": 36,            # 贷款期限（月数，这里是36个月 = 3年）
        "start_date": datetime.datetime(2025, 1, 1),# 贷款开始日
        "end_date": datetime.datetime(2027, 12, 31),# 贷款结束日
        "repayment_frequency": "monthly",  # 还款方式（月/月供、季/季供、年/年供）
        "repayment_amount": 4470.0,        # 每期还款额（这里是示例数值）
        "repayment_day": 15                # 每期还款日（每月15号还款）
    }
    
    # 贷款处理状况
    loan_status = {
        # "application_status": "审核中",  #  已提交, 审核中, 已批准, 已拒绝
        # 保持loan_status.application_status的值与前端一致
        "application_status": "草稿",  # 草稿, 已提交, 审核中, 已批准, 已拒绝
        "applicant_name": "张三",
        "applicant_phone": "13800138001",
        "applicant_email": "hfjdash@163.com",
        "application_date": datetime.datetime(2023, 10, 15, 10, 30),
        "reviewer_name": "Jack",
        "reviewer_id": "BMW001",
        "review_date": None,
        "review_result": "",  # 批准, 拒绝  
        "review_comments": ""   
    }
    
    # 从邮箱提取userid
    user_id = "applicant@example.com".split('@')[0]

    # 注意：请替换为实际的文件路径
    result = manager.create_application(
        # 个人信息
        phone = "13800138000",
        email = "applicant@example.com",
        userid = user_id,  # 新增：添加userid参数
        current_address = "北京市朝阳区某某街道123号",
        car_brand= "BMW",          # 汽车品牌
        car_model = "2025款 3.0T 豪华型",
        id_card_path = "./test_data/identity_card.jpg",          # 身份证图片
        credit_report_path = "./test_data/credit_report.pdf",  # 征信报告
        salary_slip_path = "./test_data/salary_flow.jpg",  # 工资流水
        employment_proof_path = "./test_data/incumbency.docx",  # 在职证明
        repayment_account = repayment_account,
        loan_info=loan_info,
        loan_status=loan_status
    )
    
    if result["success"]:
        print("贷款申请创建成功")
    else:
        print(f"贷款申请创建失败: {result['error']}")
