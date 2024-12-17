import logging
import os


def setup_logger(name='bigdata_logger'):
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    logger_ = logging.getLogger(name)
    if not logger_.handlers:
        logger_.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger_.addHandler(console_handler)
        logger_.propagate = False

    return logger_


logger = setup_logger()
