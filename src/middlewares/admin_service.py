from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from src.services.admin import AdminService


class AdminServiceMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.admin_service = AdminService()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        data["admin_service"] = self.admin_service
        return await handler(event, data)
