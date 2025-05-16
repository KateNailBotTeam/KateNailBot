from idlelib.window import add_windows_to_menu

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.calendar import (
    create_choose_month_keyboard,
    create_choose_day_keyboard,
    create_choose_time_keyboard
)

router = Router(name=__name__)


@router.callback_query(F.data == "book")
async def book(callback: CallbackQuery):
    await callback.message.edit_text(text='Выбеерите месяц для записи',
                                     reply_markup=create_choose_month_keyboard(message=callback.message))


@router.callback_query(F.data.regexp(r"^month_(1[0-2]|[1-9])$"))
async def show_month(callback: CallbackQuery):
    keyboard = create_choose_day_keyboard(
        year=callback.message.date.year,
        month=int(callback.data.split('_')[-1])
    )
    await callback.message.edit_text(text="Выберете день", reply_markup=keyboard)


@router.callback_query(F.data.regexp(r"^day_(\d{1,2})$"))
async def show_day(callback: CallbackQuery):
    day = int(callback.data.split('_')[-1])
    await callback.message.edit_text(text="Выберете удобное время", reply_markup=create_choose_time_keyboard())


@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback: CallbackQuery):
    await callback.message.answer(text="Мои бронирования : ...")


@router.callback_query(F.data == "show_schedule")
async def show_schedule(callback: CallbackQuery):
    await callback.message.answer(
        text="Тут должен быть календарь с расписанием сеансов"
    )
