import logging
import click
import httpx
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from src.agent import LoanPreExaminationAgent
from src.agent_executor import LoanPreExaminationAgentExecutor

logging.basicConfig(level=logging.INFO)
# 禁用httpx、httpcore和asyncio的噪音日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='0.0.0.0')
@click.option('--port', 'port', default=10030)
def main(host, port):
    """Start the Loan Pre-examination Agent server.
    """
    try:
        logger.info("Start the Loan Pre-examination Agent server.")
        capabilities = AgentCapabilities(
            streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id='loan_pre-examination',
            name='loan pre-examination',
            description='Based on the user basic information, conduct a loan pre-examination',
            tags=['loan pre-examination', 'pre-examination'],
            examples=['What is the loan pre-examination result for me?'],
        )
        agent_card = AgentCard(
            name='Loan Pre-examination Agent',
            description='Conduct loan pre-approval for users',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=LoanPreExaminationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=LoanPreExaminationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=LoanPreExaminationAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
