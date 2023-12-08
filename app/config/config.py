#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import logging.config
import os
import sys
from typing import List
from urllib.parse import quote

from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from app.helpers.logging import InterceptHandler

VERSION = "0.0.1"

ENVIRONMENT: str = os.getenv("ENVIRONMENT", 'Dev').lower().strip()
logging.info(f"ENVIRONMENT: {ENVIRONMENT}")

LOCAL_ENV = (ENVIRONMENT and ENVIRONMENT.lower() == 'local') \
            or os.getenv("LOCAL_ENV", "false").lower().strip() in [1, 'true', 'yes']

config_file_names = []
if ENVIRONMENT:
    config_file_names.append(f".env-{ENVIRONMENT}")
config_file_names.append(".env")

config = Config()
directory = os.getcwd()
for config_file_name in config_file_names:
    config_file_path = os.path.abspath(f"./properties/{config_file_name}") \
        if LOCAL_ENV else f"app/properties/{config_file_name}"
    if not os.path.exists(config_file_path):
        logger.error(f"Path does not exists: {config_file_path}")
    else:
        logger.info(f"Loading config from file '{config_file_path}'...")
    config_tmp = Config(config_file_path)
    config.file_values.update(config_tmp.file_values)

PROJECT_NAME: str = config("PROJECT_NAME", default="File crawler")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default=[],
)

DEBUG: bool = config("DEBUG", cast=bool, default=False)

DATABASE_HOST: str = config("DATABASE_HOST",
                            default='192.168.1.25')
DATABASE_PORT: str = config("DATABASE_PORT",
                            default='3306')
DATABASE_USER: str = config("DATABASE_USER", default='admin')

DATABASE_PASSWORD: str = config("DATABASE_PASSWORD", default='Welcome123!')

if not DATABASE_PASSWORD:
    logger.warning('DB password not set!')

DATABASE_NAME: str = config("DATABASE_NAME", default='fs_crawler')

DATABASE_URL: str = config("DB_CONNECTION", default='mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
                           .format(user=quote(DATABASE_USER), password=DATABASE_PASSWORD, host=DATABASE_HOST,
                                   port=DATABASE_PORT, db=DATABASE_NAME))

MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

DRY_RUN: bool = config("DRY_RUN", cast=bool, default=True)

DATE_TIME_PATTERN: str = config("DATE_TIME_PATTERN", default='%Y-%m-%dT%H:%M:%S')

# logging configuration
LOG_LEVEL_TRACE = 5
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_SUCCESS = 25
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50

LOG_LEVEL: str = config("LOG_LEVEL", default='warn')
if DEBUG or 'trace' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_TRACE
if 'debug' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_DEBUG
elif 'info' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_INFO
elif 'success' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_SUCCESS
elif 'warn' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_WARNING
elif 'error' in LOG_LEVEL.lower():
    LOGGING_LEVEL = LOG_LEVEL_ERROR
else:
    LOGGING_LEVEL = LOG_LEVEL_CRITICAL

logging.basicConfig(filemode='w', format='%(asctime)s %(thread)d %(threadName)s %(name)s - %(levelname)s - %(message)s',
                    level=LOGGING_LEVEL)

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
# logger.add("log_output_{time}.log")

logging.getLogger().handlers = [InterceptHandler()]
LOGGERS = ("uvicorn.asgi", "uvicorn.access")
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

SHOW_SQL: bool = config("SHOW_SQL", cast=bool, default=False)

sqla_logger = logging.getLogger('sqlalchemy')
sqla_logger.setLevel(logging.INFO if DEBUG else logging.WARNING)
sqla_logger.propagate = False

sqla_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
for hdlr in sqla_logger.handlers:
    hdlr.setLevel(logging.INFO if DEBUG else logging.WARNING)

sqla_logger = logging.getLogger('sqlalchemy.log')
for hdlr in sqla_logger.handlers:
    hdlr.setLevel(logging.INFO if DEBUG else logging.WARNING)

logging.getLogger('requests').setLevel(logging.INFO if DEBUG else logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.INFO if DEBUG else logging.ERROR)
logging.getLogger('botocore').setLevel(logging.INFO if DEBUG else logging.WARNING)

QUEUE_MAX_SIZE: int = config("QUEUE_MAX_SIZE", default=20000)
QUEUE_MIN_SIZE: int = config("QUEUE_MIN_SIZE", default=100)
QUEUE_WAIT_TIME: int = config("QUEUE_WAIT_TIME", cast=int, default=10)  # seconds to wait for queue to get new items when empty
