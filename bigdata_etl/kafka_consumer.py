import logging
import time
import psutil

from dataclasses import dataclass
from confluent_kafka import Consumer, KafkaException
from clickhouse_handler import ClickHouseHandler
from helpers.backoff_func_wrapper import backoff


@dataclass
class KafkaConfig:
    broker: str
    poll_interval: float
    memory_log_interval: float


class KafkaConsumer:
    def __init__(self, config: KafkaConfig, topics: list, clickhouse_handler: ClickHouseHandler):
        self.config = config
        self.topics = topics
        self.clickhouse_handler = clickhouse_handler
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_memory_log_time = time.time()
        self.consumer = self._create_consumer()
        self._running = True

    def consume_messages(self):
        self._subscribe_to_topics()
        topic_buffers = {topic.topic_name: [] for topic in self.topics}

        try:
            while self._running:
                self._poll_messages(topic_buffers)
                self._flush_buffers(topic_buffers)
                self._log_memory_usage_periodically()

        except KeyboardInterrupt:
            self.logger.info('Shutting down consumer.')
        finally:
            self.logger.info("Closing Kafka consumer.")
            self.consumer.close()

    def stop(self):
        self._running = False

    def _create_consumer(self) -> Consumer:
        return Consumer({
            'bootstrap.servers': self.config.broker,
            'group.id': 'bigdata_etl_group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

    def _subscribe_to_topics(self):
        topic_names = [topic.topic_name for topic in self.topics]
        self.consumer.subscribe(topic_names)
        self.logger.info(f'Subscribed to topics: {", ".join(topic_names)}')

    def _poll_messages(self, topic_buffers: dict):
        start_time = time.time()
        while time.time() - start_time < self.config.poll_interval:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                self._handle_error(msg)
                continue
            self._process_message(msg.topic(), msg.value().decode('utf-8'), topic_buffers)

    def _process_message(self, topic_name: str, message_value: str, topic_buffers: dict):
        for topic in self.topics:
            if topic.topic_name == topic_name:
                event_data = topic.process_message(message_value)
                if event_data:
                    topic_buffers[topic_name].append(event_data)
                break

    def _handle_error(self, msg):
        if msg.error().code() != KafkaException._PARTITION_EOF:
            self.logger.error(f'Consumer error: {msg.error()}')

    def _flush_buffers(self, topic_buffers: dict):
        for topic_name, buffer in topic_buffers.items():
            if buffer:
                self._send_to_clickhouse(buffer)
                buffer.clear()
                self.consumer.commit(asynchronous=False)

    @backoff()
    def _send_to_clickhouse(self, event_buffer: list):
        for event_data in event_buffer:
            self.clickhouse_handler.send_data_to_clickhouse(event_data['table_name'], event_data['data'])

    def _log_memory_usage_periodically(self):
        if time.time() - self.last_memory_log_time > self.config.memory_log_interval:
            self._log_memory_usage()
            self.last_memory_log_time = time.time()

    def _log_memory_usage(self):
        process = psutil.Process()
        memory_info = process.memory_info()
        self.logger.info(f'Memory usage: RSS={memory_info.rss / (1024 * 1024):.2f} MB, '
                         f'VMS={memory_info.vms / (1024 * 1024):.2f} MB')
