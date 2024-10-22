import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, on
from aiogram.types import CallbackQuery, Message

import src.bot.service.constants as const
import src.bot.service.keyboards as keyboard
import src.bot.service.msg_text as msg
from src.bot.service.utilits import send_hint
from src.db.core import async_session
from src.manager.composite_manager import CompositeManager
import src.settings as setting

main_router = Router()
main_registry = SceneRegistry(main_router)


@main_router.message(Command('reset_bot'))
async def reset_cmd(message: Message):
    tg_id = message.from_user.id
    async with async_session() as session:
        manager = CompositeManager(session)
        user = await manager.get_or_create_user(tg_id)
        user.act_code = setting.ACT_CODE['default']
        await session.commit()
    return message.answer(msg.EXIT_MSG)


class PreCheckScene(Scene, state=setting.ACT_STATE['pre_check']):
    @on.message.enter()
    async def check_user(self, message: Message) -> None:
        tg_id = message.from_user.id

        async with async_session() as session:
            manager = CompositeManager(session)
            await manager.write_history(message, setting.ACT_STATE['pre_check'])
            user_data = await manager.get_or_create_user(tg_id)
            if not user_data:
                await message.answer(
                    'Произошла ошибка при получении данных пользователя.'
                )
                return
            act_code = user_data.act_code
        state_name = setting.ACT_STATE.get(act_code, setting.ACT_STATE['start'])
        await self.wizard.goto(state_name)


class StartScene(Scene, state=setting.ACT_STATE['start']):
    @on.message.enter()
    async def handle_enter(
            self, message: Message, state: FSMContext
    ) -> None:
        user_id = message.from_user.id
        data = await state.get_data()
        data[user_id] = user_id
        user_name = (
                message.from_user.username
                or message.from_user.first_name
                or const.UNKNOWN_USER_NAME
        )
        async with async_session() as session:
            user_repo = CompositeManager(session)
            await user_repo.write_history(message, setting.ACT_STATE['start'])
            user = await user_repo.get_user_by_id(user_id)
            user_code = user.act_code
            if user_code == setting.ACT_CODE['default']:
                await message.answer(
                    msg.START_MSG.format(user_name=user_name),
                    parse_mode='Markdown',
                    reply_markup=keyboard.btn_yes(),
                )
                return
            elif user_code == setting.ACT_CODE['present']:
                await message.answer(msg.WIN_MSG)
            else:
                await message.answer('Вы уже находитесь в активном акте!')
                state_name = next(
                    (key for key, value in setting.ACT_CODE.items() if value == user_code),
                    None
                )
                await self.wizard.goto(setting.ACT_STATE[state_name])


class InfoScene(Scene, state=setting.ACT_STATE['default']):
    @on.message.enter()
    async def info_msg(self, message: Message) -> None:
        await asyncio.sleep(0.3)
        await message.answer(
            msg.INFO_ACT_MSG,
            reply_markup=keyboard.btn_start_first_act()
        )
        tg_id = message.from_user.id
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['default'])
            user = await user_manager.get_user_by_id(tg_id)
            act_code = user.act_code
        state_name = setting.ACT_STATE.get(act_code)
        if state_name and state_name != setting.ACT_STATE['default']:
            await self.wizard.goto(state_name)
        else:
            await message.answer('Вы уже находитесь в активном акте!')

    @on.callback_query.enter()
    async def cb_info_msg(self, callback_query: CallbackQuery) -> None:
        await callback_query.message.answer(
            msg.INFO_ACT_MSG,
            reply_markup=keyboard.btn_start_first_act()
        )
        async with async_session() as session:
            user_manager = CompositeManager(session)
            tg_id = callback_query.from_user.id
            user = await user_manager.get_user_by_id(tg_id)
            user.act_code = setting.ACT_CODE['1']
            await session.commit()


class FirstActScene(Scene, state=setting.ACT_STATE['1']):
    @on.message.enter()
    async def str_msg(self, message: Message) -> None:
        await asyncio.sleep(0.3)
        await message.answer(const.FIRST_ACT_NAME)
        await asyncio.sleep(0.2)
        await message.answer(msg.FIRST_ACT_MSG)

    @on.callback_query.enter()
    async def cb_str_msg(self, callback_query: CallbackQuery) -> None:
        await callback_query.answer(const.FIRST_ACT_NAME)
        await callback_query.message.answer(const.FIRST_ACT_NAME)
        await asyncio.sleep(0.2)
        await callback_query.message.answer(msg.FIRST_ACT_MSG)

    @on.message(F.text.lower() == str(msg.FIRST_ACT_KEY))
    async def check_code(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['1'])
            tg_id = message.from_user.id
            user = await user_manager.get_user_by_id(tg_id)
            user.act_code = setting.ACT_CODE['2']
            await session.commit()
        await message.reply(msg.FIRST_FOUND_CODE_MSG)
        await self.wizard.goto(setting.ACT_STATE['2'])

    @on.message(F.text.lower() == str(const.HINT))
    async def get_hint(self, message: Message, bot: Bot) -> None:
        await send_hint(message, bot, msg.FIRST_ACT_HINT, 'hint_1.PNG')

    @on.message()
    async def fallback(self, message: Message) -> None:
        await message.reply(msg.UNKNOWN_MSG_SCENE)


class SecondActScene(Scene, state=setting.ACT_STATE['2']):
    @on.message.enter()
    async def str_msg(self, message: Message) -> None:
        await asyncio.sleep(2)
        await message.answer(const.SECOND_ACT_NAME)
        await asyncio.sleep(0.2)
        await message.answer(msg.SECOND_ACT_MSG)

    @on.callback_query.enter()
    async def cb_str_msg(self, callback_query: CallbackQuery) -> None:
        await callback_query.answer(const.SECOND_ACT_NAME)
        await callback_query.message.answer(const.SECOND_ACT_NAME)
        await asyncio.sleep(0.2)
        await callback_query.message.answer(msg.SECOND_ACT_MSG)

    @on.message(F.text.lower() == str(msg.SECOND_ACT_KEY))
    async def check_code(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['2'])
            tg_id = message.from_user.id
            user = await user_manager.get_user_by_id(tg_id)
            user.act_code = setting.ACT_CODE['3']
            await session.commit()
        await message.reply(msg.SECOND_FOUND_CODE_MSG)
        await self.wizard.goto(setting.ACT_STATE['3'])

    @on.message(F.text.lower() == str(const.HINT))
    async def get_hint(self, message: Message, bot: Bot) -> None:
        await send_hint(message, bot, msg.SECOND_ACT_HINT, 'hint_2.PNG')

    @on.message()
    async def fallback(self, message: Message) -> None:
        await message.reply(msg.UNKNOWN_MSG_SCENE)


class ThirdActScene(Scene, state=setting.ACT_STATE['3']):
    @on.message.enter()
    async def str_msg(self, message: Message) -> None:
        await asyncio.sleep(2)
        await message.answer(const.THIRD_ACT_NAME)
        await asyncio.sleep(0.2)
        await message.answer(msg.THIRD_ACT_MSG)

    @on.callback_query.enter()
    async def cb_str_msg(self, callback_query: CallbackQuery) -> None:
        await callback_query.answer(const.THIRD_ACT_NAME)
        await callback_query.message.answer(const.THIRD_ACT_NAME)
        await asyncio.sleep(0.2)
        await callback_query.message.answer(msg.THIRD_ACT_MSG)

    @on.message(F.text.lower() == str(msg.THIRD_ACT_KEY))
    async def check_code(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['3'])
            tg_id = message.from_user.id
            user = await user_manager.get_user_by_id(tg_id)
            user.act_code = setting.ACT_CODE['final']
            await session.commit()
        await message.reply(msg.THIRD_FOUND_CODE_MSG)
        await self.wizard.goto(setting.ACT_STATE['final'])

    @on.message(F.text.lower() == str(const.HINT))
    async def get_hint(self, message: Message, bot: Bot) -> None:
        await send_hint(message, bot, msg.THIRD_ACT_HINT, 'hint_3.PNG')

    @on.message()
    async def fallback(self, message: Message) -> None:
        await message.reply(msg.UNKNOWN_MSG_SCENE)


class FinalActScene(Scene, state=setting.ACT_STATE['final']):
    @on.message.enter()
    async def str_msg(self, message: Message) -> None:
        await asyncio.sleep(2)
        await message.answer(const.FINAL_ACT_NAME)
        await asyncio.sleep(0.2)
        await message.answer(msg.FINAL_ACT_MSG)

    @on.callback_query.enter()
    async def cb_str_msg(self, callback_query: CallbackQuery) -> None:
        await callback_query.answer(const.FINAL_ACT_NAME)
        await callback_query.message.answer(const.FINAL_ACT_NAME)
        await asyncio.sleep(0.2)
        await callback_query.message.answer(msg.FINAL_ACT_MSG)

    @on.message(F.text.lower().in_(msg.MISTAKE_KEYS))
    async def check_mistake(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['final'])
            await session.commit()
        await message.reply(msg.MISTAKE_MSG)

    @on.message(F.text.lower().in_(msg.ANOTHER_KEY))
    async def check_another_key(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['final'])
            await session.commit()
        await message.answer(msg.ANOTHER_MSG)

    @on.message(F.text.lower().in_(msg.FINAL_ACT_KEY))
    async def check_code(self, message: Message) -> None:
        async with async_session() as session:
            user_manager = CompositeManager(session)
            await user_manager.write_history(message, setting.ACT_STATE['final'])
            tg_id = message.from_user.id
            user = await user_manager.get_user_by_id(tg_id)
            user.act_code = setting.ACT_CODE['present']
            await session.commit()
        await message.reply(msg.FINAL_FOUND_CODE_MSG)
        await self.wizard.goto(setting.ACT_STATE['present'])

    @on.message(F.text.lower() == str(const.HINT))
    async def get_hint(self, message: Message, bot: Bot) -> None:
        await send_hint(message, bot, msg.FINAL_ACT_HINT, 'hint_final.PNG')

    @on.message()
    async def fallback(self, message: Message) -> None:
        await message.reply(msg.UNKNOWN_MSG_SCENE)


class PresentScene(Scene, state=setting.ACT_STATE['present']):
    @on.message.enter()
    async def str_msg(self, message: Message) -> None:
        await asyncio.sleep(2)
        await message.answer(msg.PRESENT_MSG)


main_registry.add(
    PreCheckScene,
    StartScene,
    InfoScene,
    FirstActScene,
    SecondActScene,
    ThirdActScene,
    FinalActScene,
    PresentScene
)
main_router.message.register(
    PreCheckScene.as_handler(),
    CommandStart()
)
main_router.message.register(
    StartScene.as_handler(),
    F.text.lower().in_(msg.START_WORDS)
)
main_router.callback_query.register(
    InfoScene.as_handler(),
    F.data == const.START_QUEST_CMD
)
main_router.callback_query.register(
    FirstActScene.as_handler(),
    F.data == setting.ACT_STATE['1']
)
main_router.callback_query.register(
    SecondActScene.as_handler(),
    F.data == setting.ACT_STATE['2']
)
main_router.callback_query.register(
    ThirdActScene.as_handler(),
    F.data == setting.ACT_STATE['3']
)
main_router.callback_query.register(
    FinalActScene.as_handler(),
    F.data == setting.ACT_STATE['final']
)
main_router.callback_query.register(
    FinalActScene.as_handler(),
    F.data == setting.ACT_STATE['present']
)
