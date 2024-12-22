import logging
import time
import psutil

from confluent_kafka import Consumer, KafkaException
from clickhouse_handler import ClickHouseHandler
from helpers.backoff_func_wrapper import backoff


class KafkaConsumer:
    def __init__(
            self,
            broker: str,
            topics: list,
            clickhouse_handler: ClickHouseHandler,
            poll_interval: float,
            memory_log_interval: float
    ):
        self.broker = broker
        self.topics = topics
        self.clickhouse_handler = clickhouse_handler
        self.poll_interval = poll_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory_log_interval = memory_log_interval
        self.last_memory_log_time = time.time()

    @backoff()
    def consume_messages(self):
        consumer = Consumer({
            'bootstrap.servers': self.broker,
            'group.id': 'bigdata_etl_group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

        topic_names = [topic.topic_name for topic in self.topics]
        consumer.subscribe(topic_names)
        self.logger.info(f'Subscribed to topics: {", ".join(topic_names)}')

        topic_buffers = {topic.topic_name: [] for topic in self.topics}

        try:
            while True:
                start_time = time.time()
                while time.time() - start_time < self.poll_interval:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaException._PARTITION_EOF:
                            continue
                        else:
                            self.logger.error(f'Consumer error: {msg.error()}')
                            continue

                    topic_name = msg.topic()
                    message_value = msg.value().decode('utf-8')

                    for topic in self.topics:
                        if topic.topic_name == topic_name:
                            event_data = topic.process_message(message_value)
                            if event_data:
                                topic_buffers[topic_name].append(event_data)
                            break

                for topic_name, buffer in topic_buffers.items():
                    if buffer:
                        self._send_to_clickhouse(buffer)
                        buffer.clear()
                        consumer.commit(asynchronous=False)

                if time.time() - self.last_memory_log_time > self.memory_log_interval:
                    self._log_memory_usage()
                    self.last_memory_log_time = time.time()

        except KeyboardInterrupt:
            self.logger.info('Shutting down consumer.')
        finally:
            consumer.close()

    @backoff()
    def _send_to_clickhouse(self, event_buffer: list):
        for event_data in event_buffer:
            self.clickhouse_handler.send_data_to_clickhouse(event_data['table_name'], event_data['data'])

    def _log_memory_usage(self):
        process = psutil.Process()
        memory_info = process.memory_info()
        self.logger.info(f'Memory usage: RSS={memory_info.rss / (1024 * 1024):.2f} MB, '
                         f'VMS={memory_info.vms / (1024 * 1024):.2f} MB')
