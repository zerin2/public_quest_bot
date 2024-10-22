import json
from functools import wraps

from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    NoResultFound,
    InvalidRequestError,
    StatementError
)

from src.logs.config import db_logger


def handle_db_errors(func):
    """
    Обработка исключений, которые могут возникнуть
    при работе с бд. Декоратор применяется к
    асинхронным функциям.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except StatementError as e:
            db_logger.exception(
                f'Передаются некорректные параметры\n'
                f'StatementError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except NoResultFound as e:
            db_logger.exception(
                f'NoResultFound '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except InvalidRequestError as e:
            db_logger.exception(
                f'Запрос выполнен с нарушением '
                f'логики SQLAlchemy\n'
                f'InvalidRequestError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except SQLAlchemyError as e:
            db_logger.exception(
                f'SQLAlchemyError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except IntegrityError as e:
            db_logger.warning(
                f'IntegrityError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except ValueError as e:
            db_logger.warning(
                f'ValueError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except ConnectionError as e:
            db_logger.critical(
                f'Потеря соединения с базой данных '
                f'или проблемы на стороне сервера,\n'
                f'ConnectionError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except Exception as e:
            db_logger.exception(
                f'Неизвестная ошибка '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise

    return wrapper


def handle_json_errors(func):
    """
    Обработка исключений, которые могут возникнуть
    при обработке json. Декоратор применяется к
    асинхронным функциям.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            db_logger.exception(
                f'Файл по указанному пути не найден или '
                f'не может быть создан\n'
                f'FileNotFoundError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except TypeError as e:
            db_logger.exception(
                f'Объект, который не поддерживается JSON\n'
                f'TypeError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except PermissionError as e:
            db_logger.exception(
                f'Нет прав доступа для чтения/записи файла\n'
                f'PermissionError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except UnicodeDecodeError as e:
            db_logger.exception(
                f'Файл содержит символы, '
                f'которые не могут быть декодированы в utf-8\n'
                f'UnicodeDecodeError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except json.JSONDecodeError as e:
            db_logger.exception(
                f'Попытка десериализовать строку, '
                f'которая не является корректным JSON\n'
                f'json.JSONDecodeError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except IntegrityError as e:
            db_logger.warning(
                f'IntegrityError '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise
        except Exception as e:
            db_logger.exception(
                f'Неизвестная ошибка '
                f'in {func.__name__} {args}, {kwargs}: {str(e)}'
            )
            raise

    return wrapper
