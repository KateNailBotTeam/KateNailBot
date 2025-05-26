# from unittest.mock import AsyncMock, MagicMock
#
# import pytest
# from aiogram.types import Message
#
# from src.keyboards.book import create_book_main_menu
# from src.routers.commands.base import book
#
#
# @pytest.mark.asyncio
# async def test_command_book() -> None:
#     message = MagicMock(spec=Message)
#     message.answer = AsyncMock()
#
#     await book(message)
#
#     message.answer.assert_awaited_once_with(
#         text="Управление записями", reply_markup=create_book_main_menu()
#     )
