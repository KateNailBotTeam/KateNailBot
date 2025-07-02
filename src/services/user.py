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


class UserService(BaseService[User]):
    PHONE_REGEX = r"^\+7\d{10}$"

    def __init__(self) -> None:
        super().__init__(User)

    @classmethod
    def check_valid_phone(cls, phone: str) -> None:
        if not re.fullmatch(cls.PHONE_REGEX, phone):
            raise InvalidPhoneFormatError()

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

    async def update_name(
        self,
        session: AsyncSession,
        new_name: str,
        user: User,
    ) -> User:
        if not user:
            raise InvalidFoundUserError()

        if user.first_name == new_name:
            return user

        updated_user = await self.update(
            session=session, obj_id=user.id, new_data={"first_name": new_name}
        )
        if not updated_user:
            raise InvalidFoundUserError()

        return updated_user

    async def update_number(
        self,
        session: AsyncSession,
        user: User,
        new_number: str,
    ) -> User:
        if not user:
            raise InvalidFoundUserError()

        self.check_valid_phone(new_number)

        stmt = select(User).where(User.phone == new_number, User.id != user.id)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise PhoneAlreadyExistsError()

        if user.phone == new_number:
            return user

        updated_user = await self.update(
            session=session, obj_id=user.id, new_data={"phone": new_number}
        )
        if not updated_user:
            raise InvalidFoundUserError()

        return user
