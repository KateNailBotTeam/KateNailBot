from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.keyboards.change_schedule import create_change_schedule_keyboard

router = Router(name=__name__)


@router.callback_query(F.data == "change_schedule")
async def change_schedule(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message) and isinstance(callback.message.text, str):
        await callback.message.edit_text(
            text=callback.message.text, reply_markup=create_change_schedule_keyboard()
        )


@router.callback_query(F.data == "change_bookings")
async def change_bookings(callback: CallbackQuery) -> None:
    _ = callback


@router.callback_query(F.data == "show_all_bookings")
async def show_all_bookings(callback: CallbackQuery) -> None:
    _ = callback
