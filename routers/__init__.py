__all__ = ("router",)

from aiogram import Router

from routers.callbacks import router as callback_router
from routers.commands import router as commands_router

router = Router(name="global")
router.include_routers(commands_router, callback_router)
