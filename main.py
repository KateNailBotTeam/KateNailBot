import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from routers.callbacks import router as callbacks_router
from routers import router


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(router, callbacks_router)
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
