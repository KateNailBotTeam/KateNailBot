from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.schedule import Schedule
from src.services.base import BaseService


class AdminService(BaseService[Schedule]):
    def __init__(self) -> None:
        super().__init__(Schedule)

    @staticmethod
    async def get_booking(
        session: AsyncSession,
        booking_id: int,
    ) -> Schedule | None:
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.user))
            .where(Schedule.id == booking_id)
        )
        result = await session.execute(stmt)
        booking = result.scalar_one_or_none()
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
        return bookings

    async def set_booking_approval(
        self, session: AsyncSession, schedule_id: int, approved: bool | None
    ) -> Schedule | None:
        return await self.update(
            obj_id=schedule_id, session=session, new_data={"is_approved": approved}
        )

    async def delete_booking(self, session: AsyncSession, schedule_id: int) -> bool:
        is_success = await self.delete(session=session, obj_id=schedule_id)
        return is_success

    async def notify_admin_on_booking(self) -> None:
        pass

    async def notify_user_on_approve_or_reject(self) -> None:
        pass
