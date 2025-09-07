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
from src.agent import LoanSuggestAgent
from src.agent_executor import LoanSuggestAgentExecutor

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
@click.option('--port', 'port', default=10020)
def main(host, port):
    """Start the Loan Suggest Agent server.
    """
    try:
        logger.info("Start the Loan Suggest Agent server.")
        capabilities = AgentCapabilities(
            streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id='loan_suggest',
            name='loan suggest',
            description='Give the loan scheme suggestion to user',
            tags=['loan scheme suggestion', 'loan scheme', 'loan suggestion', 'loan suggest'],
            examples=['What is the best loan scheme for me?', 'Suggest a loan scheme based on my requirements'],
        )
        agent_card = AgentCard(
            name='Loan Scheme Suggestion Agent',
            description='Give the loan scheme suggestion to user',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=LoanSuggestAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=LoanSuggestAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=LoanSuggestAgentExecutor(),
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
