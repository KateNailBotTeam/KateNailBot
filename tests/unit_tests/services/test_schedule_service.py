from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

from src.services.schedule import ScheduleService

# --- Existing tests for other methods remain unchanged ---


@patch.object(ScheduleService, "WORKING_DAYS", (0, 2, 4))
@pytest.mark.parametrize(
    "date_obj, expected",
    [
        (date(2025, 3, 3), True),
        (date(2025, 3, 4), False),
        (date(2025, 3, 5), True),
        (date(2025, 3, 6), False),
        (date(2025, 3, 7), True),
    ],
)
def test_is_working_day(date_obj, expected, schedule_service):
    assert schedule_service.is_working_day(date_obj) == expected


def test_get_available_dates_has_correct_number(schedule_service):
    available_dates = schedule_service.get_available_dates()
    assert len(available_dates) == schedule_service.BOOKING_DAYS_AHEAD


def test_get_available_dates_only_working_dates(schedule_service):
    available_dates = schedule_service.get_available_dates()
    assert all(
        day.weekday() in schedule_service.WORKING_DAYS for day in available_dates
    )


@patch("src.services.schedule.datetime")
@patch.object(ScheduleService, "WORKING_DAYS", (0, 1, 2, 3, 4))
def test_get_available_dates_with_mocked_today(mock_datetime, schedule_service):
    mock_day = date(2025, 3, 3)
    mock_datetime.now.return_value.date.return_value = mock_day
    result = schedule_service.get_available_dates()

    assert len(result) == schedule_service.BOOKING_DAYS_AHEAD
    assert result[0] == mock_day
    assert result[-1] == date(2025, 3, 20)
    assert date(2025, 3, 8) not in result
    assert date(2025, 3, 9) not in result


@patch.object(ScheduleService, "WORKING_HOURS_START", "09:00")
@patch.object(ScheduleService, "WORKING_HOURS_END", "18:00")
@pytest.mark.parametrize(
    "visit_date, duration, slots",
    [
        (date(2025, 3, 3), 30, 18),
        (date(2025, 3, 4), 60, 9),
    ],
)
def test_get_time_slots(visit_date, duration, slots, schedule_service):
    time_slots = schedule_service.get_time_slots(visit_date, duration)
    datetime_start = datetime.strptime(schedule_service.WORKING_HOURS_START, "%H:%M")
    datetime_end = datetime.strptime(schedule_service.WORKING_HOURS_END, "%H:%M")

    assert len(time_slots) == slots
    assert time_slots[0] >= datetime_start.time()
    assert time_slots[-1] <= (datetime_end - timedelta(minutes=duration)).time()

    for i in range(len(time_slots) - 1):
        next_date = datetime.combine(visit_date, time_slots[i + 1])
        now_date = datetime.combine(visit_date, time_slots[i])
        assert (next_date - now_date).total_seconds() == duration * 60


###########################################
# async def test_is_slot_available_and_mark_slot_busy(session: AsyncSession):
#     service = ScheduleService()
#     visit_date = service.get_available_dates()[0]
#     visit_time = service.get_time_slots(visit_date)[0]
#     user_telegram_id = 123456
#
#     # Slot should be available
#     available = await service.is_slot_available(session,
#     visit_date, visit_time)
#     assert available
#
#     # Mark slot as busy
#     slot = await service.mark_slot_busy(session,
#     visit_date, visit_time, user_telegram_id)
#     assert isinstance(slot, Schedule)
#     assert slot.is_booked
#     assert slot.user_telegram_id == user_telegram_id
#
#     # Slot should now be unavailable
#     available = await service.is_slot_available(session,
#     visit_date, visit_time)
#     assert not available
#
#     # Booking the same slot again should raise error
#     with pytest.raises(SlotAlreadyBookedError):
#         await service.mark_slot_busy(session,
#         visit_date,
#         visit_time,
#         user_telegram_id)


# @pytest.mark.asyncio
# async def test_is_slot_available_invalid_date_time(session: AsyncSession):
#     service = ScheduleService()
#     # Use a weekend (not a working day)
#     today = date.today()
#     while service.is_working_day(today):
#         today += timedelta(days=1)
#     visit_time = time(10, 0)
#     with pytest.raises(BookingDateError):
#         await service.is_slot_available(session, today, visit_time)
#
#     # Use a valid date but invalid time
#     valid_date = service.get_available_dates()[0]
#     invalid_time = time(23, 59)
#     with pytest.raises(BookingTimeError):
#         await service.is_slot_available(session, valid_date, invalid_time)


# @pytest.mark.asyncio
# async def test_show_user_schedules(session: AsyncSession):
#     service = ScheduleService()
#     visit_date = service.get_available_dates()[0]
#     visit_time = service.get_time_slots(visit_date)[0]
#     user_telegram_id = 111222
#     # Book a slot
#     await service.mark_slot_busy(session,
#     visit_date, visit_time, user_telegram_id)
#     # Should show the schedule
#     schedules = await service.show_user_schedules(session, user_telegram_id)
#     assert any(isinstance(dt, datetime) for dt in schedules)
#     # Should not show for another user
#     schedules_other = await service.show_user_schedules(session, 999999)
#     assert schedules_other == []


# @pytest.mark.asyncio
# async def test_cancel_booking(session: AsyncSession):
#     service = ScheduleService()
#     visit_date = service.get_available_dates()[0]
#     visit_time = service.get_time_slots(visit_date)[0]
#     user_telegram_id = 333444
#     # Book a slot
#     slot = await service.mark_slot_busy(session,
#     visit_date, visit_time, user_telegram_id)
#     # Cancel booking
#     await service.cancel_booking(session, user_telegram_id, slot.visit_datetime)
#     # Slot should be deleted
#     result = await session.get(Schedule, slot.id)
#     assert result is None
#     # Cancel non-existent booking should raise error
#     with pytest.raises(BookingDeleteError):
#         await service.cancel_booking(session, user_telegram_id, slot.visit_datetime)
