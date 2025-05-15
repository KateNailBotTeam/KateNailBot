__all__ = ("router",)

from aiogram import Router

from routers.commands import router as commands_router
from routers.admin_handlers import router as admin_router

router = Router(name=__name__)
router.include_routers(commands_router, admin_router)
