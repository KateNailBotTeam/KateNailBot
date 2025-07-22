from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import Schedule
from src.services.base import BaseService


class AdminService(BaseService[Schedule]):
    def __init__(self) -> None:
        super().__init__(Schedule)

    async def get_all_bookings(
        self,
        session: AsyncSession,
    ) -> None:
        pass

    async def approve_booking(self, booking_id: int) -> None:
        pass

    async def reject_booking(self, booking_id: int) -> None:
        pass

    async def delete_booking(self, booking_id: int) -> None:
        pass

    async def notify_admin_on_booking(self) -> None:
        pass

    async def notify_user_on_approve_or_reject(self) -> None:
        pass
