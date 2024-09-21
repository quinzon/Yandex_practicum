from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff
from tests.functional.utils.logger import logger


@backoff(start_sleep_time=0.5, factor=2, border_sleep_time=10)
def wait_for_es():
    es_client = Elasticsearch(hosts=f'{test_settings.es_host}:{test_settings.es_port}', verify_certs=False)
    if es_client.ping():
        logger.debug("ES is available!")
        return True
    else:
        raise Exception("Waiting for ES...")


if __name__ == '__main__':
    wait_for_es()
