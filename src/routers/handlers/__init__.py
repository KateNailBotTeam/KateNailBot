__all__ = ("router",)

from aiogram import Router

from src.routers.handlers.admin import router as admin_callback_router
from src.routers.handlers.book import router as booking_callback_router
from src.routers.handlers.start import router as start_callback_router

router = Router(name=__name__)
router.include_routers(
    booking_callback_router,
    admin_callback_router,
    start_callback_router,
)
