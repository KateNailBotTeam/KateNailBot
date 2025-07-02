class RegistrationError(Exception):
    """Базовый класс ошибок регистрации."""


class InvalidTelegramIdError(RegistrationError):
    def __init__(self) -> None:
        super().__init__("telegram_id должен быть числом")


class InvalidFirstNameError(RegistrationError):
    def __init__(self) -> None:
        super().__init__("first_name должен быть строкой")


class InvalidFoundUserError(RegistrationError):
    def __init__(self) -> None:
        super().__init__("Пользователь не найден при обновлении данных.")


class InvalidPhoneFormatError(RegistrationError, ValueError):
    def __init__(self) -> None:
        super().__init__("Неверный формат номера. Используйте +7XXXXXXXXXX.")


class PhoneAlreadyExistsError(RegistrationError, ValueError):
    def __init__(self) -> None:
        super().__init__("Этот номер уже используется")
