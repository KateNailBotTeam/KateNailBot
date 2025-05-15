__all__ = ("router",)

from aiogram import Router

from routers.commands.base_commands import router as base_commands_router

router = Router(name=__name__)
router.include_router(base_commands_router)