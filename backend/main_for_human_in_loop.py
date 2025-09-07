import base64
import datetime
from bson import ObjectId
from langchain_openai import ChatOpenAI
from workflow.loan_workflow_for_human_in_loop import LoanWorkflow
from langgraph.types import Command
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List  # 保留Dict类型用于多语言
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import uvicorn
import uuid
import sys
# 将项目根目录添加到 Python 搜索路径
from utils.path_utils import PROJECT_ROOT
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
from config.load_key import load_key
from utils.log_config import setup_logger
from fastapi.middleware.cors import CORSMiddleware  # 在后端入口文件顶部导入跨域模块 # update by yan 2025/08/27 start
from typing import Optional, List, Literal

# 初始化日志记录器
logger = setup_logger()

# update by yan 2025/08/27 start
# 初始化FastAPI时，自定义文档路径（可选）
app = FastAPI(
    title="Auto Loan Analysis API",
    description="Auto Loan Analysis system",
    version="1.0.0",
    docs_url="/api-docs",  # 把/docs改成/api-docs，访问地址变成http://localhost:8000/api-docs
    #redoc_url=None,       # 关闭/redoc页面（设为None即可）
    openapi_url="/openapi.json"  # 接口的OpenAPI schema路径（默认，一般不用改）
)

# 新增：跨域配置（允许前端端口访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端运行地址（如React默认3000端口）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法（GET/POST等）
    allow_headers=["*"],  # 允许所有请求头
)

# update by yan 2025/08/27 end

# 连接 MongoDB
try:
    mongoClient = MongoClient("mongodb://localhost:27017")
    mongoDB = mongoClient["Auto_Finance_poc"]
    collection = mongoDB["car_loan_applications"]
    customers_collection = mongoDB["customers"]
    # 新增：连接汽车品牌集合（关键！）
    car_brands_collection = mongoDB["car_brands"]  # update by yan 2025/08/27
    user_collection = mongoDB["user"] # update by WXL@20250901
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")
    logger.info(f"Failed to connect to MongoDB: {e}")
    raise

# 加载API密钥
DASHSCOPE_API_KEY = load_key("DASHSCOPE_API_KEY")
logger.debug("成功加载API密钥")

# 初始化LLM
llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=DASHSCOPE_API_KEY,
    model="qwen-plus",
)
logger.debug(f"初始化LLM模型: qwen-plus")

# 创建工作流
workflow = LoanWorkflow(llm, mongoClient)
graph = workflow.get_graph()
logger.info("贷款工作流初始化完成")

# update by yan 2025/08/27 start
# update by yan 2025/08/27 start
# 个人信息模型
class PersonalInfo(BaseModel):
    fullName: str
    idNumber: str
    phoneNumber: str
    email: str
    address: str
    # 匹配前端的employmentStatus可选值
    employmentStatus: Literal['employed', 'selfEmployed', 'unemployed', 'student']
    monthlyIncome: float
    accountHolderName: str
    accountNumber: str
    bankName: str

# 车辆选择信息模型
class CarSelection(BaseModel):
    carBrand: str
    carModel: str
    carBrandLabel: str
    # 前端是number类型，后端调整为int
    carYear: int
    # 匹配前端的carType可选值
    carType: Literal['sedan', 'suv', 'electric', 'hybrid']
    carPrice: float

# 贷款详情模型
class LoanDetails(BaseModel):
    downPayment: int  # 首付比例（%）
    downPaymentAmount: int  # 首付金额
    loanAmount: int  # 贷款总额
    interestRate: float  # 年利率（%）
    loanTerm: int  # 贷款期限（月）
    loanStartDate: str  # 开始日期
    loanEndDate: str  # 结束日期
    # 匹配前端的repaymentFrequency可选值
    repaymentFrequency: Literal['monthly', 'quarterly', 'yearly']
    monthlyPayment: float  # 每期还款额
    repaymentDate: int  # 每期还款日（如每月5日）
    # 匹配前端的repaymentMethod可选值
    repaymentMethod: Literal['equalPrincipalInterest', 'equalPrincipal']

# 文档信息模型
class Document(BaseModel):
    id: str
    name: str
    type: str  # 文档类型
    url: str  # 文档存储路径或URL

# 文档集合模型（匹配前端的DocumentSet）
class DocumentSet(BaseModel):
    idCard: Optional[Document] = None         # 身份证
    creditReport: Optional[Document] = None   # 个人征信报告
    salarySlip: Optional[Document] = None     # 工资流水
    employmentProof: Optional[Document] = None # 在职证明

# 主模型：贷款申请
class LoanApplication(BaseModel):
    _id:Optional[str] = None
    applicationId: Optional[str] = None
    # 前端是userId，后端调整为驼峰命名
    userId: str
    # 匹配前端的status可选值
    status: Literal['Submitted', 'InReview', 'Approved', 'Rejected', 'Draft','contract_completed']
    personalInfo: PersonalInfo
    carSelection: CarSelection
    loanDetails: LoanDetails
    documents: DocumentSet
    aiSuggestion: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

# 多语言字段模型（新增价格列表模型）
class MultiLanguageStr(BaseModel):
    zh: str
    en: str
    ja: str

class MultiLanguageList(BaseModel):
    zh: List[str]
    en: List[str]
    ja: List[str]

# 新增：多语言价格模型（数值列表）
class MultiLanguagePrice(BaseModel):
    zh: List[float]  # 中文环境下的价格（元）
    en: List[float]  # 英文环境下的价格（元，保持数值一致）
    ja: List[float]  # 日文环境下的价格（元，保持数值一致）

# 新增：汽车品牌Pydantic模型（关键！）# 宝马汽车模型（适配价格字段）
class CarBrand(BaseModel):
    id: str  # 对应MongoDB的_id（转换为字符串）
    name: MultiLanguageStr
    country: MultiLanguageStr
    series: MultiLanguageList
    price: MultiLanguagePrice  # 新增价格字段
    created_at: str

    class Config:
        from_attributes = True  # 允许从MongoDB文档转换为模型

# update by yan 2025/08/27 end

# Customer接口定义
class Customer(BaseModel):
    id: str
    name: str
    age: int
    idNumber: str
    monthlyIncome: float
    annualIncome: float
    employmentTenure: float
    employmentPosition: str
    delinquencies: int
    creditLines: int
    loanAmount: float
    loanPurpose: str
    status: str
    verificationStatus: str

    class Config:
        from_attributes = True  # 允许从MongoDB文档转换为模型

# start-workflow接口定义
class StartRequest(BaseModel):
    application_id: str

# Approve接口定义
class LoanApprovalRequest(BaseModel):
    application_id: str
    thread_id: str
    human_reult: str
    feedback: Optional[str] = ""

# 定义loan-workflow的start API端点
@app.post('/loan-start')
def loanStart(request: StartRequest):
    # 记录API请求开始
    logger.info("=== 贷款申请API请求开始 ===")
    try:
        # 为检查点提供必要的配置信息
        thread_id = str(uuid.uuid4())
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        logger.info(f"启动贷款申请流程，thread_id={thread_id}")

        # 根据App-ID从mongoDB中取得贷款申请信息
        query = {"application_id": request.application_id}
        document = collection.find_one(query)
        if document:
            # 将 _id（ObjectId）转为字符串
            document["_id"] = str(document["_id"])
            print(f"找到匹配的文档: {request.application_id}")
            logger.info(f"获取到application_id={request.application_id}贷款申请信息")
        else:
            print(f"未找到application_id为{request.application_id}的文档")
            logger.info(f"application_id={request.application_id}贷款申请信息不存在")
            raise HTTPException(status_code=404, detail="贷款申请信息不存在")
        
        # 将MongoDB获取的文档放入初始状态
        initial_state = {
            "raw_data": document,
            "thread_id": thread_id
        }
        result = None
        
        # 处理流程，使用包含thread_id的配置
        for event in graph.stream(initial_state, config):
            for node, value in event.items():
                logger.info(f"进入处理节点: node={node}")
                print(f"\n处理节点: {node}")
                # 检查是否是中断节点
                if node == "__interrupt__":
                    logger.warning(f"节点{node}触发人工审核中断")
                    # 处理中断情况，提取中断信息
                    print("\n需要人工审核:")
                    print(f"\n处理节点value: {value}")
                    # 安全解析中断数据
                    interrupt_data = value[0]
                    value_data = interrupt_data.value
                    print(f"\nvalue_data: {value_data}")
                    thread_id = value_data["thread_id"]
                    print(f"\nthread_id: {thread_id}")
                    try:
                        # 筛选要更新的文档（通过application_id定位）
                        query_filter = {"application_id": value_data["application_id"]}
                        # 记录审核数据-更新项目
                        fields_to_update = {
                            "data_collection_status": value_data["data_collection_status"],
                            "credit_rating_result": value_data["credit_rating_result"],
                            "fraud_detection_status": value_data["fraud_detection_status"],
                            "fraud_detection_result": value_data["fraud_detection_result"],
                            "compliance_check_status": value_data["compliance_check_status"],
                            "compliance_result": value_data["compliance_result"],
                            "decision_result": value_data["decision_result"],
                            "thread_id": thread_id,
                            "status": "waiting_for_human_review"
                        }
                        # 使用$set操作符追加字段（若字段已存在，会覆盖旧值；若不存在，新增字段）
                        update_operation = {"$set": fields_to_update}
                        # 将结果更新到MongoDB
                        result = collection.update_one(query_filter, update_operation)
                        print(f"数据更新成功，更新的文档ID为: {value_data['application_id']}")
                        
                        # 返回审核请求结果
                        return {
                            "status": result.acknowledged and "success" or "failure",
                            "thread_id": thread_id
                        }
                    except KeyError as e:
                        # 处理value_data中缺少字段的情况
                        raise ValueError(f"value_data中缺少必要字段: {str(e)}") from e
                    except ValueError as e:
                        # 处理业务逻辑错误（如未找到文档、缺少字段等）
                        raise
                    except Exception as e:
                        # 处理MongoDB操作相关错误
                        raise Exception(f"更新MongoDB数据失败: {str(e)}") from e
                else:
                    result = value
                    # 安全地获取状态信息，处理可能的元组类型
                    if isinstance(result, dict):
                        if node == "fraud_detection":
                            status = result.get("fraud_detection_status", "未知")
                        elif node == "credit_rating":
                            status = f"credit_rating: {result.get('credit_rating_result', {}).get('score', '未知')}"
                        elif node == "compliance_check":
                            status = result.get("compliance_check_status", "未知")
                        else:
                            status = result.get("status", "未知")
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
                    elif isinstance(result, tuple):
                        if len(result) > 1 and isinstance(result[1], dict):
                            status = result[1].get("status", "未知")
                        elif len(result) > 0:
                            status = str(result[0])
                        else:
                            status = "空结果"
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
                    else:
                        status = str(result)
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
        
    except Exception as e:
        logger.error(f"贷款申请流程处理失败: {str(e)}", exc_info=True)
        raise  # 重新抛出异常让FastAPI处理

# 定义loan-workflow的resume API端点
@app.post('/loan-approve')
def loanApprove(request: LoanApprovalRequest):
    # 记录API请求开始
    logger.info("=== 贷款申请resume API请求开始 ===")
    try:
        # 为检查点提供必要的配置信息
        config = {
            "configurable": {
                "thread_id": request.thread_id
                }
        }
        logger.info(f"resume工作流处理，thread_id={request.thread_id}")
        print("=== resume贷款申请流程 ===")
        
        # 根据用户输入创建继续命令
        response_result = {
                "human_approval_status": request.human_reult.lower(),
                "feedback": request.feedback
        }

        # 执行恢复流程
        result = None
        logger.info(f"thread_id={request.thread_id},人工审核结果:{request.human_reult.lower()}")
        
        # 处理流程，使用包含thread_id的配置
        for event in graph.stream(Command(resume=response_result), config):
            for node, value in event.items():
                logger.info(f"进入处理节点: node={node}")
                print(f"\n处理节点: {node}")
                result = value
                # contract的interrupt时，进行数据存储
                if node == "contract_completed":
                    print(f"contract_completed node::: {node}")
                    # 修正：通过 application_id 更新 MongoDB
                    query_filter = {"application_id": request.application_id}
                    update_operation = {
                        "$set": {
                            "loan_structuring_status": value["loan_structuring_status"],
                            "loan_structuring_result": value["loan_structuring_result"],
                            "contract_generation_status": value["contract_generation_status"],
                            "contract_generation_result": value["contract_generation_result"],
                            "contract_review_status": value["contract_review_status"],
                            "contract_review_result": value["contract_review_result"],
                            "contract_modify_status": value["contract_modify_status"],
                            "contract_modify_result": value["contract_modify_result"],
                            "contract_file_name": value["contract_file_name"],
                            "contract_file_type": value["contract_file_type"],
                            "contract_binary_data": value["contract_binary_data"],
                            "status": value["status"]
                        }
                    }
                    mongo_result = collection.update_one(query_filter, update_operation)
                    if mongo_result.modified_count > 0:
                        logger.info(f"MongoDB更新成功，application_id={request.application_id}")
                    else:
                        logger.warning(f"未找到申请记录，application_id={request.application_id}")

                    return {"status": "success", "thread_id": request.thread_id, "result": str(result)}
                else:
                    result = value
                    # 安全地获取状态信息，处理可能的元组类型
                    if isinstance(result, dict):
                        if node == "human_review":
                            status = result.get("human_approval_status", "未知")
                        else:
                            status = result.get("status", "未知")
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
                    elif isinstance(result, tuple):
                        if len(result) > 1 and isinstance(result[1], dict):
                            status = result[1].get("status", "未知")
                        elif len(result) > 0:
                            status = str(result[0])
                        else:
                            status = "空结果"
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
                    else:
                        status = str(result)
                        logger.info(f"节点{node}处理完成，状态: {status}")
                        print("状态:", status)
        
    except Exception as e:
        logger.error(f"贷款申请流程处理失败: {str(e)}", exc_info=True)
        raise  # 重新抛出异常让FastAPI处理

# API路由
@app.get("/customers/pending", response_model=List[Customer], status_code=status.HTTP_200_OK)
async def get_pending_customers():
    """获取所有状态为pending的客户数据"""
    try:
        pending_customers = list(customers_collection.find({"status": "pending"}))
        # 转换MongoDB的ObjectId为字符串（如果需要）
        for customer in pending_customers:
            if "_id" in customer:
                customer["id"] = str(customer["_id"])
                del customer["_id"]
        return pending_customers
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/customers/pending/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def get_pending_customer(customer_id: str):
    """根据ID获取特定的pending状态客户数据"""
    try:
        customer = customers_collection.find_one({"id": customer_id, "status": "pending"})
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pending customer with ID {customer_id} not found"
            )
        
        # 处理MongoDB的ObjectId
        if "_id" in customer:
            del customer["_id"]
            
        return customer
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# update by yan 2025/08/27 start
# 新增：获取所有汽车品牌接口（关键！前端将调用此接口）
@app.get("/api/car-brands", response_model=List[CarBrand], status_code=status.HTTP_200_OK)
async def get_car_brands():
    """
    从MongoDB获取所有汽车品牌信息
    返回格式：[{id: "xxx", name: "奔驰", country: "德国", series: ["S级",...],...},...]
    """
    try:
        # 1. 从MongoDB查询所有品牌数据（find()无参数表示查询全部）
        brand_documents = list(car_brands_collection.find())
        
        # 2. 处理MongoDB的ObjectId：转换为字符串（前端无法解析ObjectId）
        for brand in brand_documents:
            brand["id"] = str(brand["_id"])  # 将ObjectId转为字符串，赋值给id字段
            del brand["_id"]  # 删除原始的_id字段（避免前端解析错误）
        
        # 3. 返回处理后的数据（自动符合CarBrand模型格式）
        return brand_documents
    
    # 4. 异常处理：数据库查询失败时返回500错误
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch car brands from MongoDB: {str(e)}"
        )

# 调整：根据多语言名称查询品牌
@app.get("/api/car-models", status_code=status.HTTP_200_OK)
async def get_car_models(brand: str, lang: str = "zh"):
    """根据品牌多语言名称获取车型（支持中文/英文/日文）"""
    try:
        # 构建查询条件：匹配对应语言的品牌名称（如lang=zh时查询name.zh）
        query = {f"name.{lang}": brand}
        car_brand = car_brands_collection.find_one(query)
        if not car_brand:
            return []
        
        # 返回对应语言的车型列表（如lang=en时返回series.en）
        return car_brand.get("series", {}).get(lang, [])
    
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch car models: {str(e)}"
        )

# 价格查询接口补充语言参数
@app.get("/api/car-price", status_code=status.HTTP_200_OK)
async def get_car_price(brand: str, model: str, lang: str = "zh"):
    """根据品牌、车型和语言获取价格"""
    try:
        # 按语言查询品牌
        # car_brand = car_brands_collection.find_one({f"name.{lang}": brand})
        car_brand = car_brands_collection.find_one({"_id": ObjectId(brand)})  # 需要导入ObjectId
        if not car_brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # 匹配对应语言的车型和价格
        series_list = car_brand["series"][lang]
        model_index = series_list.index(model)
        return car_brand["price"][lang][model_index]
    
    except ValueError:
        raise HTTPException(status_code=404, detail="Model not found for the brand")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch car price: {str(e)}"
        )

# 在现有路由下方新增
@app.post('/api/loan-application')
def create_loan_application(application: LoanApplication):
    """创建或更新贷款申请"""
    try:
        # 处理documents字段转换
        documents_dict = {}
        if application.documents.idCard:
            documents_dict["idCard"] = application.documents.idCard.model_dump()
        if application.documents.creditReport:
            documents_dict["creditReport"] = application.documents.creditReport.model_dump()
        if application.documents.salarySlip:
            documents_dict["salarySlip"] = application.documents.salarySlip.model_dump()
        if application.documents.employmentProof:
            documents_dict["employmentProof"] = application.documents.employmentProof.model_dump()
        
        # 构建文档数据
        doc_data = {
            "user_id": application.userId,
            "status": application.status,
            "personal_info": application.personalInfo.model_dump(),
            "car_selection": application.carSelection.model_dump(),
            "loan_details": application.loanDetails.model_dump(),
            "documents": documents_dict,
            "ai_suggestion":application.aiSuggestion,
            "updated_at": datetime.datetime.now()
        }
        
        # 检查是否有applicationId，决定执行更新还是创建操作
        if application.applicationId and application.applicationId.strip():
            # 执行更新操作
            result = collection.update_one(
                {"application_id": application.applicationId},
                {"$set": doc_data}
            )
            
            if result.modified_count == 1:
                return {"success": True, "message": "贷款申请已更新", "application_id": application.applicationId}
            elif result.matched_count == 0:
                return {"success": False, "message": f"未找到ID为{application.applicationId}的贷款申请"}
            else:
                return {"success": False, "message": "更新操作未成功执行"}
        else:
            # 生成唯一申请ID，执行创建操作
            application_id = f"APPL-{uuid.uuid4().hex[:8].upper()}"
            doc_data["application_id"] = application_id
            doc_data["created_at"] = datetime.datetime.now()
            
            result = collection.insert_one(doc_data)
            return {"success": True, "application_id": application_id, "id": str(result.inserted_id)}
            
    except Exception as e:
        logger.error(f"处理贷款申请失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/loan-application/{app_id}')
def get_loan_application(app_id: str):
    """获取贷款申请详情"""
    doc = collection.find_one({"application_id": app_id})
    if not doc:
        raise HTTPException(status_code=404, detail="申请不存在")
    doc["_id"] = str(doc["_id"])
    return doc

@app.get('/api/loan-application/{application_id}/ai-suggestion')
def get_ai_suggestion(application_id: str):
    """获取贷款申请的AI建议"""
    try:
        # 查询申请数据
        doc = collection.find_one({"application_id": application_id})
        if not doc:
            raise HTTPException(status_code=404, detail="申请不存在")
        
        # 调用LLM生成建议
        prompt = f"""基于以下贷款申请信息，生成审批建议：
        个人信息：{doc.get('personal_info')}
        车辆信息：{doc.get('car_selection')}
        贷款信息：{doc.get('loan_details')}
        """
        response = llm.predict(prompt)
        
        return {"analysis": response}
    except Exception as e:
        logger.error(f"生成AI建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 示例：获取当前用户的贷款申请
@app.get("/api/loan-application/my", status_code=status.HTTP_200_OK)
async def get_my_loan_applications():
    try:
        # 实际逻辑需根据用户认证获取当前用户的申请
        my_applications = list(collection.find({"application_id": "APPL-88ADD60F"}))  # 伪代码
        for app in my_applications:
            app["id"] = str(app["_id"])
            del app["_id"]
        return my_applications
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch my loan applications: {str(e)}"
        )
# update by yan 2025/08/27 end
# update by WXL@20250901 Start
# 请求模型 - 定义登录时需要的参数
class LoginRequest(BaseModel):
    identifier: str
    password: str
    role: str

# 用户信息子模型（对应前端的user对象）
class UserInfo(BaseModel):
    id: str
    username: str  # 确保不为None，与前端保持一致
    email: str
    role: str  # 限定为'customer'或'admin'，与前端保持一致

# 登录响应主模型（完全匹配前端的LoginResponse）
class LoginResponse(BaseModel):
    user: UserInfo  # 嵌套用户信息对象
    token: str  # 令牌字符串

# 定义欺诈检测结果子模型（包含suspicious_items）
class FraudDetectionResult(BaseModel):
    is_suspicious: bool
    suspicious_items: List[str]  # 对应截图中的字符串数组
    confidence: float
    recommendation: str

class AdminLoanApplicationDetail(LoanApplication):
    """管理员视图的贷款申请详情模型，扩展额外字段"""
    compliance_check_status: Optional[str] = None
    compliance_result: Optional[str] = None
    data_collection_status: Optional[str] = None
    fraud_detection_status: Optional[str] = None
    fraud_detection_result: Optional[FraudDetectionResult] = None  # 嵌套子模型

    # 可以根据实际用户信息添加其他字段，如name, age等
@app.post("/api/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(login_data: LoginRequest):
    """
    用户登录接口
    
    通过email和password验证用户身份，
    验证成功后返回用户信息（不包含密码）
    """
    print(login_data)
    try:
        # 从数据库查询用户
        user = user_collection.find_one({
            "email": login_data.identifier,
            "password": login_data.password,  # 注意：实际应用中应使用加密存储和验证
            "role": login_data.role
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码不正确"
            )
        
        # 构造返回数据，转换ObjectId为字符串
        # 2. 构造用户信息对象（确保字段匹配）
        user_info = UserInfo(
            id=str(user["_id"]),
            username=user.get("username") or "",  # 确保不为None
            email=user["email"],
            role=user.get("role") or "customer"  # 默认为customer
        )
        
        # 3. 生成令牌（实际项目中使用JWT等生成）
        if user_info.role == "customer":
            token = "customer-token-123"
        else:
            token = "admin-token-123"
        
        # 4. 返回匹配前端的结构
        return {"user": user_info, "token": token}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )
    
@app.get('/api/admin/loan-applications')
def get_all_loan_applications():
    """获取所有贷款申请，仅返回指定字段"""
    try:
        # 查询条件：仅返回状态为"InReview"的申请
        query = {"status": "contract_completed"}
        # 查询所有贷款申请，仅返回需要的字段
        # 投影设置：1表示返回，0表示不返回；排除_id，只保留指定字段
        projection = {
            "application_id": 1,
            "personal_info.fullName": 1,
            "updated_at": 1,
            "status": 1,
            "_id": 0  # 不返回_id字段
        }
        
        # 查询所有文档，按更新时间降序排序
        applications = collection.find(
            query,  # 查询条件：空表示所有文档
            projection
        ).sort("updated_at", -1)  # 按更新时间倒序，最新的在前
        
        # 处理查询结果
        result = []
        for app in applications:
            # 提取嵌套的fullName（处理可能的缺失情况）
            full_name = app.get("personal_info", {}).get("fullName", "")
            
            # 处理updated_at为datetime对象的情况，转换为ISO格式字符串
            updated_at = app.get("updated_at")
            if isinstance(updated_at, datetime.datetime):
                updated_at = updated_at.isoformat()
            
            # 构造返回字段字典
            result.append({
                "application_id": app.get("application_id", ""),
                "fullName": full_name,
                "updated_at": updated_at,
                "status": app.get("status", "")
            })
        
        return result
    
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取贷款申请失败: {str(e)}"
        )

@app.get('/api/admin/loan-applications/{application_id}',response_model=AdminLoanApplicationDetail)
def get_loan_application_details(application_id: str):
    """获取单个贷款申请的详细信息（管理员视图）"""
    # 尝试通过application_id查询
    application = collection.find_one({"application_id": application_id})
    
    # 如果找不到，尝试通过ObjectId查询
    if not application and ObjectId.is_valid(application_id):
        application = collection.find_one({"_id": ObjectId(application_id)})
    
    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # 3. 数据转换和字段映射（关键修改点）
    # 转换ObjectId为字符串
    application_id_str = str(application["_id"])
    
    # 处理日期字段
    def format_date(date_obj):
        if isinstance(date_obj, datetime.datetime):
            return date_obj.isoformat()
        elif isinstance(date_obj, dict) and "$date" in date_obj:
            return datetime.datetime.fromtimestamp(date_obj["$date"] / 1000).isoformat()
        return str(date_obj)
    
    # 4. 构建符合AdminLoanApplicationDetail模型的响应数据
    response_data = {
        "_id": application_id_str,
        "applicationId": application.get("application_id"),
        "userId": application.get("user_id"),
        "status": application.get("status"),
        "personalInfo": application.get("personal_info", {}),
        "carSelection": application.get("car_selection", {}),
        "loanDetails": application.get("loan_details", {}),
        "documents": application.get("documents", {}),
        "aiSuggestion": application.get("ai_suggestion"),
        "createdAt": format_date(application.get("created_at")),
        "updatedAt": format_date(application.get("updated_at")),
        "compliance_check_status":application.get("compliance_check_status"),
        "compliance_result":application.get("compliance_result"),
        "data_collection_status":application.get("data_collection_status"),
        "fraud_detection_status":application.get("fraud_detection_status"),
        "fraud_detection_result": {
            "is_suspicious": application.get("fraud_detection_result", {}).get("is_suspicious", False),
            # 关键：通过嵌套路径获取suspicious_items，默认空数组
            "suspicious_items": application.get("fraud_detection_result", {}).get("suspicious_items", []),
            "confidence": application.get("fraud_detection_result", {}).get("confidence", 0.0),
            "recommendation": application.get("fraud_detection_result", {}).get("recommendation", "")
        }

        # "internalNotes": application.get("internal_notes"),
        # "reviewHistory": application.get("review_history"),
        # "riskScore": application.get("risk_score"),
        # "documentVerificationStatus": doc_verification_status
    }
    
    return response_data
# update by WXL@20250901 End

# 主函数启动
if __name__ == "__main__":
    logger.info("启动贷款分析API服务")
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)