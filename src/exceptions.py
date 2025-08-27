from datetime import date

from fastapi import HTTPException


class NabronirovalException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args):
        super().__init__(self.detail, *args)


class NabronirovalHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundException(NabronirovalException):
    detail = "Объект не найден"


class ObjectAlreadyExistsException(NabronirovalException):
    detail = "Похожий объект уже существует"


class RoomNotFoundException(NabronirovalException):
    detail = "Номер не найден"


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


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise HTTPException(status_code=422, detail="Дата заезда должна быть меньше даты выезда!")
