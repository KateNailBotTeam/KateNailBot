from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_change_schedule_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Установка рабочих/нерабочих дней", callback_data='set_work_days')],
        [InlineKeyboardButton(text="Установка рабочего времени на день или диапазон дней",
                              callback_data='set_work_time')],
        [InlineKeyboardButton(text="Установка нерабочих дней", callback_data="set_free_days")]

    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
