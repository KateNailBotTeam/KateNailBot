import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import settings
from src.routers import router
from src.static import commands


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)
    await bot.set_my_commands(commands=commands)


if __name__ == "__main__":
    asyncio.run(main())
