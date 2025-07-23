from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.telegram_object import InvalidCallbackError, InvalidMessageError
from src.keyboards.admin import (
    create_all_bookings_keyboard,
    create_status_update_keyboard,
)
from src.services.admin import AdminService
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS

router = Router(name=__name__)


@router.callback_query(F.data == "show_all_bookings")
async def show_all_bookings(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidCallbackError()

    bookings = await admin_service.get_all_bookings(session=session)

    await callback.message.edit_text(
        text="Записи и информация о клиентах",
        reply_markup=create_all_bookings_keyboard(schedules=bookings),
    )


@router.callback_query(F.data.startswith("schedule_"))
async def on_schedule_click(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    if not isinstance(callback.data, str):
        raise TypeError("Ошибка в типе callback.data, должен быть строкой")

    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    schedule_id = int(callback.data.split("_")[1])
    schedule = await admin_service.get_booking(session=session, booking_id=schedule_id)
    if not schedule:
        raise ValueError(f"Не найдена запись по ID: {schedule_id}")

    text = (
        f"📄 Запись: №{schedule.id}\n"
        f"👤 Пользователь: {schedule.user.first_name}\n"
        f"☺ Ник: {schedule.user.username if schedule.user.username else '-'}\n"
        f"📞 Телефон: {schedule.user.phone if schedule.user.phone else '-'}\n"
        f"📅 Дата и время: {schedule.visit_datetime:%d.%m.%Y %H:%M}\n"
        f"📝 Статус: {APPOINTMENT_TYPE_STATUS.get(schedule.is_approved)}"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_status_update_keyboard(
            schedule_id=schedule_id, telegram_id=schedule.user_telegram_id
        ),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.regexp(r"^(accept|reject|pending)_(\d+)$"))
async def on_status_change(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    if not isinstance(callback.data, str):
        raise TypeError("Ошибка в типе callback.data, должен быть строкой")

    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    action, schedule_id_str = callback.data.split("_")
    schedule_id = int(schedule_id_str)

    status_map = {"accept": True, "reject": False, "pending": None}
    new_status = status_map[action]

    await admin_service.set_booking_approval(
        session=session, schedule_id=schedule_id, approved=new_status
    )

    await callback.answer(
        text=f"Статус изменен: {APPOINTMENT_TYPE_STATUS.get(new_status)}",
        show_alert=True,
    )

    await callback.message.delete()
