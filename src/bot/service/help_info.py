from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import src.bot.service.msg_text as msg

help_info_router = Router()


@help_info_router.message(Command('info'))
async def info_cmd(message: Message):
    return message.reply(msg.INFO_MESSAGE)


@help_info_router.message(Command('help'))
async def help_cmd(message: Message):
    return message.reply(msg.HELP_MESSAGE)


@help_info_router.message(F.text.lower().in_(msg.HELP_WORDS))
async def help_msg(message: Message):
    return message.reply(msg.HELP_MESSAGE)
