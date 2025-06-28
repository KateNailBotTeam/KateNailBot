# ruff: noqa: PLR0913

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError, ProgrammingError
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
            "a" * 51,
            "Valid",
            "Name",
            "+666666666",
            False,
            DBAPIError,
        ),
        (
            777777,
            "valid_user",
            "a" * 101,
            "Name",
            "+777777777",
            False,
            DBAPIError,
        ),
        (
            888888,
            "valid_user",
            "Name",
            "a" * 101,
            "+888888888",
            False,
            DBAPIError,
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
            "phone_number" * 2,
            False,
            DBAPIError,
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

    created_user = await dao.add(session=session, obj=user)
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
    "invalid_id, expected_exception",
    [
        (-1, None),
        (0, None),
        (9999999999999999, DBAPIError),
        (123.45, None),
        ("string_id", ProgrammingError),
        (None, None),
    ],
    ids=["negative", "zero", "big_int", "float_id", "string_id", "None"],
)
@pytest.mark.asyncio
async def test_fail_get_user_by_id(
    session: AsyncSession, invalid_id, expected_exception
):
    dao = UserDAO()

    if expected_exception is None:
        result = await dao.get(session=session, obj_id=invalid_id)
        assert result is None
    else:
        with pytest.raises(expected_exception):
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


@pytest.mark.parametrize(
    "telegram_id,"
    " username,"
    " first_name,"
    " last_name,"
    " phone,"
    " is_admin,"
    " delete_id,"
    " test_result",
    [
        (7491685, "gordoneric", "James", "Holmes", None, False, None, True),
        (1234567, "otheruser", "Alice", "Smith", "1234567890", False, None, True),
        (9999999, "ghost", "Ghost", None, None, False, 999999999, False),
    ],
)
@pytest.mark.asyncio
async def test_delete_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
    phone: str | None,
    is_admin: bool,
    delete_id: int | None,
    test_result: bool,
):
    dao = UserDAO()
    if delete_id is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_admin=is_admin,
        )
        created_user = await dao.add(session=session, obj=user)
        obj_id_to_delete = created_user.id
    else:
        obj_id_to_delete = delete_id

    result = await dao.delete(session=session, obj_id=obj_id_to_delete)

    assert result is test_result

    user_after = await dao.get(session=session, obj_id=obj_id_to_delete)
    assert user_after is None
