from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models.schedule import Schedule
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS


def create_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Управление записями", callback_data="show_all_bookings")
    builder.button(
        text="🗓️ Управление рабочими/нерабочими днями", callback_data="set_first_day"
    )
    builder.button(
        text="⚙️ Установить рабочие дни в неделе",
        callback_data="set_working_days_per_week",
    )
    builder.button(
        text="📤 Сделать рассылку по клиентам",
        callback_data="send_message_to_all_client",
    )

    builder.button(
        text=r"✍🏻 Изменить описание в /info", callback_data="change_info_text"
    )

    builder.button(text="❌ ВЫХОД", callback_data="cancel")

    builder.adjust(1)

    return builder.as_markup()


def create_workday_selection_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📅 Установить как рабочие дни", callback_data="set_days_work")
    builder.button(text="🚫 Установить как нерабочие дни", callback_data="set_days_off")
    builder.button(text="❌ ВЫХОД", callback_data="cancel")

    builder.adjust(1)

    return builder.as_markup()


def create_all_bookings_keyboard(schedules: list[Schedule]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for schedule in schedules:
        visit_datetime_str = schedule.visit_datetime.strftime("%d.%m.%y %H:%M")

        status = APPOINTMENT_TYPE_STATUS.get(schedule.is_approved)

        builder.button(
            text=f"{status} {visit_datetime_str}",
            callback_data=f"schedule_{schedule.id}",
        )

    builder.button(text="ВЫХОД", callback_data="cancel")

    builder.adjust(1)

    return builder.as_markup()


def create_status_update_keyboard(
    schedule_id: int, telegram_id: int | None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Подтвердить", callback_data=f"accept_{schedule_id}")
    builder.button(text="❌ Отклонить", callback_data=f"reject_{schedule_id}")
    builder.button(text="⏳ Ожидание", callback_data=f"pending_{schedule_id}")

    if telegram_id is not None:
        builder.button(
            text="📨 Связаться с пользователем",
            url=f"tg://user?id={telegram_id}",
        )
    builder.button(text="🚪 ВЫХОД", callback_data="cancel")

    builder.adjust(3, 1, 1)
    return builder.as_markup()


def confirm_change_info_text_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Подтвердить", callback_data="confirm_change_info_text")
    builder.button(text="Изменить", callback_data="change_info_text")
    builder.button(text="🚪 ВЫХОД", callback_data="cancel")

    builder.adjust(1)
    return builder.as_markup()
