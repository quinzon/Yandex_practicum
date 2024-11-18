from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from auth_service.src.api.v1 import auth, user, role, permission
from auth_service.src.core.config import (PROJECT_NAME,
                                          get_redis_settings)
from auth_service.src.db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()

    redis.redis_client = Redis(host=redis_settings.host, port=redis_settings.port,
                               decode_responses=True)

    yield

    await redis.redis_client.close()


app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"],
                  storage_uri=get_redis_settings().redis_url())
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(user.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(role.router, prefix='/api/v1/auth/roles', tags=['roles'])
app.include_router(permission.router, prefix='/api/v1/auth/permissions', tags=['permissions'])
