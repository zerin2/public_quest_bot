import inspect
import logging
from typing import Callable

from loguru import logger

BOT_DEBUG_INFO_LOGS_PATH: str = 'logs/bot/debug_info.log'
BOT_ERROR_LOGS_PATH: str = 'logs/bot/error.log'

DB_DEBUG_INFO_LOGS_PATH: str = 'logs/db/debug_info.log'
DB_ERROR_LOGS_PATH: str = 'logs/db/error.log'

LOGS_CATEGORY: dict = {
    'ALL_TYPES': ('INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'),
}


class InterceptHandler(logging.Handler):
    """
    Хэндлер, который перехватывает сообщения от стандартных логгеров
    и направляет их в глобальный синк Loguru (`global_logger`).
    """

    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = bot_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        (
            bot_logger
            .bind(logger_name=record.name)
            .opt(depth=depth, exception=record.exc_info)
            .log(level, record.getMessage())
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


def filter_category(name_category: str, logs_category: str) -> Callable:
    """ Фильтр для категории раздела и виду ошибки. """

    return lambda record: (
            record['extra'].get('category') == name_category and
            record['level'].name in LOGS_CATEGORY[logs_category]
    )


bot_logger = logger.bind(category='bot')
bot_logger.add(
    BOT_DEBUG_INFO_LOGS_PATH,
    rotation='10 MB',
    level='DEBUG',
    enqueue=True,
    backtrace=True,
    filter=filter_category('bot', 'ALL_TYPES')
)
bot_logger.add(
    BOT_ERROR_LOGS_PATH,
    rotation='10 MB',
    level='ERROR',
    enqueue=True,
    backtrace=True,
    diagnose=True,
    filter=filter_category('core', 'ALL_TYPES')
)

db_logger = logger.bind(category='db')
db_logger.add(
    DB_DEBUG_INFO_LOGS_PATH,
    rotation='10 MB',
    level='DEBUG',
    enqueue=True,
    backtrace=True,
    filter=filter_category('db', 'ALL_TYPES')
)
db_logger.add(
    DB_ERROR_LOGS_PATH,
    rotation='10 MB',
    level='ERROR',
    enqueue=True,
    backtrace=True,
    diagnose=True,
    filter=filter_category('db', 'ALL_TYPES')
)
