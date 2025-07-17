from datetime import date

from fastapi import APIRouter, Body, Query

from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение одного номера")
async def get_one_room(hotel_id: int, room_id: int, db: DBDep):
    return await db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)


@router.get("{/hotel_id}/rooms", summary="Получение номеров")
async def get_rooms(
        hotel_id: int,
        db: DBDep,
        date_from: date = Query(example='2025-08-01'),
        date_to: date = Query(example='2025-08-07')
):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.post("/{hotel_id}/rooms", summary="Добавление номера")
async def create_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)
    await db.session_commit()

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="Изменение номера")
async def put_room(room_data: RoomAddRequest, hotel_id: int, room_id: int, db: DBDep):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(room_data, id=room_id)
    await db.session_commit()

    return {"status": "OK"}


@router.patch("{hotel_id}/rooms/{room_id}", summary="Частичное изменение номера")
async def patch_room(hotel_id: int, room_id: int, db: DBDep, room_data: RoomPatchRequest):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True))
    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
    await db.session_commit()

    return {"status": "OK"}


@router.delete("{hotel_id}/rooms/{room_id}", summary="Удаление номера")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    room = await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.session_commit()

    return {"status": "OK", "data":  room}
