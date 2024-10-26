from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from starlette.requests import Request

from auth_service.src.api.v1 import auth, user, role, permission
from auth_service.src.core.config import (PROJECT_NAME,
                                          get_redis_settings)
from auth_service.src.core.tracing import init_tracer
from auth_service.src.db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()

    redis.redis_client = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)
    init_tracer()
    yield

    await redis.redis_client.close()


app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def add_x_request_id_header(request: Request, call_next):
    tracer = trace.get_tracer(__name__)
    request_id = request.headers.get("x-request-id")

    with tracer.start_as_current_span("request") as span:
        if request_id:
            span.set_attribute("x-request-id", request_id)
        response = await call_next(request)
        return response


app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(user.router, prefix='/api/v1/auth/users', tags=['users'])
app.include_router(role.router, prefix='/api/v1/auth/roles', tags=['roles'])
app.include_router(permission.router, prefix='/api/v1/auth/permissions', tags=['permissions'])
