from aiogram import Router, F
from aiogram.types import Message

from src.bot.service.msg_text import UNKNOWN_MESSAGE

error_router = Router()


@error_router.message(F.text.startswith('/'))
async def unknown_cmd(message: Message) -> None:
    return message.reply(UNKNOWN_MESSAGE)


@error_router.message()
async def unknown_msg(message: Message) -> None:
    return message.reply(UNKNOWN_MESSAGE)
