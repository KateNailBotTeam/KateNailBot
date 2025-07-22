from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_book_main_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Записаться", callback_data="book")],
        [
            InlineKeyboardButton(
                text="Просмотреть мои записи", callback_data="user_bookings"
            )
        ],
        [InlineKeyboardButton(text="Отменить запись", callback_data="cancel_booking")],
        [InlineKeyboardButton(text="ВЫХОД", callback_data="cancel")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


def create_booking_list_kb(schedules: list[datetime]) -> InlineKeyboardMarkup:
    kb = []
    for schedule in schedules:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"🗓 Дата: {schedule.strftime('%d.%m.%Y')}\n"
                    f"⏰ Время: {schedule.strftime('%H:%M')}\n",
                    callback_data=f"cancel_{schedule}",
                )
            ]
        )
    kb.append([InlineKeyboardButton(text="ВЫХОД", callback_data="cancel")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


def create_confirm_cancel_booking_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Да", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="Нет", callback_data="confirm_no")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
