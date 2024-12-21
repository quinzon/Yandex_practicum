import json
import time
from abstract_consumer import AbstractTopicConsumer


class VideoCompleteViewsConsumer(AbstractTopicConsumer):
    topic_name = "video_complete_views"
    table_name = "video_watch_process_data"
    fields = ["timestamp", "user_id", "film_id", "progress"]

    def process_message(self, message_value):
        try:
            event_data = json.loads(message_value)

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(event_data['timestamp']))
            user_id = event_data['user_id']
            film_id = event_data['payload']['film_id']
            progress = event_data['payload']['progress']

            return {
                "table_name": self.table_name,
                "data": [{
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "film_id": film_id,
                    "progress": progress
                }]
            }

        except json.JSONDecodeError:
            print(f"Error decoding JSON message: {message_value}")
            return None

    def create_table_query(self):
        return f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            timestamp DateTime,
            user_id UUID,
            film_id UUID,
            progress Float32
        ) ENGINE = MergeTree()
        ORDER BY timestamp
        """
