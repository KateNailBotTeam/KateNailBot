from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_admin_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Управление расписанием", callback_data="change_schedule"
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
