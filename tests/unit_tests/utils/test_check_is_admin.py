from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.utils.get_admins_ids import get_admin_ids


def _make_result_with_db_ids(ids: list[int | None]):
    result = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = ids
    result.scalars.return_value = scalars_mock
    return result


@pytest.mark.asyncio
@patch("src.utils.get_admins_ids.settings")
async def test_get_admin_ids_merges_settings_and_db(mock_settings):
    mock_settings.ADMIN_IDS = [111, 222]
    session = AsyncMock()
    session.execute.return_value = _make_result_with_db_ids([333, 222])

    admin_ids = await get_admin_ids(session)

    assert admin_ids == {111, 222, 333}
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.utils.get_admins_ids.settings")
async def test_get_admin_ids_only_db(mock_settings):
    mock_settings.ADMIN_IDS = []
    session = AsyncMock()
    session.execute.return_value = _make_result_with_db_ids([10, 20])

    admin_ids = await get_admin_ids(session)

    assert admin_ids == {10, 20}
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.utils.get_admins_ids.settings")
async def test_get_admin_ids_only_settings(mock_settings):
    mock_settings.ADMIN_IDS = [777, 888]
    session = AsyncMock()
    session.execute.return_value = _make_result_with_db_ids([])

    admin_ids = await get_admin_ids(session)

    assert admin_ids == {777, 888}
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.utils.get_admins_ids.settings")
async def test_get_admin_ids_filters_falsy_and_deduplicates(mock_settings):
    mock_settings.ADMIN_IDS = [0, None, 111]
    session = AsyncMock()
    session.execute.return_value = _make_result_with_db_ids([0, 222, None, 111])

    admin_ids = await get_admin_ids(session)

    assert admin_ids == {111, 222}
    session.execute.assert_awaited_once()
