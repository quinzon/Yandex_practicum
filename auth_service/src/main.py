from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from auth_service.src.api.v1 import auth
from auth_service.src.core.config import (PROJECT_NAME,
                                          get_redis_settings)
from auth_service.src.db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()

    redis.redis_client = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)

    yield

    await redis.redis_client.close()


app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
