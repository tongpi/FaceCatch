import logging
import sys
from logging.handlers import RotatingFileHandler

from settings import LOG_FILE_PATH


def config_log():

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=(1024 * 1024 * 10),  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = config_log()

