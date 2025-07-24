import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule_settings import ScheduleSettings

logger = logging.getLogger(__name__)


class ScheduleSettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        session: AsyncSession = data["session"]

        stmt = select(ScheduleSettings).limit(1)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()

        if not settings:
            logger.error("Настройки расписания не найдены в базе")
            raise RuntimeError("Настройки расписания не найдены")

        data["schedule_settings"] = settings
        return await handler(event, data)
