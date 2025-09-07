import logging
import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from src.agent import LoanPreExaminationAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class LoanPreExaminationAgentExecutor(AgentExecutor):
    """Loan pre-examination agent executor based on LangGraph.

    Be responsible for the task of providing Loan pre-examinations.
    Use the LangGraph framework and stream processing to loan pre-examination.
    """

    def __init__(self):
        """Initialize the Loan pre-examination agent executor.
        """
        self.agent = LoanPreExaminationAgent()
        asyncio.run(self.agent.initialize())
        logger.info("Loan pre-examination agent executor initialize completed.")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """The main methods for performing Loan pre-examination tasks.

        Args:
            context: The request context contains user input and task information
            event_queue: Event queue, used for publishing task status updates
        """
        error = self._validate_request(context)
        session_id = context._params.metadata["session_id"]
        if error:
            logger.error("Loan pre-examination agent: Request verification failed")
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        logger.info(f"Loan pre-examination agent receives: {query[:100]}...")

        task = context.current_task
        if not task:
            if not context.message:
                logger.error("Loan pre-examination agent: Missing message context")
                raise ServerError(error=InvalidParamsError())
            task = new_task(context.message)
            event_queue.enqueue_event(task)
            logger.info(f"Create a new task - ID: {task.id}, Context: {task.contextId}")
            
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        try:
            logger.info(f"Start streaming processing of Loan pre-examination queries - Task ID: {task.id}")
            # 使用异步流处理
            async for item in self.agent.astream(query, task.contextId, session_id):
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']

                if not is_task_complete and not require_user_input:
                    logger.debug(
                        f"In task processing - Task ID: {task.id}, Content: {item['content']}")
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                    )
                elif require_user_input:
                    logger.info(
                        f"User input is required - Task ID: {task.id}, Content: {item['content']}")
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    break
                else:
                    logger.info(
                        f"Loan pre-examination completed - Task ID: {task.id}, Result: {item['content'][:100]}...")
                    # 添加最终的agent响应消息到历史记录
                    final_message = new_agent_text_message(
                        item['content'],
                        task.contextId,
                        task.id,
                    )
                    # 添加 artifact 包含转换结果
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='conversion_result',
                    )
                    # 完成任务并包含最终消息
                    await updater.complete()
                    break

        except Exception as e:
            logger.error(
                f'The Loan pre-examination agent has a streaming response error - Task ID: {task.id if task else "Unknown"}, ErrorInfo: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())