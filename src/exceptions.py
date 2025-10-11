from datetime import date

from fastapi import HTTPException


class NabronirovalException(Exception):
    def __init__(self, detail: str = "Неожиданная ошибка"):
        self.detail = detail
        super().__init__(self.detail)


class NabronirovalHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class IncorrectTokenException(NabronirovalException):
    detail = "Некорректный токен"


class EmailNotRegisteredException(NabronirovalException):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordException(NabronirovalException):
    detail = "Пароль неверный"


class UnavailableFileFormatException(NabronirovalException):
    def __init__(self, detail: str | None = None):
        if detail is None:
            detail = "Недопустимый формат файла"
        super().__init__(detail)


class UserAlreadyExistsException(NabronirovalException):
    detail = "Пользователь уже существует"


class ValidationException(NabronirovalException):
    detail = "Пожалуйста, заполните все поля"


class ObjectNotFoundException(NabronirovalException):
    detail = "Объект не найден"


class ObjectAlreadyExistsException(NabronirovalException):
    detail = "Похожий объект уже существует"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Номер не найден"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Отель не найден"


class FacilityNotFoundException(ObjectNotFoundException):
    def __init__(self, detail: str | None = None):
        if detail is None:
            detail = "Удобство не найдено"
        super().__init__(detail)


class AllRoomsAreBookedException(NabronirovalException):
    detail = "Не осталось свободных номеров"


class HotelNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Номер не найден"


class NoDataHasBeenTransmitted(NabronirovalException):
    detail = "Данные не переданы"


class AllRoomsAreBookedHTTPException(NabronirovalHTTPException):
    status_code = 409
    detail = "Не осталось свободных номеров"


class IncorrectTokenHTTPException(NabronirovalHTTPException):
    detail = "Некорректный токен"


class EmailNotRegisteredHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class UserEmailAlreadyExistsHTTPException(NabronirovalHTTPException):
    status_code = 409
    detail = "Пользователь с такой почтой уже существует"


class IncorrectPasswordHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Пароль неверный"


class NoAccessTokenHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен доступа"


class ObjectAlreadyExistsHTTPException(NabronirovalHTTPException):
    status_code = 409
    detail = "Похожий объект уже существует"


class UnavailableFileFormatHTTPException(NabronirovalHTTPException):
    def __init__(self, detail: str):
        self.detail = detail

    status_code = 400


class ValidationHTTPException(NabronirovalHTTPException):
    def __init__(self, detail: str):
        self.detail = detail

    status_code = 401


class FacilityNotFoundHTTPException(NabronirovalHTTPException):
    def __init__(self, detail: str):
        self.detail = detail

    status_code = 404


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise HTTPException(status_code=422, detail="Дата заезда должна быть меньше даты выезда!")
