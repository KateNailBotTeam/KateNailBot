from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.telegram_object import InvalidCallbackError
from src.keyboards.admin import create_all_bookings_keyboard
from src.services.admin import AdminService

router = Router(name=__name__)


@router.callback_query(F.data == "show_all_bookings")
async def show_all_bookings(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidCallbackError("callback.message должен быть объектом Message")

    bookings = await admin_service.get_all_bookings(session=session)

    await callback.message.edit_text(
        text="Все записи клиентов", reply_markup=create_all_bookings_keyboard(bookings)
    )
