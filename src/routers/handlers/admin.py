import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.telegram_object import InvalidCallbackError, InvalidMessageError
from src.keyboards.admin import (
    create_all_bookings_keyboard,
    create_status_update_keyboard,
)
from src.keyboards.calendar import create_calendar_for_available_dates
from src.models import ScheduleSettings
from src.services.admin import AdminService
from src.services.schedule import ScheduleService
from src.states.days_off import DaysOff
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "show_all_bookings")
async def show_all_bookings(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    logger.info("Пользователь %s запросил все записи", callback.from_user.id)

    if not isinstance(callback.message, Message):
        logger.error("Неверный тип callback.message в show_all_bookings")
        raise InvalidCallbackError()

    bookings = await admin_service.get_all_bookings(session=session)
    logger.debug("Найдено записей: %d", len(bookings))

    await callback.message.edit_text(
        text="Записи и информация о клиентах",
        reply_markup=create_all_bookings_keyboard(schedules=bookings),
    )


@router.callback_query(F.data.startswith("schedule_"))
async def on_schedule_click(
    callback: CallbackQuery, session: AsyncSession, admin_service: AdminService
) -> None:
    logger.info(
        "Пользователь %s открыл запись: %s", callback.from_user.id, callback.data
    )
    if not isinstance(callback.data, str):
        logger.error("callback.data не является строкой")
        raise TypeError("Ошибка в типе callback.data, должен быть строкой")

    if not isinstance(callback.message, Message):
        logger.error("Неверный тип callback.message в on_schedule_click")
        raise InvalidMessageError()

    schedule_id = int(callback.data.split("_")[1])
    schedule = await admin_service.get_booking(session=session, booking_id=schedule_id)
    if not schedule:
        logger.warning("Запись с ID %d не найдена", schedule_id)
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
    logger.info(
        "Пользователь %s изменяет статус: %s", callback.from_user.id, callback.data
    )
    if not isinstance(callback.data, str):
        logger.error("callback.data не является строкой в on_status_change")
        raise TypeError("Ошибка в типе callback.data, должен быть строкой")

    if not isinstance(callback.message, Message):
        logger.error("Неверный тип callback.message в on_status_change")
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
    logger.info(
        "Пользователь %s изменил статус записи %d на %s",
        callback.from_user.id,
        schedule_id,
        action,
    )


@router.callback_query(F.data == "set_days_off")
async def set_first_day_off(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    schedule_service: ScheduleService,
    schedule_settings: ScheduleSettings,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    available_dates = await schedule_service.get_available_dates(
        session=session, schedule_settings=schedule_settings
    )
    await callback.message.edit_text(
        text="Выберите первый нерабочий день",
        reply_markup=create_calendar_for_available_dates(dates=available_dates),
    )

    await state.set_state(DaysOff.first_day_off)


@router.callback_query(DaysOff.first_day_off, F.data.startswith("choose_date_"))
async def set_last_day_off(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    schedule_service: ScheduleService,
    schedule_settings: ScheduleSettings,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    if not isinstance(callback.data, str):
        raise InvalidCallbackError("Данные в callback.data не являются типом str")

    available_dates = await schedule_service.get_available_dates(
        session=session, schedule_settings=schedule_settings
    )

    await callback.message.edit_text(
        text="Выберете последний нерабочий день",
        reply_markup=create_calendar_for_available_dates(dates=available_dates),
    )

    await state.set_state(DaysOff.last_day_off)

    first_day_off_str = callback.data.replace("choose_date_", "")
    await state.update_data(first_day_off_str=first_day_off_str)


@router.callback_query(DaysOff.last_day_off, F.data.startswith("choose_date_"))
async def set_days_off_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    admin_service: AdminService,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    if not isinstance(callback.data, str):
        raise InvalidCallbackError("Данные в callback.data не являются типом str")

    data = await state.get_data()

    first_day_off_str = data.get("first_day_off_str")
    if not first_day_off_str:
        raise ValueError("Не передан первый нерабочий день")

    last_day_off_str = callback.data.replace("choose_date_", "")

    first_day_off = datetime.strptime(first_day_off_str, "%Y_%m_%d").date()
    last_day_off = datetime.strptime(last_day_off_str, "%Y_%m_%d").date()

    if last_day_off < first_day_off:
        await callback.answer(
            "Последний день не может быть раньше первого. Повторите выбор.",
            show_alert=True,
        )
        await state.set_state(DaysOff.first_day_off)
        return

    await admin_service.set_days_off(
        first_day_off=first_day_off,
        last_day_off=last_day_off,
        session=session,
    )

    await callback.message.edit_text(
        text=f"Вы установили нерабочие дни с {first_day_off_str} по {last_day_off_str}."
    )
