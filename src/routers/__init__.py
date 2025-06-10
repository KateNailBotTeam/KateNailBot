__all__ = ("router",)

from aiogram import Router

from src.routers.commands import router as commands_router
from src.routers.handlers import router as callback_router

router = Router(name="global")
router.include_routers(commands_router, callback_router)
