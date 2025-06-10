from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ask_about_name_kb() -> InlineKeyboardMarkup:
    inline_kb = [
        [
            InlineKeyboardButton(text="Оставить", callback_data="profile_keep_name"),
            InlineKeyboardButton(text="Изменить", callback_data="profile_change_name"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)

    return keyboard


def ask_about_phone_kb() -> InlineKeyboardMarkup:
    inline_kb = [
        [
            InlineKeyboardButton(text="Добавить", callback_data="profile_add_phone"),
            InlineKeyboardButton(text="Пропустить", callback_data="profile_skip_phone"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    return keyboard
