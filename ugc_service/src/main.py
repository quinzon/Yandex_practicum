from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


from ugc_service.src.core.config import settings
from ugc_service.src.api.v1 import bookmark, film_rating, review
from ugc_service.src.core.mongo import mongo_client
from ugc_service.src.setup_mongo import init_mongo_and_shard


if settings.env != 'test':
    from sentry.sentry_client import SentryClient
    sentry_client = SentryClient()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_mongo_and_shard()
    yield
    mongo_client.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(bookmark.router, prefix='/api/v1/ugc', tags=['bookmark'])
app.include_router(film_rating.router, prefix='/api/v1/ugc', tags=['film_rating'])
app.include_router(review.router, prefix='/api/v1/ugc', tags=['review'])
