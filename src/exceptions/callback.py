class InvalidCallbackError(Exception):
    """Исключение для невалидных callback данных"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Сallback: {self.message}"
