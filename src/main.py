import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src.config import settings
from src.exceptions.token import TokenNotFoundError
from src.middlewares.db import DatabaseMiddleware
from src.middlewares.schedule_service import ScheduleServiceMiddleware
from src.middlewares.user_service import UserServiceMiddleware
from src.routers import router
from src.static_commands import commands


async def main() -> None:
    token = settings.BOT_TOKEN
    if not token:
        raise TokenNotFoundError("Не найден токен telegram")

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
    dp.update.middleware(UserServiceMiddleware())
    dp.update.middleware(ScheduleServiceMiddleware())

    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d"
        " %(levelname)-7s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    await dp.start_polling(bot)
    await bot.set_my_commands(commands=commands)


if __name__ == "__main__":
    asyncio.run(main())
