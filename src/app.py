import asyncio

from aiogram import Bot, Dispatcher

from src.bot.service.errors import error_router
from src.bot.service.help_info import help_info_router
from src.bot.main import main_router
from logs.config import bot_logger
from settings import TELEGRAM_TOKEN

dp = Dispatcher()


@bot_logger.catch()
async def main() -> None:
    bot = Bot(token=TELEGRAM_TOKEN)
    dp.include_routers(
        help_info_router,
        main_router,
        error_router
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    bot_logger.info('Bot Start')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.exception('Bot has ended')
