from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.models.user import User


class UserDAO(BaseDAO):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_telegram_id(
        self, session: AsyncSession, telegram_id: int
    ) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
