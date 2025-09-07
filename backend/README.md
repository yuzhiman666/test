# auto_finance_poc

## 前提准备

-   本地安装 Mysql(存储汽车信息)
-   本地安装 Podman(容器化 Redis，存储贷款方案)
-   本地安装 MongoDB(存储测试用户征信信息)
-   Python 虚拟环境创建(如果需要的话，需要安装的模块包参见：requirements.txt)

## 数据准备

-   MysqlDB，汽车信息表创建和数据初始化：chat_bot\remotes\auto_recommend\ddl.sql
-   Redis，贷款方案 RAG 初始化，chat_bot\remotes\loan_suggest\rag_input.py
-   Redis, 汽车贷款管理办法 RAG 初始化 init_data\rag_input.py
    > 注意修改向量模型的 API-Key
-   MongoDB，预审测试用户征信信息初始化，chat_bot\remotes\loan_pre-examination\src\credit_info_service.py

## 设定修改

-   chat_bot\remotes\auto_recommend\src\agent.py 修改自己的 Mysql 的用户名和密码
-   后端各个子文件夹下的 config 文件夹下放置 Keys.json(设定 DASHSCOPE_API_KEY 的 Json 数据)

## 后端启动(python 命令启动)

-   chat_bot\mcp_server\_\_main\_\_.py
-   chat_bot\remotes\auto_recommend\_\_main\_\_.py
-   chat_bot\remotes\loan_suggest\_\_main\_\_.py
-   chat_bot\remotes\loan_pre-examination\_\_main\_\_.py
-   chat_bot\hosts\_\_main\_\_.py
-   backend\main_for_human_in_loop.py

## 测试用前端启动(npm install 后 npm run dev)

-   chat_bot\Stream_Chat_Demo\frontend\stream-chat
