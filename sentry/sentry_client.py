import os
import sentry_sdk
from dotenv import load_dotenv
from threading import Lock


class SentryClient:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        sentry_dsn = os.getenv("SENTRY_DSN")
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,  # Захват производительности
        )
