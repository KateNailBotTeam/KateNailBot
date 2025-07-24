from datetime import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_book_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Записаться", callback_data="book")
    builder.button(text="Просмотреть мои записи", callback_data="user_bookings")
    builder.button(text="Отменить запись", callback_data="cancel_booking")
    builder.button(text="ВЫХОД", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()


def create_booking_list_kb(schedules: list[datetime]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for schedule in schedules:
        builder.button(
            text=f"🗓 Дата: {schedule.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {schedule.strftime('%H:%M')}\n",
            callback_data=f"cancel_{schedule}",
        )
    builder.button(text="ВЫХОД", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()


def create_confirm_cancel_booking_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="confirm_yes")
    builder.button(text="Нет", callback_data="confirm_no")
    builder.adjust(1)
    return builder.as_markup()
