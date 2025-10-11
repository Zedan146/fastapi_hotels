from datetime import date
from fastapi import APIRouter, Body, Query

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import (
    ObjectNotFoundException,
    RoomNotFoundException,
    check_date_to_after_date_from,
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException, HotelNotFoundException, FacilityNotFoundException, FacilityNotFoundHTTPException,
    ValidationException, ValidationHTTPException
)
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение одного номера")
@cache(expire=10)
async def get_one_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        return await RoomService(db).get_room(hotel_id, room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException


@router.get("/{hotel_id}/rooms", summary="Получение номеров")
@cache(expire=10)
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-08-01"),
    date_to: date = Query(example="2025-08-07"),
):
    check_date_to_after_date_from(date_from, date_to)
    try:
        return await RoomService(db).get_filtered_by_time(hotel_id, date_from, date_to)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


@router.post("/{hotel_id}/rooms", summary="Добавление номера")
async def create_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    try:
        room = await RoomService(db).add_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except FacilityNotFoundException as ex:
        raise FacilityNotFoundHTTPException(detail=f"{ex}")
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="Изменение номера")
async def put_room(room_data: RoomAddRequest, hotel_id: int, room_id: int, db: DBDep):
    try:
        room = await RoomService(db).edit_room(hotel_id, room_id, room_data)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except FacilityNotFoundException as ex:
        raise FacilityNotFoundHTTPException(detail=f"{ex}")

    return {"status": "OK", "new_data": room}


@router.patch("{hotel_id}/rooms/{room_id}", summary="Частичное изменение номера")
async def patch_room(hotel_id: int, room_id: int, db: DBDep, room_data: RoomPatchRequest):
    try:
        room = await RoomService(db).edit_room_partially(hotel_id, room_id, room_data)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except FacilityNotFoundException as ex:
        raise FacilityNotFoundHTTPException(detail=f"{ex}")
    except ValidationException as ex:
        raise ValidationHTTPException(detail="Пожалуйста, заполните хотя бы одно поле для изменения") from ex

    return {"status": "OK", "new_data": room}


@router.delete("{hotel_id}/rooms/{room_id}", summary="Удаление номера")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        await RoomService(db).delete_room(hotel_id, room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK"}
