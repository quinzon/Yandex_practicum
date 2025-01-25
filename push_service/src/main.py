from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from push_service.src.api.v1 import message, websocket
from push_service.src.core.config import get_global_settings, get_redis_settings
from push_service.src.db import redis

settings = get_global_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()
    redis.redis_client = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)
    yield
    await redis.redis_client.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(message.router, prefix='/api/v1/message', tags=['message'])
app.include_router(websocket.router, prefix='/api/v1/websocket', tags=['websocket'])
