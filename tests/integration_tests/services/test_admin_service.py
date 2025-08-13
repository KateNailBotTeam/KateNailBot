from collections.abc import Iterable
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.day_off import DaysOff
from src.models.schedule import Schedule
from src.models.schedule_settings import ScheduleSettings
from src.models.user import User
from src.services.admin import AdminService


@pytest.mark.asyncio
async def test_get_booking_returns_booking_with_user(session: AsyncSession):
    user = User(
        telegram_id=123456,
        username="tester",
        first_name="Tester",
        phone="+70000000000",
        is_admin=False,
    )
    session.add(user)
    await session.flush()

    visit_dt = datetime(2025, 5, 20, 10, 0)
    schedule = Schedule(
        visit_datetime=visit_dt,
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )
    session.add(schedule)
    await session.commit()

    booking = await AdminService.get_booking(session=session, booking_id=schedule.id)

    assert booking is not None
    assert booking.id == schedule.id
    assert booking.visit_datetime == visit_dt
    assert booking.user is not None
    assert booking.user.telegram_id == user.telegram_id


@patch("src.services.admin.datetime")
@pytest.mark.asyncio
async def test_get_all_bookings_filters_and_orders(
    mock_datetime, session: AsyncSession
):
    mock_datetime.now.return_value = datetime(2025, 3, 3, 8, 0, 0)

    user = User(
        telegram_id=111,
        username="one",
        first_name="One",
        phone=None,
        is_admin=False,
    )
    session.add(user)
    await session.flush()

    base = mock_datetime.now.return_value

    past = Schedule(
        visit_datetime=base - timedelta(days=1),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )

    future_free = Schedule(
        visit_datetime=base + timedelta(days=1),
        visit_duration=60,
        is_booked=False,
        user_telegram_id=None,
    )

    future1 = Schedule(
        visit_datetime=base + timedelta(hours=2),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )
    future2 = Schedule(
        visit_datetime=base + timedelta(hours=1),
        visit_duration=60,
        is_booked=True,
        user_telegram_id=user.telegram_id,
    )

    session.add_all([past, future_free, future1, future2])
    await session.commit()

    bookings = await AdminService.get_all_bookings(session=session)

    assert [b.id for b in bookings] == [future2.id, future1.id]


@pytest.mark.parametrize("approved", [True, False, None])
@pytest.mark.asyncio
async def test_set_booking_approval_updates_and_notifies(
    session: AsyncSession, approved: bool | None
):
    visit_dt = datetime(2025, 6, 1, 9, 30)
    schedule = Schedule(
        visit_datetime=visit_dt,
        visit_duration=30,
        is_booked=True,
        user_telegram_id=123456789,
        is_approved=None,
    )
    session.add(schedule)
    await session.commit()

    class BotStub:
        def __init__(self):
            self.calls: list[dict] = []

        async def send_message(self, chat_id: int, text: str):
            self.calls.append({"chat_id": chat_id, "text": text})

    bot = BotStub()
    service = AdminService()
    updated = await service.set_booking_approval(
        session=session, schedule_id=schedule.id, approved=approved, bot=bot
    )

    assert updated is not None
    assert updated.id == schedule.id
    assert updated.is_approved is approved

    refreshed = await session.get(Schedule, schedule.id)
    assert refreshed is not None
    assert refreshed.is_approved is approved

    # Notification should be sent when user_telegram_id exists
    assert len(bot.calls) == 1
    assert bot.calls[0]["chat_id"] == schedule.user_telegram_id
    assert "Ваше бронирование обновлено" in bot.calls[0]["text"]


def _daterange(d1: date, d2: date) -> Iterable[date]:
    current = d1
    while current <= d2:
        yield current
        current += timedelta(days=1)


@pytest.mark.asyncio
async def test_set_workdays_add_and_remove_days_off(session: AsyncSession):
    first = date(2025, 1, 1)
    last = date(2025, 1, 3)

    # Add non-working days
    await AdminService.set_workdays(
        first_day=first, last_day=last, is_work=False, session=session
    )

    result = await session.execute(select(DaysOff.day_off))
    stored = set(result.scalars().all())
    assert stored == set(_daterange(first, last))

    await AdminService.set_workdays(
        first_day=first,
        last_day=first + timedelta(days=1),
        is_work=True,
        session=session,
    )

    result_after = await session.execute(select(DaysOff.day_off))
    stored_after = set(result_after.scalars().all())
    assert stored_after == {last}


@pytest.mark.asyncio
async def test_set_workdays_invalid_range_raises_and_unchanged(session: AsyncSession):
    first = date(2025, 1, 5)
    last = date(2025, 1, 1)

    with pytest.raises(ValueError):
        await AdminService.set_workdays(
            first_day=first, last_day=last, is_work=False, session=session
        )

    result = await session.execute(select(DaysOff))
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_toggle_working_day_add_and_remove(session: AsyncSession):
    settings = ScheduleSettings()  # defaults: working days Mon-Fri -> [0,1,2,3,4]
    session.add(settings)
    await session.commit()

    service = AdminService()

    await service.toggle_working_day(
        session=session, day_index=5, schedule_settings=settings
    )

    refreshed = await session.get(ScheduleSettings, settings.id)
    assert 5 in refreshed.working_days

    await service.toggle_working_day(
        session=session, day_index=5, schedule_settings=refreshed
    )
    refreshed2 = await session.get(ScheduleSettings, settings.id)
    assert 5 not in refreshed2.working_days


@pytest.mark.asyncio
async def test_toggle_working_day_invalid_index_raises(session: AsyncSession):
    settings = ScheduleSettings()
    session.add(settings)
    await session.commit()

    service = AdminService()

    for bad_index in (-1, 8):
        with pytest.raises(ValueError):
            await service.toggle_working_day(
                session=session, day_index=bad_index, schedule_settings=settings
            )


class StubBot:
    def __init__(self, fail_ids: set[int] | None = None) -> None:
        self.fail_ids = fail_ids or set()
        self.calls: list[tuple[int, str, bool]] = []

    async def send_message(
        self, chat_id: int, text: str, disable_notification: bool = True
    ):
        self.calls.append((chat_id, text, disable_notification))
        if chat_id in self.fail_ids:
            raise RuntimeError("network error")


@pytest.mark.asyncio
async def test_send_message_from_admin_to_all_users_counts_and_excludes_admin(
    session: AsyncSession,
    create_users: list[User],
):
    # Add one admin user, it must be excluded from broadcast
    admin = User(
        telegram_id=999999,
        username="admin",
        first_name="Admin",
        phone=None,
        is_admin=True,
    )
    session.add(admin)
    await session.commit()

    non_admin_ids = {u.telegram_id for u in create_users}
    # Fail for two users
    fail_for = set(list(non_admin_ids)[:2])

    bot = StubBot(fail_ids=fail_for)

    summary = await AdminService.send_message_from_admin_to_all_users(
        bot=bot, session=session, text_message="Hello!", disable_notification=True
    )

    # Ensure we sent to all non-admins only
    called_ids = {chat_id for chat_id, _, _ in bot.calls}
    assert called_ids == non_admin_ids
    assert all(disable for _, _, disable in bot.calls)

    # Check summary counts (numbers only)
    assert f"Всего пользователей: {len(non_admin_ids)}" in summary
    assert (
        f"Успешно отправлено сообщений: {len(non_admin_ids) - len(fail_for)}" in summary
    )
    assert f"Не удалось отправить сообщения: {len(fail_for)}" in summary
