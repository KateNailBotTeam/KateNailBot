import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import settings
from src.middlewares.db_middleware import DatabaseMiddleware
from src.routers import router
from src.static import commands


async def main() -> None:
    token = settings.BOT_TOKEN
    if token:
        bot = Bot(token=token)
        dp = Dispatcher()

        dp.include_routers(router)
        dp.update.middleware(DatabaseMiddleware())

        logging.basicConfig(level=logging.DEBUG)

        await dp.start_polling(bot)
        await bot.set_my_commands(commands=commands)


if __name__ == "__main__":
    asyncio.run(main())
