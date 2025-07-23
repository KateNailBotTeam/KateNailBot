from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models.schedule import Schedule


def create_admin_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Посмотреть все записи", callback_data="show_all_bookings"
            )
        ],
        [
            InlineKeyboardButton(
                text="Управление записями", callback_data="change_bookings"
            )
        ],
        [
            InlineKeyboardButton(
                text="Просмотр записей", callback_data="show_all_bookings"
            )
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


def create_all_bookings_keyboard(schedules: list[Schedule]) -> InlineKeyboardMarkup:
    kb = []
    for schedule in schedules:
        button = [
            InlineKeyboardButton(text=f"Запись пользователя {schedule.user.first_name}")
        ]
        kb.append(button)

    return InlineKeyboardMarkup(inline_keyboard=kb)
