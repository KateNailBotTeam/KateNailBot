from unittest.mock import AsyncMock, patch

import pytest

from src.utils.get_admins_ids import check_is_admin


@pytest.mark.asyncio
@patch("src.utils.check_is_admin.settings")
async def test_check_is_admin_true_by_settings(mock_settings):
    mock_settings.ADMIN_IDS = [111, 222]
    session = AsyncMock()

    assert await check_is_admin(telegram_id=222, session=session) is True
    session.execute.assert_not_awaited()


@pytest.mark.asyncio
@patch("src.utils.check_is_admin.settings")
async def test_check_is_admin_fallback_to_db(mock_settings):
    mock_settings.ADMIN_IDS = []

    session = AsyncMock()

    # Simulate DB returning True for is_admin
    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = True
    session.execute.return_value = result_mock

    is_admin = await check_is_admin(telegram_id=999, session=session)

    assert is_admin is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.utils.check_is_admin.settings")
async def test_check_is_admin_not_admin(mock_settings):
    mock_settings.ADMIN_IDS = []

    session = AsyncMock()
    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock

    is_admin = await check_is_admin(telegram_id=12345, session=session)
    assert is_admin is False
