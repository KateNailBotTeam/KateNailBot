import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.registration import RegistrationError
from src.models import User
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    PHONE_REGEX = r"^\+7\d{10}$"

    def __init__(self) -> None:
        super().__init__(User)

    @classmethod
    def check_valid_phone(cls, phone: str) -> None:
        if not re.fullmatch(cls.PHONE_REGEX, phone):
            logger.warning("Invalid phone format: %s", phone)
            raise RegistrationError("Неверный формат номера. Используйте +7XXXXXXXXXX.")

    @staticmethod
    async def get_by_telegram_id(
        session: AsyncSession,
        telegram_id: int,
    ) -> User | None:
        logger.info("Getting user by telegram_id: %d", telegram_id)
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = await session.scalar(stmt)
        logger.info("User found: %s", user)
        return user

    async def create_or_get_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
    ) -> User:
        logger.info(
            "Create or get user: telegram_id=%d, first_name=%s", telegram_id, first_name
        )
        user = await self.get_by_telegram_id(session=session, telegram_id=telegram_id)
        if user:
            logger.info("User already exists: %s", user)
            return user

        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
        )
        created_user = await self.add(session=session, obj=user)
        logger.info("Created new user: %s", created_user)
        return created_user
