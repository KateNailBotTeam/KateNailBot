import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import RegistrationError
from src.models.user import User
from src.services.base import BaseService


class UserService(BaseService[User]):
    PHONE_REGEX = r"^\+7\d{10}$"

    def __init__(self) -> None:
        super().__init__(User)

    @classmethod
    def check_valid_phone(cls, phone: str) -> None:
        if not re.fullmatch(cls.PHONE_REGEX, phone):
            raise RegistrationError("Неверный формат номера. Используйте +7XXXXXXXXXX.")

    @staticmethod
    async def get_by_telegram_id(
        session: AsyncSession,
        telegram_id: int,
    ) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = await session.scalar(stmt)
        return user

    async def create_or_get_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
    ) -> User:
        user = await self.get_by_telegram_id(session=session, telegram_id=telegram_id)
        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
        )
        created_user = await self.add(session=session, obj=user)
        return created_user
