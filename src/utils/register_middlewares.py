from aiogram import Dispatcher

from src.middlewares.admin_service import AdminServiceMiddleware
from src.middlewares.db import DatabaseMiddleware
from src.middlewares.schedule_service import ScheduleServiceMiddleware
from src.middlewares.user_service import UserServiceMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserServiceMiddleware())
    dp.update.middleware(ScheduleServiceMiddleware())
    dp.update.middleware(AdminServiceMiddleware())
