from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models.schedule import Schedule
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS


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
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


def create_all_bookings_keyboard(schedules: list[Schedule]) -> InlineKeyboardMarkup:
    kb = []

    for schedule in schedules:
        visit_datetime_str = schedule.visit_datetime.strftime("%d.%m.%y %H:%M")

        status = APPOINTMENT_TYPE_STATUS.get(schedule.is_approved)

        button = [
            InlineKeyboardButton(
                text=f"{status} {visit_datetime_str}",
                callback_data=f"schedule_{schedule.id}",
            )
        ]
        kb.append(button)

    kb.append([InlineKeyboardButton(text="ВЫХОД", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def create_status_update_keyboard(
    schedule_id: int, telegram_id: int | None
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data=f"accept_{schedule_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить", callback_data=f"reject_{schedule_id}"
            ),
            InlineKeyboardButton(
                text="⏳ Ожидание", callback_data=f"pending_{schedule_id}"
            ),
        ]
    ]

    if telegram_id is not None:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="📨 Связаться с пользователем",
                    url=f"tg://user?id={telegram_id}",
                )
            ]
        )

    keyboard.append([InlineKeyboardButton(text="🚪 ВЫХОД", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
