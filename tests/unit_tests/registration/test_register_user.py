from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import RegistrationError
from src.keyboards.start import InlineKeyboardMarkup, ask_about_name_kb
from src.models.user import User
from src.routers.commands.start import handle_start
from src.routers.handlers.start import (
    add_phone,
    change_name,
    finish_registration,
    keep_name,
    skip_phone,
)
from src.services.user import UserService
from src.states.registration import RegistrationState


@pytest.mark.asyncio
async def test_keep_name(callback_mock, message_mock):
    callback_mock.data = "profile_keep_name"

    await keep_name(callback_mock)

    callback_mock.answer.assert_awaited_once()

    edit_text_call_args = message_mock.edit_text.await_args
    assert edit_text_call_args is not None

    assert edit_text_call_args.kwargs["text"] == "Хотите добавить номер телефона?"

    assert "reply_markup" in edit_text_call_args.kwargs
    assert isinstance(edit_text_call_args.kwargs["reply_markup"], InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_change_name(callback_mock, message_mock, state_mock):
    callback_mock.data = "profile_change_name"

    await change_name(callback_mock, state_mock)

    callback_mock.answer.assert_awaited_once()
    message_mock.edit_text.assert_awaited_once_with("Введите новое имя:")
    state_mock.set_state.assert_awaited_once_with(RegistrationState.waiting_for_name)


@pytest.mark.asyncio
async def test_add_phone(callback_mock, message_mock, state_mock):
    callback_mock.data = "profile_add_phone"

    await add_phone(callback_mock, state_mock)

    callback_mock.answer.assert_awaited_once()
    message_mock.edit_text.assert_awaited_once_with(
        text="Введите номер в формате +7XXXXXXXXXX:"
    )
    state_mock.set_state.assert_awaited_once_with(RegistrationState.waiting_for_phone)


@pytest.mark.asyncio
async def test_skip_phone():
    callback_mock = MagicMock(spec=CallbackQuery)
    message_mock = MagicMock(spec=Message)
    callback_mock.message = message_mock

    state_mock = AsyncMock()
    session_mock = AsyncMock(spec=AsyncSession)

    user_mock = MagicMock(spec=User)
    user_mock.id = 1
    user_mock.first_name = "TestUser"
    user_mock.phone = None

    user_service_mock = MagicMock(spec=UserService)
    user_service_mock.update = AsyncMock(return_value=user_mock)

    test_data = {
        "telegram_id": 12345,
        "first_name": "TestUser",
        "phone": None,
        "user_schema_dict": {
            "id": 1,
            "telegram_id": 12345,
            "first_name": "OldName",
            "phone": None,
        },
    }

    state_mock.update_data = AsyncMock()
    state_mock.get_data = AsyncMock(return_value=test_data)
    state_mock.clear = AsyncMock()
    callback_mock.answer = AsyncMock()
    message_mock.edit_text = AsyncMock()

    await skip_phone(callback_mock, state_mock, session_mock, user_service_mock)

    callback_mock.answer.assert_awaited()
    state_mock.update_data.assert_awaited_once_with(phone=None)
    message_mock.edit_text.assert_awaited_once_with(
        text="Вы зарегистрированы!\nИмя: TestUser\nТелефон: не указан",
        reply_markup=None,
    )
    state_mock.clear.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data,expected_output",
    [
        (
            {
                "telegram_id": 123,
                "first_name": "John",
                "phone": "+7123456789",
                "user_schema_dict": {
                    "id": 1,
                    "telegram_id": 123,
                    "first_name": "OldName",
                    "phone": None,
                },
            },
            "Вы зарегистрированы!\nИмя: John\nТелефон: +7123456789",
        ),
        (
            {
                "telegram_id": 123,
                "first_name": "John",
                "phone": None,
                "user_schema_dict": {
                    "id": 1,
                    "telegram_id": 123,
                    "first_name": "OldName",
                    "phone": "+75556667788",
                },
            },
            "Вы зарегистрированы!\nИмя: John\nТелефон: не указан",
        ),
    ],
)
async def test_finish_registration_success(data, expected_output):
    message_mock = MagicMock(spec=Message)
    message_mock.answer = AsyncMock()
    message_mock.edit_text = AsyncMock()

    session_mock = AsyncMock(spec=AsyncSession)
    state_mock = AsyncMock()

    updated_user_mock = MagicMock()
    updated_user_mock.first_name = data["first_name"]
    updated_user_mock.phone = data["phone"]

    user_service_mock = MagicMock(spec=UserService)
    user_service_mock.update = AsyncMock(return_value=updated_user_mock)

    await finish_registration(
        obj=message_mock,
        data=data,
        state=state_mock,
        session=session_mock,
        user_service=user_service_mock,
    )

    message_mock.answer.assert_awaited_once_with(expected_output)
    state_mock.clear.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data,expected_exception",
    [
        (
            {"first_name": "John", "phone": None, "user_schema_dict": {}},
            RegistrationError,
        ),
        (
            {"telegram_id": 123, "phone": None, "user_schema_dict": {}},
            RegistrationError,
        ),
        (
            {"telegram_id": 123, "first_name": "John", "user_schema_dict": None},
            RegistrationError,
        ),
    ],
)
async def test_finish_registration_errors(data, expected_exception):
    session_mock = AsyncMock(spec=AsyncSession)
    state_mock = AsyncMock()
    user_service_mock = MagicMock(spec=UserService)

    obj_mock = AsyncMock(spec=Message)
    obj_mock.answer = AsyncMock()

    with pytest.raises(expected_exception):
        await finish_registration(
            obj=obj_mock,
            data=data,
            state=state_mock,
            session=session_mock,
            user_service=user_service_mock,
        )

    user_service_mock.update.assert_not_called()
    obj_mock.answer.assert_not_called()
    state_mock.clear.assert_not_called()


@pytest.mark.asyncio
async def test_handle_start():
    message_mock = AsyncMock(spec=Message)
    state_mock = AsyncMock()
    session_mock = AsyncMock(spec=AsyncSession)
    user_service_mock = MagicMock(spec=UserService)

    message_mock.from_user = MagicMock()
    message_mock.from_user.id = 123
    message_mock.from_user.first_name = "John"
    message_mock.from_user.is_bot = False
    message_mock.from_user.username = "test_user"

    db_user_mock = MagicMock(spec=User)
    db_user_mock.id = 1
    db_user_mock.telegram_id = 123
    db_user_mock.first_name = "John_DB"
    db_user_mock.username = "johnny"
    db_user_mock.phone = "+79998887766"

    user_service_mock.create_or_get_user = AsyncMock(return_value=db_user_mock)
    state_mock.update_data = AsyncMock()
    message_mock.answer = AsyncMock()

    await handle_start(
        message=message_mock,
        session=session_mock,
        user_service=user_service_mock,
        state=state_mock,
    )

    user_service_mock.create_or_get_user.assert_awaited_once_with(
        session=session_mock, telegram_id=123, first_name="John"
    )

    state_mock.update_data.assert_awaited_once()
    message_mock.answer.assert_awaited_once()

    args, kwargs = message_mock.answer.call_args
    assert "reply_markup" in kwargs
    actual_keyboard = kwargs["reply_markup"]
    assert actual_keyboard == ask_about_name_kb()
