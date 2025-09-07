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
from src.agent import AutoRecommendAgent
from src.agent_executor import AutoRecommendAgentExecutor

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
@click.option('--port', 'port', default=10010)
def main(host, port):
    """Start Automobile Recommendation Agent Server.
    """
    try:
        logger.info("Start Automobile Recommendation Agent Server.")
        capabilities = AgentCapabilities(
            streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id='automobile_recommendation',
            name='Automobile Recommendation',
            description='Query relevant data from the database for automobile recommendation to user',
            tags=['Automobile Recommendation', 'Auto Recommend'],
            examples=['Recommend a car for me', 'What is the best car for my budget?'],
        )
        agent_card = AgentCard(
            name='Automobile Recommendation Agent',
            description='Query relevant data from the database for automobile recommendation to user',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=AutoRecommendAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=AutoRecommendAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=AutoRecommendAgentExecutor(),
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
