from langchain_openai import ChatOpenAI
from workflow.loan_workflow import LoanWorkflow
from langgraph.types import Command
from fastapi import FastAPI
import uvicorn
import sys
from utils.path_utils import PROJECT_ROOT
# 将项目根目录添加到 Python 搜索路径
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
from config.load_key import load_key
from utils.log_config import setup_logger
# 初始化日志记录器
logger = setup_logger()

app = FastAPI(
    title="Auto Loan Analysis API",
    description="Auto Loan Analysis system",
    version="1.0.0"
)

# 定义一个简单的API端点
@app.get('/loan')
def loan():
    # 记录API请求开始
    logger.info("=== 贷款申请API请求开始 ===")

    try:
        # 加载API密钥并初始化LLM
        DASHSCOPE_API_KEY = load_key("DASHSCOPE_API_KEY")
        logger.debug("成功加载API密钥")

        llm = ChatOpenAI(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=DASHSCOPE_API_KEY,
            model="qwen-plus",
        )
        logger.debug(f"初始化LLM模型: qwen-plus")
        
        # 创建工作流
        workflow = LoanWorkflow(llm)
        graph = workflow.get_graph()
        logger.info("贷款工作流初始化完成")
        
        # 示例用户数据
        user_data = {
            "user_id": "user_12345",
            "raw_data": {
                "applicant": {
                    "name": "张三",
                    "age": 35,
                    "id_number": "1101011989XXXXXXXX"
                },
                "income": {
                    "data": {
                        "monthly_income": 15000,
                        "annual_income": 180000
                    },
                    "verification_status": "verified"
                },
                "employment": {
                    "data": {
                        "tenure": 5,
                        "position": "工程师"
                    }
                },
                "credit_history": {
                    "data": {
                        "delinquencies": 0,
                        "credit_lines": 3
                    }
                },
                "loan_details": {
                    "amount": 300000,
                    "purpose": "housing"
                }
            },
            "status": "started"
        }
        logger.info(f"加载用户数据: user_id={user_data['user_id']}")

        # 为检查点提供必要的配置信息
        thread_id = "loan_application_123"
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        logger.info(f"启动工作流处理，thread_id={thread_id}")

        print("=== 启动贷款申请流程 ===")
        result = None
        
        # 处理流程，使用包含thread_id的配置
        for event in graph.stream(user_data, config):
            for node, value in event.items():
                logger.info(f"进入处理节点: node={node}")
                print(f"\n处理节点: {node}")
                
                # 检查是否是中断节点
                if node == "__interrupt__":
                    logger.warning(f"节点{node}触发人工审核中断")
                    # 处理中断情况，提取中断信息
                    print("\n需要人工审核:")
                    
                    # 安全解析中断数据，修复索引错误
                    interrupt_data = {}
                    if isinstance(value, tuple):
                        # 检查元组长度，只在安全时访问
                        if len(value) >= 2 and isinstance(value[1], dict):
                            interrupt_data = value[1]
                        elif len(value) >= 1 and isinstance(value[0], dict):
                            interrupt_data = value[0]
                        else:
                            # 尝试将元组转换为字典
                            try:
                                interrupt_data = dict(value)
                            except:
                                interrupt_data = {"error": "无法解析中断数据"}
                                logger.error("中断数据解析失败，转换为字典出错")
                    elif isinstance(value, dict):
                        interrupt_data = value
                    else:
                        interrupt_data = {"data": str(value)}
                    
                    # 记录审核数据
                    credit_rating = interrupt_data.get("credit_rating", "未提供")
                    fraud_detection = interrupt_data.get("fraud_detection", "未提供")
                    compliance = interrupt_data.get("compliance", "未提供")
                    logger.info(f"人工审核数据 - 信用评级: {credit_rating}, 反欺诈结果: {fraud_detection}, 合规检查: {compliance}")
                                        
                    # 安全获取审核数据
                    print("信用评级:", credit_rating)
                    print("反欺诈结果:", fraud_detection)
                    print("合规检查:", compliance)
                    
                    # 获取人工输入
                    while True:
                        action = input("请输入审核结果(approve/reject): ").strip().lower()
                        if action in ["approve", "reject"]:
                            break
                        print("请输入有效的审核结果(approve/reject)")
                    logger.info(f"人工审核操作: {action}")
                    
                    feedback = input("请输入审核意见（可选）: ").strip()
                    if feedback:
                        logger.info(f"人工审核意见: {feedback}")
                    
                    # 使用Command继续流程
                    command_type = "accept" if action == "approve" else "reject"
                    logger.info(f"发送继续流程命令: type={command_type}")

                    for chunk in graph.stream(
                        Command(resume={"type": command_type, "feedback": feedback}),
                        config
                    ):
                        for chunk_node, chunk_value in chunk.items():
                            logger.info(f"处理子节点: {chunk_node}")
                            print(f"处理节点: {chunk_node}")
                            # 安全地获取状态信息
                            if isinstance(chunk_value, dict):
                                status = chunk_value.get("status", "未知")
                                logger.info(f"子节点状态: {status}")
                                print("状态:", status)
                            elif isinstance(chunk_value, tuple):
                                # 处理元组类型的返回值
                                if len(chunk_value) > 1 and isinstance(chunk_value[1], dict):
                                    status = chunk_value[1].get("status", "未知")
                                elif len(chunk_value) > 0:
                                    status = str(chunk_value[0])
                                else:
                                    status = "空结果"
                                logger.info(f"子节点状态: {status}")
                                print("状态:", status)
                            else:
                                status = str(chunk_value)
                                logger.info(f"子节点状态: {status}")
                                print("状态:", status)
                
                else:
                    result = value
                    # 安全地获取状态信息，处理可能的元组类型
                    if isinstance(result, dict):
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
        
        # 输出最终结果
        print("\n=== 流程结束 ===")
        logger.info("=== 贷款申请流程处理结束 ===")

        # 安全处理最终结果
        if isinstance(result, dict):
            final_status = result.get("status", "未知")
            logger.info(f"最终状态: {final_status}")
            print("最终状态:", final_status)

            if "human_feedback" in result:
                logger.info(f"审核意见: {result['human_feedback']}")
                print("审核意见:", result["human_feedback"])

            if "final_contract" in result:
                logger.info("生成合同已完成")
                print("\n生成的合同:")
                print(result["final_contract"])

        elif isinstance(result, tuple):
            final_data = None
            if len(result) > 1 and isinstance(result[1], dict):
                final_data = result[1]
            elif len(result) > 0 and isinstance(result[0], dict):
                final_data = result[0]
                
            if final_data:
                final_status = final_data.get("status", "未知")
                logger.info(f"最终状态: {final_status}")
                print("最终状态:", final_status)

                if "human_feedback" in final_data:
                    logger.info(f"审核意见: {final_data['human_feedback']}")
                    print("审核意见:", final_data["human_feedback"])

                if "final_contract" in final_data:
                    logger.info("生成合同已完成")
                    print("\n生成的合同:")
                    print(final_data["final_contract"])
            else:
                logger.info(f"最终结果: {str(result)}")
                print("最终结果:", str(result))
        else:
            logger.info(f"最终结果: {str(result)}")
            print("最终结果:", str(result))

        return {"status": "success", "thread_id": thread_id}

    except Exception as e:
        logger.error(f"贷款申请流程处理失败: {str(e)}", exc_info=True)
        raise  # 重新抛出异常让FastAPI处理
    

if __name__ == "__main__":
    logger.info("启动贷款分析API服务")
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)
