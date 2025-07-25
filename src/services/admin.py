import logging
from datetime import date, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.day_off import DaysOff
from src.models.schedule import Schedule
from src.services.base import BaseService
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS

logger = logging.getLogger(__name__)


class AdminService(BaseService[Schedule]):
    def __init__(self) -> None:
        super().__init__(Schedule)

    @staticmethod
    async def get_booking(
        session: AsyncSession,
        booking_id: int,
    ) -> Schedule | None:
        logger.debug("Получение бронирования id=%d", booking_id)
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.user))
            .where(Schedule.id == booking_id)
        )
        result = await session.execute(stmt)
        booking = result.scalar_one_or_none()
        logger.info("Бронь: %s", booking_id)

        return booking

    @staticmethod
    async def get_all_bookings(
        session: AsyncSession,
    ) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.user))
            .where(and_(Schedule.is_booked, Schedule.visit_datetime >= datetime.now()))
            .order_by(Schedule.visit_datetime)
        )
        result = await session.execute(stmt)
        bookings = list(result.scalars().all())

        logger.info("Получены все бронирования: %d", len(bookings))
        return bookings

    async def set_booking_approval(
        self, session: AsyncSession, schedule_id: int, approved: bool | None
    ) -> Schedule | None:
        updated_booking = await self.update(
            obj_id=schedule_id, session=session, new_data={"is_approved": approved}
        )
        status = APPOINTMENT_TYPE_STATUS.get(approved)
        logger.info(
            "Обновлено подтверждение записи id=%s на значение %s", schedule_id, status
        )
        return updated_booking

    @staticmethod
    async def set_days_off(
        first_day_off: date,
        last_day_off: date,
        session: AsyncSession,
    ) -> None:
        if first_day_off > last_day_off:
            logger.warning(
                "Попытка установить выходные: начальная дата позже конечной (%s > %s)",
                first_day_off,
                last_day_off,
            )
            raise ValueError("first_day_off не может быть позже last_day_off")

        current_date = first_day_off
        while current_date <= last_day_off:
            await session.execute(
                insert(DaysOff)
                .values(day_off=current_date)
                .on_conflict_do_nothing(index_elements=["day_off"])
            )

            current_date += timedelta(days=1)

        await session.commit()

        logger.info(
            "Все выходные дни с %s по %s добавлены (без дубликатов).",
            first_day_off,
            last_day_off,
        )
