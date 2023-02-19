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
config_file_name = f".env-{ENVIRONMENT}" if ENVIRONMENT else ".env"
directory = os.getcwd()
config_file_path = os.path.abspath(f"./properties/{config_file_name}") \
    if LOCAL_ENV else f"app/properties/{config_file_name}"
if not os.path.exists(config_file_path):
    logger.error(f"Path does not exists: {config_file_path}")
else:
    logger.info(f"Loading config from file '{config_file_path}'...")
config = Config(config_file_path)


PROJECT_NAME: str = config("PROJECT_NAME", default="File crawler")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
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
LOG_LEVEL: str = config("LOG_LEVEL", default='warn')
if DEBUG or 'debug' in LOG_LEVEL.lower():
    LOGGING_LEVEL = logging.DEBUG
elif 'info' in LOG_LEVEL.lower():
    LOGGING_LEVEL = logging.INFO
elif 'warn' in LOG_LEVEL.lower():
    LOGGING_LEVEL = logging.WARNING
elif 'error' in LOG_LEVEL.lower():
    LOGGING_LEVEL = logging.ERROR
else:
    LOGGING_LEVEL = logging.FATAL

logging.basicConfig(filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=LOGGING_LEVEL)

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

QUEUE_WAIT_TIME: int = config("QUEUE_WAIT_TIME", cast=int, default=10)
