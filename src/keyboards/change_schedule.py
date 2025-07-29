from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.keyboards.calendar import WEEKDAYS
from src.models import ScheduleSettings


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


def create_weekday_kb(schedule_settings: ScheduleSettings) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, weekday in enumerate(WEEKDAYS):
        builder.button(
            text=f"{
                '🟢 рабочий'
                if index in schedule_settings.working_days
                else '🔴 выходной'
            } {weekday}",
            callback_data=f"set_weekday_{index}",
        )

    builder.button(text="Сохранить", callback_data="save_weekdays")
    builder.adjust(1)

    return builder.as_markup()
