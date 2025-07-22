class RegistrationError(Exception):
    """Ошибка регистрации. Сообщение указывает детали"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Ошибка регистрации: {self.message}"
