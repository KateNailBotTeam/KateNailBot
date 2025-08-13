from aiogram import Dispatcher
from aiogram.utils.chat_action import ChatActionMiddleware

from src.middlewares.admin_service import AdminServiceMiddleware
from src.middlewares.db import DatabaseMiddleware
from src.middlewares.error_handler import ErrorHandlerMiddleware
from src.middlewares.schedule_service import ScheduleServiceMiddleware
from src.middlewares.schedule_settings import ScheduleSettingsMiddleware
from src.middlewares.user_service import UserServiceMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(ErrorHandlerMiddleware())
    dp.update.middleware(UserServiceMiddleware())
    dp.update.middleware(ScheduleServiceMiddleware())
    dp.update.middleware(ScheduleSettingsMiddleware())
    dp.update.middleware(AdminServiceMiddleware())
    dp.message.middleware(ChatActionMiddleware())
