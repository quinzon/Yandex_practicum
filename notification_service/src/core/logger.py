import logging

from notification_service.src.core.config import settings


def setup_logger(name='notification_logger'):
    log_level = settings.log_level

    logger_instance = logging.getLogger(name)
    if not logger_instance.handlers:
        logger_instance.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger_instance.addHandler(console_handler)
        logger_instance.propagate = False

    return logger_instance


logger = setup_logger()
