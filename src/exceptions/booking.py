from datetime import date, time


class BookingError(Exception):
    """Базовый класс ошибок бронирования."""


class BookingDateError(BookingError):
    def __init__(self, date_info: date) -> None:
        super().__init__(f"{date_info} Недоступная дата записи.")


class BookingDateNotFoundError(BookingError):
    def __init__(self) -> None:
        super().__init__("Дата не найдена.")


class UserTelegramIDNotFoundError(BookingError):
    def __init__(self) -> None:
        super().__init__("Телеграм id не найден.")


class BookingTimeError(BookingError):
    def __init__(self, time_info: time) -> None:
        super().__init__(f"{time_info} Недоступное время записи.")


class SlotAlreadyBookedError(BookingError):
    def __init__(self) -> None:
        super().__init__("Слот уже занят")


class BookingDeleteError(BookingError):
    def __init__(self) -> None:
        super().__init__("Не получилось удалить запись. Возможно она отсутствует")


class InvalidCallbackError(Exception):
    """Исключение для невалидных callback данных"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка Сallback: {self.message}"
