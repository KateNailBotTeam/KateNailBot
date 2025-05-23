__all__ = ("router",)

from aiogram import Router

from src.routers.commands.admin import router as admin_commands_router
from src.routers.commands.base import router as base_commands_router

router = Router(name=__name__)
router.include_routers(base_commands_router, admin_commands_router)
