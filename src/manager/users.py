from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.db.models import UsersProfile, UsersHistory
from src.manager.base import BaseManager
from src.manager.handle_errors import handle_db_errors


class UserManager(BaseManager):
    """
    Управление действиями, связанными с пользователями в бд:
    добавление, получение информации о пользователе и
    запись истории взаимодействия пользователя с ботом.
    """

    async def get_user_by_id(
            self,
            tg_id: int
    ) -> UsersProfile | None:
        """Получение 'user' из бд по 'user_tg_id'."""

        return await self.get_by_field(
            self.USER_PROFILE_MODEL,
            'telegram_id',
            tg_id
        )

    @handle_db_errors
    async def del_user_by_id(
            self,
            tg_id: int
    ) -> None:
        """Удаление 'user' из бд по 'user_tg_id'."""

        return await self.delete_instance(
            self.USER_PROFILE_MODEL,
            'telegram_id',
            tg_id
        )

    async def is_exist_user(
            self,
            tg_id: int
    ) -> bool | None:
        """Проверка, существует ли пользователь с указанным 'tg_id'."""

        return await self.is_exist(
            self.USER_PROFILE_MODEL,
            'telegram_id',
            tg_id)

    @handle_db_errors
    async def add_user(
            self,
            tg_id: int
    ) -> UsersProfile | None:
        """
        Добавьте нового пользователя с 'user_tg_id',
        если пользователь не существует.
        """
        return await self.add_instance(
            self.USER_PROFILE_MODEL,
            {
                'telegram_id': str(tg_id)
            }
        )

    @handle_db_errors
    async def get_or_create_user(self, tg_id):
        """
        Получает пользователя по его Telegram ID, если такой пользователь существует.
        Если пользователь не найден, создаёт нового пользователя с указанным Telegram ID
        и возвращает его.
        """
        user = await self.get_user_by_id(tg_id)
        if user:
            return user
        else:
            await self.add_user(tg_id)
            user = await self.get_user_by_id(tg_id)
            return user

    @handle_db_errors
    async def write_history(
            self,
            message: Message,
            state: FSMContext | str = ''
    ) -> UsersHistory | None:
        """
        Запись информации о сообщениях пользователей в бд,
        сохраняя историю взаимодействий с ботом.
        Проверяет, существует ли пользователь в базе данных,
        и добавляет его, если его нет.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        message_id = message.message_id
        message_content = message.text

        if not await self.is_exist_user(user_id):
            await self.add_user(user_id)

        if isinstance(state, FSMContext):
            state = str(await state.get_data())

        user = await self.get_user_by_id(user_id)

        if not user:
            raise ValueError(
                'Передано пустое значение в \'user\'.'
            )

        await self.add_instance(
            self.USER_HISTORY_MODEL,
            {
                'user_id': user.id,
                'chat_id': chat_id,
                'message_id': message_id,
                'message_content': message_content,
                'state': state or '',
            }
        )
        return None
