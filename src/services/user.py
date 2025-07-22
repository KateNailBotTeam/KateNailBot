import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.registration import (
    InvalidFoundUserError,
    InvalidPhoneFormatError,
    PhoneAlreadyExistsError,
)
from src.models.user import User
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
            raise InvalidPhoneFormatError()

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

    async def update_name(
        self,
        session: AsyncSession,
        new_name: str,
        user: User,
    ) -> User:
        logger.info(
            "Updating user name: user_id=%s, new_name=%s",
            getattr(user, "id", None),
            new_name,
        )
        if not user:
            logger.warning("User not found for update_name")
            raise InvalidFoundUserError()
        if user.first_name == new_name:
            logger.info("User name is already up to date: %s", new_name)
            return user
        updated_user = await self.update(
            session=session, obj_id=user.id, new_data={"first_name": new_name}
        )
        if not updated_user:
            logger.warning("Failed to update user name for user_id=%s", user.id)
            raise InvalidFoundUserError()
        logger.info("User name updated: %s", updated_user)
        return updated_user

    async def update_number(
        self,
        session: AsyncSession,
        user: User,
        new_number: str,
    ) -> User:
        logger.info(
            "Updating user number: user_id=%s, new_number=%s",
            getattr(user, "id", None),
            new_number,
        )
        if not user:
            logger.warning("User not found for update_number")
            raise InvalidFoundUserError()
        self.check_valid_phone(new_number)
        stmt = select(User).where(User.phone == new_number, User.id != user.id)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            logger.warning("Phone already exists: %s", new_number)
            raise PhoneAlreadyExistsError()
        if user.phone == new_number:
            logger.info("User phone is already up to date: %s", new_number)
            return user
        updated_user = await self.update(
            session=session, obj_id=user.id, new_data={"phone": new_number}
        )
        if not updated_user:
            logger.warning("Failed to update user phone for user_id=%s", user.id)
            raise InvalidFoundUserError()
        logger.info("User phone updated: %s", updated_user)
        return user
