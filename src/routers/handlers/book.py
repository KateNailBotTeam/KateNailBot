from datetime import datetime

from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import (
    BookingDateNotFoundError,
    BookingError,
    UserTelegramIDNotFoundError,
)
from src.keyboards.book import create_booking_list_kb, create_confirm_cancel_booking_kb
from src.keyboards.calendar import (
    create_calendar_for_available_dates,
    create_choose_time_keyboard,
)
from src.services.schedule import ScheduleService
from src.states.cancel_booking import CancelBooking
from src.states.choose_visit_datetime import ChooseVisitDatetime

router = Router(name=__name__)


@router.callback_query(F.data == "book")
async def show_days(
    callback: CallbackQuery, state: FSMContext, schedule_service: ScheduleService
) -> None:
    await callback.answer()

    available_dates = schedule_service.get_available_dates()

    await state.set_state(ChooseVisitDatetime.waiting_for_date)
    await state.update_data(telegram_id=callback.from_user.id)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text="Выберите дату для записи",
            reply_markup=create_calendar_for_available_dates(available_dates),
        )


@router.callback_query(
    ChooseVisitDatetime.waiting_for_date, F.data.startswith("choose_date_")
)
async def show_time(
    callback: CallbackQuery, state: FSMContext, schedule_service: ScheduleService
) -> None:
    if isinstance(callback.data, str) and isinstance(callback.message, Message):
        await callback.answer()

        visit_date_str = callback.data.replace("choose_date_", "")
        visit_date = datetime.strptime(visit_date_str, "%Y_%m_%d").date()

        await state.update_data(visit_date_str=visit_date_str)
        await state.set_state(ChooseVisitDatetime.waiting_for_time)

        time_slots = schedule_service.get_time_slots(visit_date=visit_date)

        await callback.message.edit_text(
            text="Выберете удобное время",
            reply_markup=create_choose_time_keyboard(time_slots),
        )


@router.callback_query(
    ChooseVisitDatetime.waiting_for_time, F.data.startswith("timeline_")
)
async def finish_booking(
    callback: CallbackQuery,
    state: FSMContext,
    schedule_service: ScheduleService,
    session: AsyncSession,
) -> None:
    if isinstance(callback.data, str) and isinstance(callback.message, Message):
        try:
            await callback.answer()

            visit_time_str = callback.data.replace("timeline_", "")
            visit_time = datetime.strptime(visit_time_str, "%H:%M").time()

            data = await state.get_data()
            visit_date_str = data.get("visit_date_str")
            user_telegram_id = data.get("telegram_id")

            if not visit_date_str:
                raise BookingDateNotFoundError()

            if not user_telegram_id:
                raise UserTelegramIDNotFoundError()

            visit_date = datetime.strptime(visit_date_str, "%Y_%m_%d").date()

            await schedule_service.mark_slot_busy(
                session=session,
                visit_date=visit_date,
                visit_time=visit_time,
                user_telegram_id=user_telegram_id,
            )

            await callback.message.edit_text(
                text=f"✅ Вы успешно записаны на"
                f" <b>{visit_date.strftime('%d.%m.%Y')}</b>,"
                f" время <b>{visit_time.strftime('%H:%M')}</b>",
                parse_mode=ParseMode.HTML,
            )

        except BookingError as e:
            await callback.message.edit_text(text=f"Ошибка при записи. {e}")

    await state.clear()


@router.callback_query(F.data == "user_bookings")
async def my_bookings(
    callback: CallbackQuery, schedule_service: ScheduleService, session: AsyncSession
) -> None:
    if isinstance(callback.message, Message):
        user_telegram_id = callback.from_user.id
        schedules = await schedule_service.show_user_schedules(
            session=session, user_telegram_id=user_telegram_id
        )

        if not schedules:
            await callback.message.edit_text(
                text="✨ У вас пока нет записей.\n\n"
                "Хотите записаться на услугу? Нажмите /book",
                parse_mode=ParseMode.HTML,
            )
            return

        message_text = [
            "🌸 <b>Ваши ближайшие записи</b> 🌸\n",
            "————————————————",
            *[
                f"\n<b>📌 Запись №{index}</b>\n"
                f"🗓 <i>Дата:</i> <b>{schedule.strftime('%d.%m.%Y')}</b>\n"
                f"⏰ <i>Время:</i> <code>{schedule.strftime('%H:%M')}</code>\n"
                f"————————————————"
                for index, schedule in enumerate(schedules, 1)
            ],
        ]

        await callback.message.edit_text(
            text="".join(message_text), parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data == "cancel_booking")
async def choose_date_for_cancel_booking(
    callback: CallbackQuery,
    session: AsyncSession,
    schedule_service: ScheduleService,
    state: FSMContext,
) -> None:
    if isinstance(callback.message, Message):
        user_telegram_id = callback.from_user.id
        schedules = await schedule_service.show_user_schedules(
            session=session, user_telegram_id=user_telegram_id
        )

        if not schedules:
            await callback.message.edit_text(
                text="✨ У вас пока нет записей.\n\n"
                "Хотите записаться на услугу? Нажмите /book",
                parse_mode=ParseMode.HTML,
            )
            return

        await state.set_state(CancelBooking.waiting_for_choose_datetime)
        await state.update_data(user_telegram_id=user_telegram_id)

        await callback.message.edit_text(
            text="<b>Выберите запись для отмены:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=create_booking_list_kb(schedules=schedules),
        )


@router.callback_query(
    CancelBooking.waiting_for_choose_datetime, F.data.startswith("cancel_")
)
async def confirm_cancel_booking(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if isinstance(callback.message, Message) and isinstance(callback.data, str):
        datetime_str_to_cancel = callback.data.replace("cancel_", "")
        datetime_to_cancel = datetime.strptime(
            datetime_str_to_cancel, "%Y-%m-%d %H:%M:%S"
        )

        await state.set_state(CancelBooking.waiting_for_cancel_datetime)
        await state.update_data(datetime_str_to_cancel=datetime_str_to_cancel)

        await callback.message.edit_text(
            text=f"Точно отменить запись на 🗓"
            f" <b>{datetime_to_cancel.strftime('%d.%m.%y')}</b>"
            f" в <b>{datetime_to_cancel.strftime('%H:%M')}</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=create_confirm_cancel_booking_kb(),
        )


@router.callback_query(
    CancelBooking.waiting_for_cancel_datetime, F.data.in_(["confirm_yes", "confirm_no"])
)
async def cancel_booking(
    callback: CallbackQuery,
    state: FSMContext,
    schedule_service: ScheduleService,
    session: AsyncSession,
) -> None:
    if isinstance(callback.message, Message):
        try:
            data = await state.get_data()
            datetime_str_to_cancel = data.get("datetime_str_to_cancel")
            user_telegram_id = data.get("user_telegram_id")

            if not datetime_str_to_cancel:
                raise BookingDateNotFoundError()

            if not user_telegram_id:
                raise UserTelegramIDNotFoundError()

            datetime_to_cancel = datetime.strptime(
                datetime_str_to_cancel, "%Y-%m-%d %H:%M:%S"
            )

            if callback.data == "confirm_yes":
                await schedule_service.cancel_booking(
                    session=session,
                    user_telegram_id=user_telegram_id,
                    datetime_to_cancel=datetime_to_cancel,
                )

                await callback.message.edit_text(
                    text=f"✖️ Запись 🗓 <b>{datetime_to_cancel.strftime('%d.%m.%y')}</b>"
                    f" в <b>{datetime_to_cancel.strftime('%H:%M')}</b>"
                    f" успешно удалена.",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await callback.message.edit_text(
                    text=f"Ваша запись 🗓"
                    f" <b>{datetime_to_cancel.strftime('%d.%m.%y')}</b>"
                    f" в <b>{datetime_to_cancel.strftime('%H:%M')}</b>"
                    f" остаётся без изменений.",
                    parse_mode=ParseMode.HTML,
                )

        except BookingError as e:
            await callback.message.edit_text(text=f"{e}")

        finally:
            await state.clear()
