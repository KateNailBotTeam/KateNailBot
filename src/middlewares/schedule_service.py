from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from src.services.schedule import ScheduleService


class ScheduleServiceMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.schedule_service = ScheduleService()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        data["schedule_service"] = self.schedule_service
        return await handler(event, data)
