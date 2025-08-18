from unittest.mock import MagicMock

from src.utils.register_middlewares import register_middlewares


def test_register_middlewares_registers_all():
    dp = MagicMock()

    register_middlewares(dp)
    assert dp.update.middleware.call_count == 6
    dp.message.middleware.assert_called_once()
