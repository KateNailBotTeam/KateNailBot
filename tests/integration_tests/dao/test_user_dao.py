# ruff: noqa: PLR0913

import pytest
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.user import UserDAO
from src.models.user import User


@pytest.mark.parametrize(
    "telegram_id, username, first_name, last_name, phone, is_admin",
    [
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
    ],
)
@pytest.mark.asyncio
async def test_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
    phone: str | None,
    is_admin: bool,
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
    await session.commit()

    assert created_user.telegram_id == telegram_id
    assert created_user.username == username
    assert created_user.first_name == first_name
    assert created_user.last_name == last_name
    assert created_user.phone == phone
    assert created_user.is_admin == is_admin
    assert created_user.id is not None
    assert created_user.created_at is not None
    assert created_user.updated_at is not None


@pytest.mark.parametrize(
    "telegram_id, username, first_name, last_name, phone, is_admin, expected_exception",
    [
        (
            666666,
            "too_long_username_abcdefghijklmnopqrstuvwxyz",
            "Valid",
            "Name",
            "+666666666",
            False,
            DataError,
        ),
        (
            777777,
            "valid_user",
            "TooLongFirstName" * 10,
            "Name",
            "+777777777",
            False,
            DataError,
        ),
        (
            888888,
            "valid_user",
            "Name",
            "TooLongLastName" * 10,
            "+888888888",
            False,
            DataError,
        ),
        (None, "no_id", "No-ID", "User", "+123123123", False, IntegrityError),
        (
            555555,
            "no_first_name",
            None,
            "NoFirstName",
            "+555555555",
            False,
            IntegrityError,
        ),
        (
            999999,
            "valid_user",
            "Name",
            "Last",
            "invalid_phone_format",
            False,
            IntegrityError,
        ),
    ],
    ids=[
        "too_long_username",
        "too_long_first_name",
        "too_long_last_name",
        "missing_telegram_id",
        "missing_first_name",
        "invalid_phone_format",
    ],
)
@pytest.mark.asyncio
async def test_fail_create_user(
    session: AsyncSession,
    telegram_id,
    username,
    first_name,
    last_name,
    phone,
    is_admin,
    expected_exception,
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

    with pytest.raises(expected_exception):
        await dao.add(session=session, obj=user)
        await session.commit()


@pytest.mark.parametrize(
    "telegram_id, username, first_name, last_name, phone, is_admin",
    [
        (1017999, "taylordavis", "Ryan", "Griffin", "+74509171166", True),
        (4415900, None, "Jason", "Dunn", "+74055965284", False),
        (4153494, "leekimberly", "Cassidy", "Lloyd", "+78586994522", False),
    ],
    ids=["with_all_fields", "without_username", "full_fields_not_admin"],
)
@pytest.mark.asyncio
async def test_get_user_by_id(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
    phone: str | None,
    is_admin: bool,
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

    created_user = await dao.add(user)
    get_user = await dao.get(session=session, obj_id=created_user.id)

    assert get_user is not None, "User not found"
    assert get_user.telegram_id == telegram_id
    assert get_user.username == username
    assert get_user.first_name == first_name
    assert get_user.last_name == last_name
    assert get_user.phone == phone
    assert get_user.is_admin == is_admin
    assert get_user.created_at is not None


@pytest.mark.parametrize(
    "invalid_id",
    [-1, 0, 9999999999999999, 123.45, "string_id", None],
    ids=["negative", "zero", "big_int", "float_id", "string_id", "None"],
)
@pytest.mark.asyncio
async def test_fail_get_user_by_id(session: AsyncSession, invalid_id):
    dao = UserDAO()

    if isinstance(invalid_id, int):
        result = await dao.get(session=session, obj_id=invalid_id)
        assert result is None
    else:
        with pytest.raises(TypeError):
            await dao.get(session=session, obj_id=invalid_id)


@pytest.mark.parametrize(
    "telegram_id, username, first_name, last_name, phone, is_admin, updates",
    [
        (
            2774389,
            "andrea62",
            "Sonya",
            "Moore",
            "+76423145440",
            True,
            {
                "username": "new_username",
                "last_name": "new_last_name",
                "phone": "+79192454433",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
    phone: str | None,
    is_admin: bool,
    updates: dict,
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

    updated_user = await dao.update(
        session=session, obj_id=created_user.id, new_data=updates
    )

    assert updated_user.telegram_id == created_user.telegram_id
    assert updated_user.username == updates["username"]
    assert updated_user.first_name == created_user.first_name
    assert updated_user.last_name == updates["last_name"]
    assert updated_user.phone == updates["phone"]
    assert updated_user.is_admin == created_user.is_admin
    assert updated_user.id is not None
    assert updated_user.created_at is not None
    assert updated_user.updated_at is not None
