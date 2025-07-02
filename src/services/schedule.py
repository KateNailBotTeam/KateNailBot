from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import (
    BookingDateError,
    BookingTimeError,
    SlotAlreadyBookedError,
)
from src.models.schedule import Schedule
from src.services.base import BaseService


class ScheduleService(BaseService[Schedule]):
    WORKING_DAYS = (0, 1, 2, 3, 4)  # пн-пт
    WORKING_HOURS_START = "09:00"
    WORKING_HOURS_END = "18:00"
    DEFAULT_SLOT_DURATION = 30  # минут
    BOOKING_DAYS_AHEAD = 14

    def __init__(self) -> None:
        super().__init__(Schedule)

    def is_working_day(self, visit_date: date) -> bool:
        return visit_date.weekday() in self.WORKING_DAYS

    def get_available_dates(self) -> list[date]:
        available_dates: list = []
        current_date = datetime.now().date()

        while len(available_dates) < self.BOOKING_DAYS_AHEAD:
            if self.is_working_day(current_date):
                available_dates.append(current_date)
            current_date += timedelta(days=1)

        return available_dates

    def get_time_slots(
        self, visit_date: date, duration: int = DEFAULT_SLOT_DURATION
    ) -> list[time]:
        time_slots = []
        last_visit = datetime.combine(
            visit_date,
            (
                datetime.strptime(self.WORKING_HOURS_END, "%H:%M")
                - timedelta(minutes=duration)
            ).time(),
        )

        start_visit = datetime.combine(
            visit_date, datetime.strptime(self.WORKING_HOURS_START, "%H:%M").time()
        )

        while start_visit <= last_visit:
            time_slots.append(start_visit.time())
            start_visit += timedelta(minutes=duration)
        return time_slots

    async def is_slot_available(
        self, session: AsyncSession, visit_date: date, visit_time: time
    ) -> bool:
        dt = datetime.combine(visit_date, visit_time)

        if visit_date not in self.get_available_dates():
            raise BookingDateError(date_info=visit_date)

        if visit_time not in self.get_time_slots(visit_date=visit_date):
            raise BookingTimeError(time_info=visit_time)

        stmt = select(Schedule.is_booked).where(Schedule.visit_datetime == dt)

        result = await session.execute(stmt)
        booked = result.scalar_one_or_none()

        return bool(booked is None or booked is False)

    async def mark_slot_busy(
        self,
        session: AsyncSession,
        visit_date: date,
        visit_time: time,
        user_telegram_id: int,
        duration: int = DEFAULT_SLOT_DURATION,
    ) -> Schedule:
        available = await self.is_slot_available(session, visit_date, visit_time)
        if not available:
            raise SlotAlreadyBookedError()

        new_slot = Schedule(
            visit_datetime=datetime.combine(visit_date, visit_time),
            visit_duration=duration,
            is_booked=True,
            user_telegram_id=user_telegram_id,
        )
        created_slot = await self.add(session=session, obj=new_slot)
        return created_slot

    async def show_user_schedules(
        self,
        session: AsyncSession,
        user_telegram_id: int,
    ) -> list[datetime]:
        stmt = select(Schedule.visit_datetime).where(
            and_(
                Schedule.user_telegram_id == user_telegram_id,
            )
        )

        result = await session.execute(stmt)
        schedules = list(result.scalars().all())
        return schedules
