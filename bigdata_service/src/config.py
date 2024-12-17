import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('APP_PORT', '5000'))

    KAFKA_BROKER_URLS = os.getenv('KAFKA_BROKER_URLS', 'localhost:9092')
    KAFKA_EVENTS_TOPIC_PREFIX = os.getenv('KAFKA_EVENTS_TOPIC_PREFIX', 'events')

    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
