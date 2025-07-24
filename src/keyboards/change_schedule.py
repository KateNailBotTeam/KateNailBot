from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_change_schedule_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Установка рабочих/нерабочих дней", callback_data="set_work_days"
    )
    builder.button(
        text="Установка рабочего времени на день или диапазон дней",
        callback_data="set_work_time",
    )
    builder.button(text="Установка нерабочих дней", callback_data="set_free_days")
    builder.adjust(1)
    return builder.as_markup()
