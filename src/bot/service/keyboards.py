from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

import src.bot.service.constants as const
import src.settings as setting


def btn_yes() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да!',
                callback_data=const.START_QUEST_CMD
            )
        ]
    ])


def btn_start_first_act() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Активировать первый квест',
                callback_data=setting.ACT_STATE['1']
            )
        ]
    ])
