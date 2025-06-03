import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.user import UserDAO
from src.models.user import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, user_dao: UserDAO):
    user_data = {
        "telegram_id": 312451,
        "username": None,
        "first_name": "Georgy",
        "last_name": "Astanov",
        "phone": "+7911835912",
    }

    user = User(**user_data)
    created_user = await user_dao.add(session=session, obj=user)

    assert created_user.id is not None
    assert created_user.created_at is not None

    for k, v in user_data.items():
        assert getattr(created_user, k) == v


@pytest.mark.asyncio
async def test_get_user_by_id(session: AsyncSession, user_dao: UserDAO):
    pass
