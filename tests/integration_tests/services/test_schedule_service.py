# ruff: noqa: PLR0913
from datetime import date, datetime, time, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import BookingDateError, BookingTimeError
from src.models.schedule import Schedule
from src.models.user import User
from src.services.schedule import ScheduleService


@pytest.mark.asyncio
async def test_show_user_schedules(
    session: AsyncSession,
    schedule_service: ScheduleService,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
):
    visit_date = available_dates[-1]
    visit_time = time_slots[0]

    for user in create_users:
        await schedule_service.mark_slot_busy(
            session=session,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user.telegram_id,
            duration=schedule_service.DEFAULT_SLOT_DURATION,
        )

        schedules = await schedule_service.show_user_schedules(
            session=session, user_telegram_id=user.telegram_id
        )

        assert len(schedules) == 1
        assert datetime.combine(visit_date, visit_time) in schedules


@pytest.mark.asyncio
async def test_is_slot_available_for_free_slot(
    session: AsyncSession,
    schedule_service: ScheduleService,
    available_dates: list[date],
):
    for visit_date in available_dates:
        for visit_time in schedule_service.get_time_slots(visit_date):
            assert (
                await schedule_service.is_slot_available(
                    session=session, visit_date=visit_date, visit_time=visit_time
                )
                is True
            )


@pytest.mark.asyncio
async def test_is_slot_available_for_busy_slot(
    session: AsyncSession,
    schedule_service: ScheduleService,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
):
    visit_date = available_dates[0]
    visit_time = time_slots[0]
    user = create_users[0]

    booked_slot = Schedule(
        visit_datetime=datetime.combine(visit_date, visit_time),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )

    session.add(booked_slot)
    await session.commit()

    is_slot_available = await schedule_service.is_slot_available(
        session=session, visit_date=visit_date, visit_time=visit_time
    )

    assert is_slot_available is False


@pytest.mark.parametrize(
    "date_offset, expected_error",
    [
        (-1, BookingDateError),
        (+1, BookingDateError),
    ],
    ids=["before_first_available", "after_last_available"],
)
@pytest.mark.asyncio
async def test_is_slot_available_with_invalid_dates(
    session: AsyncSession,
    schedule_service: ScheduleService,
    available_dates: list[date],
    time_slots: list[time],
    date_offset: int,
    expected_error: type[Exception],
    create_users: list[User],
):
    user = create_users[-1]

    test_date = (
        available_dates[0] + timedelta(days=date_offset)
        if date_offset < 0
        else available_dates[-1] + timedelta(days=date_offset)
    )

    with pytest.raises(expected_error):
        await schedule_service.mark_slot_busy(
            session=session,
            visit_date=test_date,
            visit_time=time_slots[0],
            user_telegram_id=user.telegram_id,
        )


@pytest.mark.parametrize(
    "time_offset, expected_error",
    [
        (-ScheduleService.DEFAULT_SLOT_DURATION, BookingTimeError),
        (+ScheduleService.DEFAULT_SLOT_DURATION, BookingTimeError),
    ],
    ids=["before_first_available", "after_last_available"],
)
@pytest.mark.asyncio
async def test_is_slot_available_with_invalid_time(
    session: AsyncSession,
    schedule_service: ScheduleService,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
    time_offset: int,
    expected_error: type[Exception],
):
    user = create_users[-1]
    visit_date = available_dates[0]
    if time_offset < 0:
        visit_time = (
            datetime.combine(visit_date, time_slots[0]) + timedelta(minutes=time_offset)
        ).time()
    else:
        visit_time = (
            datetime.combine(visit_date, time_slots[-1])
            + timedelta(minutes=time_offset)
        ).time()

    with pytest.raises(expected_error):
        await schedule_service.mark_slot_busy(
            session=session,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user.telegram_id,
        )
