# ruff: noqa: PLR0913
from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import BookingError
from src.models.schedule import Schedule
from src.models.user import User
from src.services.admin import AdminService
from src.services.schedule import ScheduleService


@patch("src.services.schedule.datetime")
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
    assert schedules[0].visit_datetime == datetime.combine(visit_date, visit_time)


@pytest.mark.asyncio
async def test_is_slot_available_for_free_slot(
    session: AsyncSession,
    schedule_service: ScheduleService,
    available_dates: list[date],
    schedule_settings,
):
    for visit_date in available_dates:
        for visit_time in schedule_service.get_time_slots(
            visit_date, schedule_settings
        ):
            assert (
                await schedule_service.is_slot_available(
                    session=session,
                    visit_date=visit_date,
                    visit_time=visit_time,
                    schedule_settings=schedule_settings,
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
    schedule_settings,
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
        session=session,
        visit_date=visit_date,
        visit_time=visit_time,
        schedule_settings=schedule_settings,
    )

    assert is_slot_available is False


@pytest.mark.parametrize(
    "date_offset, expected_error",
    [
        (-1, BookingError),
        (+1, BookingError),
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
    schedule_settings,
    mock_bot,
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
            schedule_settings=schedule_settings,
            bot=mock_bot,
        )
        await session.flush()


@pytest.mark.parametrize(
    "time_offset, expected_error",
    [
        (-30, BookingError),
        (+30, BookingError),
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
    schedule_settings,
    mock_bot,
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
            schedule_settings=schedule_settings,
            bot=mock_bot,
        )
        await session.flush()


@pytest.mark.asyncio
async def test_set_booking_approval_without_user_telegram_id(
    session: AsyncSession,
    mock_bot,
):
    # Arrange
    schedule = Schedule(
        visit_datetime=datetime(2025, 6, 1, 9, 30),
        visit_duration=30,
        is_booked=True,
        user_telegram_id=None,  # Нет telegram_id
        is_approved=None,
    )
    session.add(schedule)
    await session.commit()

    service = AdminService()

    with pytest.raises(BookingError):
        await service.set_booking_approval(
            session=session, bot=mock_bot, schedule_id=schedule.id, approved=True
        )

    # Проверяем, что сообщение не отправлялось
    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_create_busy_slot_success(mock_bot, schedule_settings, future_datetime):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123
    visit_date = future_datetime.date()
    visit_time = future_datetime.time()

    service = ScheduleService()

    with (
        patch.object(service, "is_slot_available", AsyncMock(return_value=True)),
        patch.object(
            service, "_check_user_booking_limit", AsyncMock(return_value=True)
        ),
        patch.object(service, "add", AsyncMock()),
    ):
        result = await service.create_busy_slot(
            session=session,
            bot=mock_bot,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user_telegram_id,
            schedule_settings=schedule_settings,
        )

        assert result is not None
        assert result.user_telegram_id == user_telegram_id
        assert result.is_booked is True
        service.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_busy_slot_when_slot_not_available(
    mock_bot, schedule_settings, future_datetime
):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123
    visit_date = future_datetime.date()
    visit_time = future_datetime.time()

    service = ScheduleService()

    with (
        patch.object(service, "is_slot_available", AsyncMock(return_value=False)),
        pytest.raises(BookingError, match="Это время уже занято"),
    ):
        await service.create_busy_slot(
            session=session,
            bot=mock_bot,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user_telegram_id,
            schedule_settings=schedule_settings,
        )


@pytest.mark.asyncio
async def test_create_busy_slot_when_user_limit_reached(
    mock_bot, schedule_settings, future_datetime
):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123
    visit_date = future_datetime.date()
    visit_time = future_datetime.time()

    service = ScheduleService()

    with (
        patch.object(service, "is_slot_available", AsyncMock(return_value=True)),
        patch.object(
            service, "_check_user_booking_limit", AsyncMock(return_value=False)
        ),
    ):
        result = await service.create_busy_slot(
            session=session,
            bot=mock_bot,
            visit_date=visit_date,
            visit_time=visit_time,
            user_telegram_id=user_telegram_id,
            schedule_settings=schedule_settings,
            max_user_bookings=3,
        )

        assert result is None
        mock_bot.send_message.assert_awaited_once_with(
            chat_id=user_telegram_id,
            text="⚠️ Достигнут лимит бронирований (3)."
            " Отмените предыдущую запись, чтобы создать новую.",
        )


@pytest.mark.asyncio
async def test_show_user_schedules_empty():
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    session.execute.return_value = mock_result

    result = await ScheduleService.show_user_schedules(session, user_telegram_id)

    assert len(result) == 0
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_show_user_schedules_with_results(future_datetime):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123

    test_schedule = Schedule(
        visit_datetime=future_datetime,
        visit_duration=30,
        is_booked=True,
        user_telegram_id=user_telegram_id,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [test_schedule]
    session.execute.return_value = mock_result

    result = await ScheduleService.show_user_schedules(session, user_telegram_id)

    assert len(result) == 1
    assert result[0].user_telegram_id == user_telegram_id
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_booking_success(future_datetime):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123

    mock_result = MagicMock()
    mock_result.rowcount = 1
    session.execute.return_value = mock_result

    await ScheduleService.cancel_booking(
        session=session,
        user_telegram_id=user_telegram_id,
        datetime_to_cancel=future_datetime,
    )

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_booking_not_found(future_datetime):
    session = AsyncMock(spec=AsyncSession)
    user_telegram_id = 123

    mock_result = MagicMock()
    mock_result.rowcount = 0
    session.execute.return_value = mock_result

    with pytest.raises(BookingError, match="Запись не найдена"):
        await ScheduleService.cancel_booking(
            session=session,
            user_telegram_id=user_telegram_id,
            datetime_to_cancel=future_datetime,
        )

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
