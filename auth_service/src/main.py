from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from auth_service.src.api.v1 import auth, user, role, permission
from auth_service.src.core.oauth import register_providers
from auth_service.src.core.config import (get_global_settings,
                                          get_redis_settings)
from auth_service.src.core.tracing import init_tracer
from auth_service.src.db import redis
from auth_service.src.models.dto.common import ErrorMessages

settings = get_global_settings()


def setup_tracing(app: FastAPI):
    if settings.env != 'test':
        init_tracer()
        FastAPIInstrumentor.instrument_app(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()

    redis.redis_client = Redis(host=redis_settings.host, port=redis_settings.port,
                               decode_responses=True)
    register_providers()
    yield

    await redis.redis_client.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


setup_tracing(app)


@app.middleware('http')
async def add_x_request_id_header(request: Request, call_next):
    tracer = trace.get_tracer(__name__) if settings.env != 'test' else None
    request_id = request.headers.get('x-request-id')

    if not request_id:
        return ORJSONResponse(status_code=HTTPStatus.BAD_REQUEST,
                              content={'detail': ErrorMessages.REQUEST_ID_REQUIRED})

    if tracer:
        with tracer.start_as_current_span('request') as span:
            span.set_attribute('x-request-id', request_id)
            response = await call_next(request)
            return response
    else:
        return await call_next(request)


limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit],
                  storage_uri=get_redis_settings().redis_url())

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key,
                   session_cookie='session')

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(user.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(role.router, prefix='/api/v1/auth/roles', tags=['roles'])
app.include_router(permission.router, prefix='/api/v1/auth/permissions', tags=['permissions'])
