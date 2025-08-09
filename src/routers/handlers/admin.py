import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.telegram_object import InvalidCallbackError, InvalidMessageError
from src.keyboards.admin import (
    create_all_bookings_keyboard,
    create_status_update_keyboard,
    create_workday_selection_keyboard,
)
from src.keyboards.calendar import create_calendar_for_available_dates
from src.keyboards.change_schedule import create_weekday_kb
from src.models import ScheduleSettings
from src.services.admin import AdminService
from src.services.schedule import ScheduleService
from src.states.broadcast_message import BroadcastMessage
from src.states.days import Days
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


@router.callback_query(F.data == "set_first_day")
async def set_first_day(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    schedule_service: ScheduleService,
    schedule_settings: ScheduleSettings,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    available_dates = await schedule_service.get_available_dates(
        session=session,
        schedule_settings=schedule_settings,
        check_days_off=False,
    )
    await callback.message.edit_text(
        text="Выберите первый день",
        reply_markup=create_calendar_for_available_dates(dates=available_dates),
    )

    await state.set_state(Days.first_day)


@router.callback_query(Days.first_day, F.data.startswith("choose_date_"))
async def set_last_day(
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
        session=session, schedule_settings=schedule_settings, check_days_off=False
    )

    await callback.message.edit_text(
        text="Выберете последний день",
        reply_markup=create_calendar_for_available_dates(dates=available_dates),
    )

    await state.set_state(Days.last_day)

    first_day_str = callback.data.replace("choose_date_", "")
    await state.update_data(first_day_str=first_day_str)


@router.callback_query(Days.last_day, F.data.startswith("choose_date_"))
async def choose_dates_to_change_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    if not isinstance(callback.data, str):
        raise InvalidCallbackError("Данные в callback.data не являются типом str")

    data = await state.get_data()

    first_day_str = data.get("first_day_str")
    if not first_day_str:
        raise ValueError("Не передан первый день")

    last_day_str = callback.data.replace("choose_date_", "")

    first_day = datetime.strptime(first_day_str, "%Y_%m_%d").date()
    last_day = datetime.strptime(last_day_str, "%Y_%m_%d").date()

    if last_day < first_day:
        await callback.answer(
            "Последний день не может быть раньше первого. Повторите выбор.",
            show_alert=True,
        )
        await state.set_state(Days.first_day)
        return

    await state.update_data(last_day_str=last_day_str)
    await state.set_state(Days.apply_changes)

    await callback.message.edit_text(
        text=rf"Вы выбрали дни с <b>{first_day.strftime('%d.%m.%Y')}</b> "
        rf"по <b>{last_day.strftime('%d.%m.%Y')}</b>.",
        reply_markup=create_workday_selection_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(Days.apply_changes, F.data.startswith("set_days_"))
async def set_days(
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
    first_day_str = data.get("first_day_str")
    last_day_str = data.get("last_day_str")

    if not first_day_str:
        raise ValueError("Не передан первый день")

    if not last_day_str:
        raise ValueError("Не передан последний день")

    first_day = datetime.strptime(first_day_str, "%Y_%m_%d").date()
    last_day = datetime.strptime(last_day_str, "%Y_%m_%d").date()

    check_type_days = callback.data.replace("set_days_", "")

    if check_type_days == "work":
        is_work = True
    elif check_type_days == "off":
        is_work = False
    else:
        raise ValueError("Неверный тип дня(рабочий или выходной) для установки дней")

    await admin_service.set_workdays(
        first_day=first_day, last_day=last_day, is_work=is_work, session=session
    )

    await callback.message.edit_text(
        text=rf"Установлены {'рабочие' if is_work else 'нерабочие'} дни c "
        rf"<b>{first_day.strftime('%d.%m.%Y')}</b> "
        rf"по <b>{last_day.strftime('%d.%m.%Y')}</b>.",
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "set_working_days_per_week")
async def set_working_days_per_week_handler(
    callback: CallbackQuery,
    schedule_settings: ScheduleSettings,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    await callback.message.edit_text(
        text="<b>Нажмите на день</b> для его <i>изменения</i>",
        reply_markup=create_weekday_kb(schedule_settings),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("set_weekday_"))
async def change_weekday_status(
    callback: CallbackQuery,
    session: AsyncSession,
    admin_service: AdminService,
    schedule_settings: ScheduleSettings,
) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    if not isinstance(callback.data, str):
        raise InvalidCallbackError("Данные в callback.data не являются типом str")

    day_index = int(callback.data.replace("set_weekday_", ""))

    await admin_service.toggle_working_day(
        session=session, day_index=day_index, schedule_settings=schedule_settings
    )

    await callback.message.edit_text(
        text="<b>Нажмите на день</b> для его изменения",
        reply_markup=create_weekday_kb(schedule_settings),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "save_weekdays")
async def save_weekdays(callback: CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    await callback.message.edit_text("✅ Данные успешно сохранены")


@router.callback_query(F.data == "send_message_to_all_client")
async def get_message_from_admin(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        raise InvalidMessageError()

    await callback.message.edit_text(
        "Введите сообщение для отправки <b>всем пользователям</b>",
        parse_mode=ParseMode.HTML,
    )
    await state.update_data(prompt_message_id=callback.message.message_id)
    await state.set_state(BroadcastMessage.waiting_for_text)


@router.message(BroadcastMessage.waiting_for_text, flags={"type_operation": "typing"})
async def send_message_from_admin(
    message: Message,
    state: FSMContext,
    bot: Bot,
    session: AsyncSession,
    admin_service: AdminService,
) -> None:
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)

    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    text_message = message.text.strip()
    sending_info = await admin_service.send_message_from_admin_to_all_users(
        bot=bot, session=session, text_message=text_message
    )
    await message.answer(sending_info)
    await state.clear()
