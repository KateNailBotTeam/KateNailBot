class InvalidCallbackError(Exception):
    """Исключение для невалидных callback данных"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Сallback: {self.message}"


class InvalidMessageError(Exception):
    """Исключение для невалидных message данных"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Message: {self.message}"


class InvalidUserError(Exception):
    """Исключение для невалидных данных пользователя"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Message: {self.message}"
