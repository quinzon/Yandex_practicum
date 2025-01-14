from kafka_consumer import KafkaConsumer
from clickhouse_handler import ClickHouseHandler
from topics.video_complete_views import VideoCompleteViewsConsumer
from topics.video_page_views import VideoPageViewsConsumer
from config import settings


def create_clickhouse_handler():
    return ClickHouseHandler(settings.clickhouse_host)


def create_kafka_consumer(clickhouse_handler, topics):
    return KafkaConsumer(
        settings.kafka_broker,
        topics=topics,
        clickhouse_handler=clickhouse_handler,
        poll_interval=settings.poll_interval,
        memory_log_interval=settings.memory_log_interval,
    )


def main():
    clickhouse_handler = create_clickhouse_handler()

    topics = [
        VideoCompleteViewsConsumer(),
        VideoPageViewsConsumer(),
    ]

    kafka_consumer = create_kafka_consumer(clickhouse_handler, topics)

    for topic in topics:
        clickhouse_handler.create_table(topic)

    kafka_consumer.consume_messages()


if __name__ == '__main__':
    main()
