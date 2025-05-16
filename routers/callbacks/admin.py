from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.change_schedule import create_change_schedule_keyboard

router = Router(name=__name__)


@router.callback_query(F.data == "change_schedule")
async def change_schedule(callback: CallbackQuery):
    await callback.message.edit_text(text=callback.message.text, reply_markup=create_change_schedule_keyboard())


@router.callback_query(F.data == "change_bookings")
async def change_bookings(callback: CallbackQuery):
    pass


@router.callback_query(F.data == "show_all_bookings")
async def show_all_bookings(callback: CallbackQuery):
    pass
