from aiogram import Bot
from aiogram.types import FSInputFile, Message

import src.settings as setting


async def send_hint(
        message: Message,
        bot: Bot, hint_text: str,
        photo_name: str
) -> None:
    await message.reply(hint_text)
    photo_path = setting.BASE_DIR / 'src' / 'bot' / 'media' / photo_name
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=FSInputFile(photo_path)
    )
