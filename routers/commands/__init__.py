__all__ = ("router",)

from aiogram import Router

from routers.commands.admin import router as admin_router
from routers.commands.base import router as base_commands_router

router = Router(name=__name__)
router.include_routers(base_commands_router, admin_router)
