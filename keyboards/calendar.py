import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

RU_MONTHS = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}


def create_month_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    kb = []

    kb.append([InlineKeyboardButton(text=f"📅{RU_MONTHS.get(month, "Нет данных")} ", callback_data="ignore")])

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in weekdays])

    for week in month_days:
        temp_kb = []
        for day in week:
            if day == 0:
                temp_kb.append(InlineKeyboardButton(text=' ', callback_data="ignore"))
            else:
                temp_kb.append(InlineKeyboardButton(text=f"{day}", callback_data='day'))
        kb.append(temp_kb)

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
