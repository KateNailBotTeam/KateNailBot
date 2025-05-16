__all__ = ("router",)

from aiogram import Router

from routers.callbacks.booking import router as booking_router
from routers.callbacks.admin import router as admin_router

router = Router(name=__name__)
router.include_routers(booking_router, admin_router)
