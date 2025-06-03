# ruff: noqa: PLR0913

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.user import UserDAO
from src.models.user import User

success_test_users_data = [
    (1017999, "taylordavis", "Ryan", "Griffin", "+74509171166", True),
    (4415900, None, "Jason", "Dunn", "+74055965284", True),
    (4153494, "leekimberly", "Cassidy", "Lloyd", "+78586994522", True),
    (4440465, "nicole23", "Stephanie", None, "+74843365165", True),
    (7491685, "gordoneric", "James", "Holmes", None, False),
    (807783, None, "John", None, None, False),
    (2774389, "andrea62", "Sonya", "Moore", "+76423145440", True),
    (5079279, "colonjoshua", "Michael", "Mason", "+74046839310", True),
    (5848696, "matthewwalton", "Anthony", "Thompson", "+75776924426", False),
    (7430156, "shaney", "Elizabeth", "Martinez", "+73257068473", False),
]


@pytest.mark.parametrize(
    "telegram_id, username, first_name, last_name, phone, is_admin",
    success_test_users_data,
)
@pytest.mark.asyncio
async def test_success_create_user(
    session: AsyncSession,
    telegram_id,
    username,
    first_name,
    last_name,
    phone,
    is_admin,
):
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        is_admin=is_admin,
    )

    dao = UserDAO()

    created_user = await dao.add(session=session, obj=user)

    assert created_user.telegram_id == telegram_id
    assert created_user.username == username
    assert created_user.first_name == first_name
    assert created_user.last_name == last_name
    assert created_user.phone == phone
    assert created_user.is_admin == is_admin
    assert created_user.id is not None
    assert created_user.created_at is not None
    assert created_user.updated_at is not None
