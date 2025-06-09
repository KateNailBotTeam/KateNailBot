from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from database.database import get_session


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Awaitable[Any]:
        async for session in get_session():
            data["session"] = session
            return await handler(event, data)
        return await handler(event, data)
