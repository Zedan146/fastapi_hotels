from datetime import date

from fastapi import APIRouter, Body, HTTPException

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import AllRoomsAreBookedException
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("", summary="Получение всех бронирований")
async def get_bookings(db: DBDep):
    return await BookingService(db).get_bookings()


@router.get("/me", summary="Получение бронирований пользователя")
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    bookings = await BookingService(db).get_user_bookings(user_id)
    if not bookings:
        return {"message": "У вас еще нет бронирований"}
    return bookings


@router.post("", summary="Добавление бронирования")
async def create_booking(
    user_id: UserIdDep,
    db: DBDep,
    booking_data: BookingAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Бронирование 1",
                "value": {
                    "room_id": 1,
                    "date_from": date.today(),
                    "date_to": date.today(),
                },
            },
            "2": {
                "summary": "Бронирование 2",
                "value": {
                    "room_id": 2,
                    "date_from": "2026-10-27",
                    "date_to": "2026-11-02",
                },
            },
        }
    ),
):
    try:
        booking = await BookingService(db).create_booking(user_id, booking_data)
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)

    return {"status": "OK", "data": booking}
