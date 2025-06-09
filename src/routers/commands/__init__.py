__all__ = ("router",)

from aiogram import Router

from src.routers.commands.admin import router as admin_command_router
from src.routers.commands.book import router as book_command_router
from src.routers.commands.info import router as info_command_router
from src.routers.commands.start import router as start_command_router

router = Router(name=__name__)
router.include_routers(
    admin_command_router,
    book_command_router,
    start_command_router,
    info_command_router,
)
