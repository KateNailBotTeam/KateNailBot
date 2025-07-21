# ruff: noqa: PLR0913
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import (
    BookingDateError,
    BookingDeleteError,
    BookingTimeError,
    SlotAlreadyBookedError,
)
from src.models.schedule import Schedule
from src.models.user import User
from src.services.schedule import ScheduleService


@patch("src.services.schedule.datetime")
@patch.object(ScheduleService, "WORKING_DAYS", (0, 1, 2, 3, 4))
@pytest.mark.asyncio
async def test_show_user_schedules(
    mock_datetime,
    session: AsyncSession,
    schedule_service: ScheduleService,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
):
    mock_datetime.now.return_value = datetime(2025, 3, 3, 8, 0, 0)

    user = create_users[0]
    visit_date = available_dates[-1]
    visit_time = time_slots[0]

    booked_slot = Schedule(
        visit_datetime=datetime.combine(visit_date, visit_time),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )

    past_date = datetime(2025, 3, 2).date()
    past_slot = Schedule(
        visit_datetime=datetime.combine(past_date, visit_time),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )

    other_user_slot = Schedule(
        visit_datetime=datetime.combine(visit_date, time_slots[2]),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=create_users[1].telegram_id,
    )

    session.add_all([booked_slot, past_slot, other_user_slot])
    await session.commit()

    schedules = await schedule_service.show_user_schedules(
        session=session, user_telegram_id=user.telegram_id
    )

    assert len(schedules) == 1
    assert schedules[0] == datetime.combine(visit_date, visit_time)


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
        await schedule_service.create_busy_slot(
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
        await schedule_service.create_busy_slot(
            session=session,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user.telegram_id,
        )


@pytest.mark.asyncio
async def test_create_busy_slot(
    session: AsyncSession,
    create_users: list[User],
    schedule_service: ScheduleService,
    available_dates: list[date],
    time_slots: list[time],
):
    user = create_users[-1]
    visit_date = available_dates[-1]
    visit_time = time_slots[0]

    assert await schedule_service.is_slot_available(session, visit_date, visit_time), (
        "Слот должен быть свободен перед тестом"
    )

    await schedule_service.create_busy_slot(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
        user_telegram_id=user.telegram_id,
    )

    stmt = select(Schedule).where(
        Schedule.visit_datetime == datetime.combine(visit_date, visit_time)
    )

    result = await session.execute(stmt)

    user_schedule = result.scalar_one()

    assert user_schedule.user_telegram_id == user.telegram_id
    assert user_schedule.visit_datetime == datetime.combine(visit_date, visit_time)
    assert user_schedule.is_booked is True
    assert user_schedule.visit_duration == schedule_service.DEFAULT_SLOT_DURATION

    is_available_after_book = await schedule_service.is_slot_available(
        session=session, visit_date=visit_date, visit_time=visit_time
    )
    assert not is_available_after_book, "Слот должен быть занят после бронирования"


@pytest.mark.asyncio
async def test_create_busy_slot_already_booked(
    session: AsyncSession,
    create_users: list[User],
    schedule_service: ScheduleService,
    available_dates: list[date],
    time_slots: list[time],
):
    user_1 = create_users[-1]
    user_2 = create_users[-2]
    visit_date = available_dates[-1]
    visit_time = time_slots[0]

    assert await schedule_service.is_slot_available(session, visit_date, visit_time), (
        "Слот должен быть свободен перед тестом"
    )

    await schedule_service.create_busy_slot(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
        user_telegram_id=user_1.telegram_id,
    )

    with pytest.raises(SlotAlreadyBookedError):
        await schedule_service.create_busy_slot(
            session=session,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user_2.telegram_id,
        )


@pytest.mark.asyncio
async def test_cancel_booking(
    session: AsyncSession,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
    schedule_service: ScheduleService,
):
    visit_date = available_dates[2]
    visit_time = time_slots[2]
    user = create_users[2]

    await schedule_service.create_busy_slot(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
        user_telegram_id=user.telegram_id,
    )

    is_slot_available_after_book = await schedule_service.is_slot_available(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
    )

    assert is_slot_available_after_book is False

    await schedule_service.cancel_booking(
        session=session,
        user_telegram_id=user.telegram_id,
        datetime_to_cancel=datetime.combine(visit_date, visit_time),
    )

    is_slot_available_after_cancel = await schedule_service.is_slot_available(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
    )

    assert is_slot_available_after_cancel is True


@pytest.mark.asyncio
async def test_cancel_booking_wrong_user_does_not_cancel(
    session: AsyncSession,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
    schedule_service: ScheduleService,
):
    user_1 = create_users[0]
    user_2 = create_users[1]
    visit_date = available_dates[2]
    visit_time = time_slots[2]

    await schedule_service.create_busy_slot(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
        user_telegram_id=user_1.telegram_id,
    )

    with pytest.raises(BookingDeleteError):
        await schedule_service.cancel_booking(
            session=session,
            user_telegram_id=user_2.telegram_id,
            datetime_to_cancel=datetime.combine(visit_date, visit_time),
        )

    is_available = await schedule_service.is_slot_available(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
    )
    assert is_available is False


@pytest.mark.asyncio
async def test_cancel_booking_not_existing_raises_error(
    session: AsyncSession,
    create_users: list[User],
    available_dates: list[date],
    time_slots: list[time],
    schedule_service: ScheduleService,
):
    user = create_users[0]
    visit_date = available_dates[-1]
    visit_time = time_slots[2]
    visit_datetime = datetime.combine(visit_date, visit_time)

    is_available = await schedule_service.is_slot_available(
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
    )
    assert is_available is True

    with pytest.raises(BookingDeleteError):
        await schedule_service.cancel_booking(
            session=session,
            user_telegram_id=user.telegram_id,
            datetime_to_cancel=visit_datetime,
        )
