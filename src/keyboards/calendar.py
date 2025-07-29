import calendar
from collections import defaultdict
from datetime import date, time

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.schedule import ScheduleService

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

WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


def build_calendar_section(
    year: int, month: int, available_days: set[int]
) -> list[list[InlineKeyboardButton]]:
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    kb: list[list[InlineKeyboardButton]] = []

    kb.append(
        [
            InlineKeyboardButton(
                text=f"📅 {RU_MONTHS[month]} {year}", callback_data="ignore"
            )
        ]
    )

    kb.append(
        [InlineKeyboardButton(text=day, callback_data="ignore") for day in WEEKDAYS]
    )

    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            elif day in available_days:
                row.append(
                    InlineKeyboardButton(
                        text=str(day), callback_data=f"choose_date_{year}_{month}_{day}"
                    )
                )
            else:
                row.append(InlineKeyboardButton(text="▫️", callback_data="ignore"))
        kb.append(row)

    return kb


def create_calendar_for_available_dates(dates: set[date]) -> InlineKeyboardMarkup:
    grouped: dict[tuple[int, int], set[int]] = defaultdict(set)
    for d in dates:
        grouped[(d.year, d.month)].add(d.day)

    full_kb: list[list[InlineKeyboardButton]] = []

    for year, month in sorted(grouped):
        kb_section = build_calendar_section(year, month, grouped[(year, month)])
        full_kb.extend(kb_section)

    full_kb.append([InlineKeyboardButton(text="ВЫХОД", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=full_kb)


async def create_choose_time_keyboard(
    time_slots: list[time],
    session: AsyncSession,
    schedule_service: ScheduleService,
    visit_date: date,
) -> InlineKeyboardMarkup:
    busy_datetimes = await schedule_service.get_booking_slots_for_date(
        session=session, visit_date=visit_date
    )
    busy_times = {value.time() for value in busy_datetimes}

    kb = []
    for time_slot in time_slots:
        time_to_text = time_slot.strftime("%H:%M")
        is_available = time_slot not in busy_times
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"🟢 {time_to_text}"
                    if is_available
                    else f"🔴 Время {time_to_text} занято",
                    callback_data=f"timeline_{time_to_text}"
                    if is_available
                    else "unavailable_time",
                )
            ]
        )

    kb.append([InlineKeyboardButton(text="ВЫХОД", callback_data="cancel")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
