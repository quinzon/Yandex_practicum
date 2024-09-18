import time

from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{test_settings.es_host}:{test_settings.es_port}', verify_certs=False)
    while True:
        if es_client.ping():
            print("ES is available!")
            break
        print(f"Waiting for ES...")
        time.sleep(1)
