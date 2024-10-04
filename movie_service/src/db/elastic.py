from elasticsearch import AsyncElasticsearch

from movie_service.src.engines.elastic import ElasticAsyncSearchEngine

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch:
    return es


async def get_elastic_engine() -> ElasticAsyncSearchEngine:
    return ElasticAsyncSearchEngine(es)
