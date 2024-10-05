pytest_plugins = [
    'movie_service.tests.functional.fixtures.es_fixtures',
    'movie_service.tests.functional.fixtures.redis_fixtures',
    'movie_service.tests.functional.fixtures.http_fixtures',
    'movie_service.tests.functional.fixtures.event_loop_fixtures',
]
