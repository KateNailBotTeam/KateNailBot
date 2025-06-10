import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src.config import settings
from src.middlewares.db_middleware import DatabaseMiddleware
from src.routers import router
from src.static import commands


async def main() -> None:
    token = settings.BOT_TOKEN
    if token:
        redis = Redis(
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASSWORD,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DATABASE,
            decode_responses=True,
        )
        storage = RedisStorage(redis=redis)

        bot = Bot(token=token)
        dp = Dispatcher(storage=storage)

        dp.include_routers(router)
        dp.update.middleware(DatabaseMiddleware())

        logging.basicConfig(level=logging.DEBUG)

        await dp.start_polling(bot)
        await bot.set_my_commands(commands=commands)


if __name__ == "__main__":
    asyncio.run(main())
