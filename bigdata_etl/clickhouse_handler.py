import requests

from abstract_consumer import AbstractTopicConsumer
from helpers.backoff_func_wrapper import backoff


class ClickHouseHandler:
    def __init__(self, host):
        self.host = host

    @backoff()
    def create_table(self, topic: AbstractTopicConsumer):
        query = topic.create_table_query()
        requests.post(self.host, params={"query": query})

    @backoff()
    def send_data_to_clickhouse(self, table_name: str, data: list):
        values = ", ".join(
            f"({', '.join([repr(value) for value in row.values()])})"
            for row in data
        )

        query = f"INSERT INTO {table_name} ({', '.join(data[0].keys())}) VALUES {values}"

        requests.post(self.host, params={"query": query})
