from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from src.services.user import UserService


class UserServiceMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.user_service = UserService()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        data["user_service"] = self.user_service
        return await handler(event, data)
