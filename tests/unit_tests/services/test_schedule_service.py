from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.models.schedule_settings import ScheduleSettings

# --- Existing tests for other methods remain unchanged ---


@pytest.mark.parametrize(
    "date_obj, expected",
    [
        (date(2025, 3, 3), True),  # Mon
        (date(2025, 3, 4), False),  # Tue not in [0,2,4]
        (date(2025, 3, 5), True),  # Wed
        (date(2025, 3, 6), False),  # Thu
        (date(2025, 3, 7), True),  # Fri
    ],
)
def test_is_working_day(date_obj, expected, schedule_service):
    settings = ScheduleSettings(working_days=[0, 2, 4])
    assert (
        schedule_service.is_working_day(
            visit_date=date_obj, schedule_settings=settings, all_days_off=set()
        )
        == expected
    )


@patch("src.services.schedule.datetime")
@pytest.mark.asyncio
async def test_get_available_dates_has_correct_number(mock_datetime, schedule_service):
    # Start from Monday and look 4 days ahead (Mon..Fri) → 5 working days expected
    mock_day = date(2025, 3, 3)  # Monday
    mock_datetime.now.return_value.date.return_value = mock_day

    session = AsyncMock()
    settings = ScheduleSettings(working_days=[0, 1, 2, 3, 4], booking_days_ahead=4)

    result = await schedule_service.get_available_dates(
        session=session, schedule_settings=settings, check_days_off=False
    )

    assert len(result) >= 5  # could include today + 4 more working days
    assert mock_day in result


@pytest.mark.asyncio
async def test_get_available_dates_only_working_dates(schedule_service):
    session = AsyncMock()
    settings = ScheduleSettings(working_days=[0, 1, 2, 3, 4], booking_days_ahead=14)
    dates = await schedule_service.get_available_dates(
        session=session, schedule_settings=settings, check_days_off=False
    )
    assert all(day.weekday() in settings.working_days for day in dates)


@patch("src.services.schedule.datetime")
@pytest.mark.asyncio
async def test_get_available_dates_with_mocked_today(mock_datetime, schedule_service):
    mock_day = date(2025, 3, 3)  # Monday
    mock_datetime.now.return_value.date.return_value = mock_day

    session = AsyncMock()
    settings = ScheduleSettings(working_days=[0, 1, 2, 3, 4], booking_days_ahead=17)

    result = await schedule_service.get_available_dates(
        session=session, schedule_settings=settings, check_days_off=False
    )

    assert min(result) == mock_day
    # Ensure weekends excluded
    assert date(2025, 3, 8) not in result
    assert date(2025, 3, 9) not in result


@pytest.mark.parametrize(
    "visit_date, slot_minutes, slots",
    [
        (date(2025, 3, 3), 30, 18),
        (date(2025, 3, 4), 60, 9),
    ],
)
def test_get_time_slots(visit_date, slot_minutes, slots, schedule_service):
    settings = ScheduleSettings(
        start_working_time=time(9, 0),
        end_working_time=time(18, 0),
        slot_duration_minutes=slot_minutes,
    )
    time_slots = schedule_service.get_time_slots(visit_date, settings)

    datetime_start = datetime.combine(visit_date, time(9, 0))
    datetime_end = datetime.combine(visit_date, time(18, 0))

    assert len(time_slots) == slots
    assert time_slots[0] >= datetime_start.time()
    assert time_slots[-1] <= (datetime_end - timedelta(minutes=slot_minutes)).time()

    for i in range(len(time_slots) - 1):
        next_date = datetime.combine(visit_date, time_slots[i + 1])
        now_date = datetime.combine(visit_date, time_slots[i])
        assert (next_date - now_date).total_seconds() == slot_minutes * 60
