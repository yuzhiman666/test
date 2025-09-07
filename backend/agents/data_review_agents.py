from agents.state import LoanApplicationState
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
import agents.tools
from dotenv import load_dotenv

# 信用评级Agent
class CreditRatingAgent:
    @staticmethod
    def process(state: LoanApplicationState) -> Dict[str, Any]:
        """信用评级处理"""
        temp_path = "temp_个人信用报告.pdf"
        try:
            pdf_bytes = state["creditInfo"]
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)
            result = agents.tools.credit_rating_from_pdf(temp_path)
            print(f"-----credit_rating_result: {result.get('credit_rating')}-----")
            return {
                "credit_rating_result": result["credit_rating"]
            }
        except Exception as e:
            error_msg = str(e)
            print(f"信用评级处理出错: {error_msg}")
        finally:
            # 确保临时文件被删除
            import os
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    print(f"临时文件已删除: {temp_path}")
                except OSError as e:
                    print(f"删除临时文件失败: {str(e)}")
    
# 合规检查Agent
class ComplianceAgent:
    """合规检查Agent，负责检查申请是否符合相关法规"""   
    def __init__(self, redis_vector_store, llm: BaseChatModel):
        load_dotenv()
        self.redis_vector_store = redis_vector_store
        self.llm = llm

    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """处理合规检查流程"""
        try:
            # 构建查询 - 优化：移除与法规检索无关的个人信息，聚焦检查要点
            query = (f"汽车贷款审核，需检查以下要点：首付比例要求、贷款期限规定、"
                    f"收入还款比限制、贷款人资格条件")
            
            # 搜索相关法规
            try:
                regulations = agents.tools.search_regulations(self.redis_vector_store, query)
                print(f"-----regulations已取到-----")
                # 检查法规搜索结果是否有效
                if not regulations or len(regulations) == 0:
                    raise ValueError("未检索到相关法规信息")
            except Exception as e:
                error_msg = f"法规检索失败: {str(e)}"
                print(f"-----法规检索出错: {error_msg}-----")
                
            # 调用通义千问大模型分析合规性
            try:
                prompt = PromptTemplate(
                template="""你是一名汽车贷款资格审核师，请根据《汽车贷款管理办法》及相关法规，判断以下申请人信息是否合规：
                    申请人信息：身份证号{id}，姓名{name}，月薪{income}元，工作单位{company}
                    法规条款：{regulations}
                    请先明确回答"合规"或"不合规"，再简要说明原因（100字以内）。
                    回答格式：
                    结论：[合规/不合规]
                    原因：[简要说明]""",
                    input_variables=["id", "name", "income", "company", "regulations"]
                )

                chain = prompt | self.llm
                try:
                    compliance_result = chain.invoke({
                        "id": state["idNumber"],
                        "name": state["fullName"],
                        "income": state["monthlyIncome"],
                        "company": state["companyName"],
                        "regulations": "\n".join(regulations)
                    })
                    print(f"-----compliance_result:{compliance_result.content}---------")
                except Exception as e:
                    print(f"模型调用失败: {str(e)}")
                    compliance_result = None
            except Exception as e:
                error_msg = f"结果解析失败: {str(e)}"
                print(f"-----结果解析出错: {error_msg}-----")
                
            # 解析合规状态
            try:
                result_content = compliance_result.content
                compliance_check_status = "rejected"  # 默认不合规
                # 提取结论（优先匹配明确结论）
                if "结论：合规" in result_content:
                    compliance_check_status = "approved"
                elif "结论：不合规" in result_content:
                    compliance_check_status = "rejected"
                #  fallback：通过关键词辅助判断
                elif "符合规定" in result_content or "合规" in result_content:
                    compliance_check_status = "approved"
                elif "不符合" in result_content or "违规" in result_content:
                    compliance_check_status = "rejected"
                print(f"-----compliance_check_status: {compliance_check_status}-----")
            except Exception as e:
                error_msg = f"结果解析失败: {str(e)}"
                print(f"-----结果解析出错: {error_msg}-----")
                
            # 整理返回结果
            regulations.append(f"合规性分析：{result_content}")

            return {
                "compliance_result": compliance_result.content,
                "compliance_check_status": compliance_check_status
            }
        # 捕获所有未处理的异常
        except Exception as e:
            error_msg = f"合规检查流程发生未预期错误: {str(e)}"
            print(f"-----合规检查流程出错: {error_msg}-----")

# 反欺诈Agent
class FraudDetectionAgent:
    """反欺诈Agent，负责检测申请中的欺诈风险"""
    def __init__(self, llm: BaseChatModel, mongo_client):
        self.mongo_client=mongo_client
    
    def process(self, state: LoanApplicationState) -> Dict[str, Any]:
        """处理反欺诈检测流程"""
        suspicious_items = []
        total_risk = 0.0
        
        # 1. 身份信息验证
        try:
            id_suspicious, id_reason = agents.tools.check_id_integrity(
                state["idNumber"], state["fullName"]
            )
            if id_suspicious:
                suspicious_items.append(f"身份信息验证：{id_reason}")
                total_risk += 0.25
            else:
                suspicious_items.append(f"身份信息验证：{id_reason}")
            print(f"------身份信息验证完成-------")
        except Exception as e:
            error_msg = f"身份信息验证失败：系统错误 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.35  # 验证失败分配较高风险
            print(f"------身份信息验证出错：{str(e)}-------")

        # 2. 收入真实性验证
        try:
            income_suspicious, income_reason = agents.tools.verify_income_authenticity(
                state["monthlyIncome"], state["salary"], state["companyName"]
            )
            if income_suspicious:
                suspicious_items.append(f"收入真实性：{income_reason}")
                total_risk += 0.30
            else:
                suspicious_items.append(f"收入真实性：{income_reason}")
            print(f"------收入真实性验证完成-------")
        except KeyError as e:
            error_msg = f"收入真实性验证失败：缺少必要信息 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.40
            print(f"------收入真实性验证出错：{str(e)}-------")
        except Exception as e:
            error_msg = f"收入真实性验证失败：系统错误 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.40
            print(f"------收入真实性验证出错：{str(e)}-------")
        
        # 3. 异常交易检测
        try:
            transaction_suspicious, transaction_reason = agents.tools.detect_abnormal_transactions(
                state["salary"]
            )
            if transaction_suspicious:
                suspicious_items.append(f"异常交易：{transaction_reason}")
                total_risk += 0.20
            else:
                suspicious_items.append(f"异常交易：{transaction_reason}")
            print(f"------异常交易验证完成-------")
        except Exception as e:
            error_msg = f"异常交易检测失败：系统错误 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.30
            print(f"------异常交易验证出错：{str(e)}-------")

        # 4. 黑名单检查（从state获取数据）
        try:
            blacklist_suspicious, blacklist_reason = agents.tools.check_blacklist_from_mongo(
                self.mongo_client,  # 传入MongoDB客户端实例
                state["idNumber"]   # 传入身份证号
            )
            if blacklist_suspicious:
                suspicious_items.append(f"黑名单检查：{blacklist_reason}")
                total_risk += 0.10
            else:
                suspicious_items.append(f"黑名单检查：{blacklist_reason}")
            print(f"------黑名单验证完成-------")
        except ConnectionError as e:
            error_msg = f"黑名单检查失败：数据库连接错误 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.35
            print(f"------黑名单验证出错：{str(e)}-------")
        except Exception as e:
            error_msg = f"黑名单检查失败：系统错误 - {str(e)}"
            suspicious_items.append(error_msg)
            total_risk += 0.35
            print(f"------黑名单验证出错：{str(e)}-------")
        
        #5. 反欺诈结果计算
        try:
            # 计算置信度和建议
            confidence = min(1.0, total_risk)
            if confidence < 0.3:
                recommendation = "通过自动审核"
                fraud_detection_status = "approved"  # 低风险通过
            elif confidence < 0.7:
                recommendation = "需要人工复核"
                fraud_detection_status = "human_review"  # 需人工复核
            else:
                recommendation = "拒绝申请"
                fraud_detection_status = "rejected"  # 高风险拒绝
        
            # 构建反欺诈结果字典
            fraud_detection_result = {
                "is_suspicious": confidence >= 0.3,
                "suspicious_items": suspicious_items,
                "confidence": confidence,
                "recommendation": recommendation
            }
            print(f"反欺诈结果： {fraud_detection_result}")
            print(f"反欺诈status:  {fraud_detection_status}")
            # 按要求返回包含状态和结果的字典
            return {
                "fraud_detection_status": fraud_detection_status,
                "fraud_detection_result": fraud_detection_result,
            }
        except Exception as e:
            print(f"生成结果时出错：{str(e)}")
