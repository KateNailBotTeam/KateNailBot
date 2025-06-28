from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from database.database import session_factory


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        async with session_factory() as session:
            try:
                data["session"] = session
                result = await handler(event, data)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            else:
                return result
