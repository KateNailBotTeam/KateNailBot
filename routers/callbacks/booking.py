from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router(name=__name__)

@router.callback_query(F.data == "book")
async def book(callback: CallbackQuery):
    await callback.message.answer(text="Тут будет логика бронирования")


@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback:  CallbackQuery):
    await callback.message.answer(text="Мои бронирования : ...")


@router.callback_query(F.data == "show_schedule")
async def show_schedule(callback:  CallbackQuery):
    await callback.message.answer(
        text="Тут должен быть календарь с расписанием сеансов"
    )