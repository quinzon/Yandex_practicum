from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from notification_service.src.api.v1 import notifications
from notification_service.src.core.config import settings
from notification_service.src.core.logger import logger
from notification_service.src.core.rabbitmq import rabbitmq


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Starting RabbitMQ in lifespan...')
    await rabbitmq.connect()
    await rabbitmq.initialize_queues()

    yield

    logger.info('Stopping RabbitMQ in lifespan...')
    await rabbitmq.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(notifications.router, prefix='/api/v1', tags=['notifications'])
