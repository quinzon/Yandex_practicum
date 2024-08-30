from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core.config import RedisSettings, ElasticSearchSettings, PROJECT_NAME
from db import elastic, redis

app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=RedisSettings.REDIS_HOST, port=RedisSettings.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{ElasticSearchSettings.ELASTIC_HOST}:{ElasticSearchSettings.ELASTIC_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
