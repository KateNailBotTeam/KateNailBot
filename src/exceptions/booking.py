class BookingError(Exception):
    """Базовый класс ошибок бронирования."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Бронирования: {self.message}"
