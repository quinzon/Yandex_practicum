from kafka_consumer import KafkaConsumer
from clickhouse_handler import ClickHouseHandler
from topics.video_complete_views import VideoCompleteViewsConsumer
from topics.video_page_views import VideoPageViewsConsumer
from config import settings


def main():
    clickhouse_handler = ClickHouseHandler(settings.clickhouse_host)

    video_complete_views_consumer = VideoCompleteViewsConsumer()
    video_page_views_consumer = VideoPageViewsConsumer()

    topics = [
        video_complete_views_consumer,
        video_page_views_consumer,
    ]

    kafka_consumer = KafkaConsumer(
        settings.kafka_broker,
        topics=topics,
        clickhouse_handler=clickhouse_handler,
        poll_interval=settings.poll_interval
    )

    for topic in topics:
        clickhouse_handler.create_table(topic)

    kafka_consumer.consume_messages()


if __name__ == "__main__":
    main()
