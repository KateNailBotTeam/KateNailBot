import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

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


def create_choose_month_keyboard(message: Message) -> InlineKeyboardMarkup:
    this_month = message.date.month
    next_month = (this_month % 12) + 1

    kb = [
        [
            InlineKeyboardButton(
                text=f"📆 {RU_MONTHS[this_month]}", callback_data=f"month_{this_month}"
            ),
            InlineKeyboardButton(
                text=f"➡️ {RU_MONTHS[next_month]}", callback_data=f"month_{next_month}"
            ),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def create_choose_day_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    kb = []

    kb.append(
        [
            InlineKeyboardButton(
                text=f"📅 {RU_MONTHS.get(month, 'Нет данных')}", callback_data="ignore"
            )
        ]
    )

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.append(
        [
            InlineKeyboardButton(text=f"{day}", callback_data="ignore")
            for day in weekdays
        ]
    )

    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(
                    InlineKeyboardButton(text=f"{day}", callback_data=f"day_{day}")
                )
        kb.append(row)

    return InlineKeyboardMarkup(inline_keyboard=kb)


def create_choose_time_keyboard() -> InlineKeyboardMarkup:
    kb = []
    for timeline in range(10, 22):
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{timeline}:00 - {timeline + 1}:00",
                    callback_data=f"timeline_{timeline}",
                )
            ]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
