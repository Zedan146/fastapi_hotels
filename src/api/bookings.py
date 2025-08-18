from datetime import date

from fastapi import APIRouter, Body, HTTPException

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAdd, BookingAddRequest

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("", summary="Получение всех бронирований")
async def get_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me", summary="Получение бронирований пользователя")
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    booking = await db.bookings.get_filtered(user_id=user_id)
    if booking:
        return booking
    return {"message": "У вас еще нет бронирований"}


@router.post("", summary="Добавление бронирования")
async def create_booking(
        user_id: UserIdDep,
        db: DBDep,
        booking_data: BookingAddRequest = Body(openapi_examples={
        "1": {
            "summary": "Бронирование 1",
            "value": {
                "room_id": 1,
                "date_from": date.today(),
                "date_to": date.today()
            }
        },
        "2": {
            "summary": "Бронирование 2",
            "value": {
                "room_id": 2,
                "date_from": "2026-10-27",
                "date_to": "2026-11-02"
            }
        }
        })):
    room_data = await db.rooms.get_one_or_none(id=booking_data.room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail="Комнаты с таким id не существует!")
    _booking_data = BookingAdd(user_id=user_id, price=room_data.price, **booking_data.model_dump())
    await db.bookings.add(_booking_data)

    return {"status": "OK", "data": _booking_data}
