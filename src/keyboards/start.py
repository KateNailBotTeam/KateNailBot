from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> InlineKeyboardMarkup:
    inline_kb = [
        [
            InlineKeyboardButton(text="Оставить", callback_data="profile_keep_name"),
            InlineKeyboardButton(text="Изменить", callback_data="profile_change_name"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)

    return keyboard
