from typing import TypeVar, Type

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

import src.db.models as model
from src.manager.handle_errors import handle_db_errors
from src.logs.config import db_logger


class BaseRepository:
    """Базовый репозиторий."""

    USER_PROFILE_MODEL = model.UsersProfile
    USER_HISTORY_MODEL = model.UsersHistory

    def __init__(self, session: AsyncSession):
        self.session = session


class BaseManager(BaseRepository):
    """
    Базовый менеджер, с основными методами работы с бд.

    Большинство ошибок обрабатывается в '@handle_db_errors'.
    """

    ModelType = TypeVar('ModelType', bound=DeclarativeMeta)

    @staticmethod
    def check_variable(*variables: str | int) -> None:
        """
        Проверяет, что переменные не являются None,
        пустой строкой или нулевым числом.
        Выбрасывает ValueError, если условие нарушено.
        """

        for variable in variables:
            if variable is None:
                raise ValueError(
                    'Передано значение None в одну из переменных.'
                )

            if isinstance(variable, str) and variable == '':
                raise ValueError(
                    'Передана пустая строка.'
                )

            if isinstance(variable, int) and variable <= 0:
                raise ValueError(
                    f'Передано значение меньше или равное нулю: {variable}.'
                )

    @handle_db_errors
    async def is_exist(
            self,
            model: Type[ModelType],
            field_name: str,
            variable: str | int,
    ) -> bool:
        """
        Проверяет, существует ли запись в бд для заданной модели,
        имени поля и значения переменной.
        Возвращает True, если запись существует, иначе False.
        """
        self.check_variable(variable)

        field = getattr(model, field_name)
        result = await self.session.execute(
            select(model)
            .where(field == str(variable))
        )
        variable_is_exist = result.scalars().first()
        return variable_is_exist is not None

    @handle_db_errors
    async def is_exist_fields(
            self,
            model: Type[ModelType],
            fields: dict
    ) -> bool:
        """
        Проверяет, существуют ли записи в бд
        для всех полей в переданном словаре.
        """

        for field_name, value in fields.items():
            self.check_variable(value)
            if not await self.is_exist(model, field_name, value):
                return False
        return True

    @handle_db_errors
    async def get_by_field(
            self,
            model: Type[ModelType],
            field_name: str,
            variable: str | int,
    ) -> ModelType | None:
        """
        Получает запись из бд для заданной модели,
        где значение указанного поля совпадает с переданным значением.
        """
        self.check_variable(variable)

        field = getattr(model, field_name)
        result = await self.session.execute(
            select(model)
            .where(field == str(variable))
        )
        value = result.scalars().first()
        return value

    @handle_db_errors
    async def get_all_by_field(
            self,
            model: Type[ModelType],
            field_name: str,
            variable: str | int,
    ) -> ModelType | None:
        """
        Получает все записи из бд для заданной модели,
        где значение указанного поля совпадает с переданным значением.
        """
        self.check_variable(variable)

        field = getattr(model, field_name)
        result = await self.session.execute(
            select(model)
            .where(field == str(variable))
        )
        all_value = result.scalars().all()
        return all_value

    @handle_db_errors
    async def delete_instance(
            self,
            model: Type[ModelType],
            field_name: str,
            variable: str | int,
    ) -> None:
        """
        Удаление записи из базы данных для указанной модели
        по заданному полю и значению.
        """
        self.check_variable(variable)

        field = getattr(model, field_name)
        await self.session.execute(
            delete(model)
            .where(field == str(variable))
        )
        await self.session.commit()

    @handle_db_errors
    async def add_instance(
            self,
            model: Type[ModelType],
            fields: dict,
    ) -> ModelType | None:
        """
        Добавление новой записи в базу данных
        для указанной модели с переданными полями.
        """
        for field_name, value in fields.items():
            self.check_variable(value)

        try:
            instance = model(**fields)
            self.session.add(instance)
            await self.session.commit()
        except Exception as e:
            db_logger.exception(
                f'Неизвестная ошибка записи в бд '
                f'{model.__name__}: {str(e)}'
            )
            await self.session.rollback()
            return None
        else:
            return instance
