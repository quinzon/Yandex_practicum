from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from .api.v1 import films, genres, persons
from .core.config import (PROJECT_NAME,
                          get_redis_settings, get_elastic_settings)
from .db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()
    elastic_settings = get_elastic_settings()

    redis.redis = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{elastic_settings.host}:{elastic_settings.port}']
    )

    yield

    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
