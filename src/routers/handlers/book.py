from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.keyboards.calendar import (
    create_calendar_for_available_dates,
    create_choose_time_keyboard,
)
from src.services.schedule import ScheduleService
from src.states.choose_visit_datetime import ChooseVisitDatetime

router = Router(name=__name__)


@router.callback_query(F.data == "book")
async def show_days(
    callback: CallbackQuery, state: FSMContext, schedule_service: ScheduleService
) -> None:
    available_dates = schedule_service.get_available_dates()
    await state.set_state(ChooseVisitDatetime.waiting_for_date)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text="Выберите дату для записи",
            reply_markup=create_calendar_for_available_dates(available_dates),
        )


@router.callback_query(ChooseVisitDatetime.waiting_for_date)
async def show_time(
    callback: CallbackQuery, state: FSMContext, schedule_service: ScheduleService
) -> None:
    if isinstance(callback.data, str) and isinstance(callback.message, Message):
        visit_date_str = callback.data.replace("choose_date_", "")
        visit_date = datetime.strptime(visit_date_str, "%Y_%m_%d").date()

        await state.update_data(visit_date=visit_date_str)
        await state.set_state(ChooseVisitDatetime.waiting_for_time)

        time_slots = schedule_service.get_time_slots(visit_date=visit_date)

        await callback.message.edit_text(
            text="Выберете удобное время",
            reply_markup=create_choose_time_keyboard(
                time_slots, duration=schedule_service.DEFAULT_SLOT_DURATION
            ),
        )


@router.callback_query(ChooseVisitDatetime.waiting_for_time)
async def finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if isinstance(callback.data, str) and isinstance(callback.message, Message):
        visit_time_str = callback.data.replace("timeline_", "")
        await state.update_data(visit_time=visit_time_str)
        await callback.message.answer(text=f"{await state.get_data()}")


@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.message.answer(text="Мои бронирования : ...")


@router.callback_query(F.data == "show_schedule")
async def show_schedule(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.message.answer(
            text="Тут должен быть календарь с расписанием сеансов"
        )
