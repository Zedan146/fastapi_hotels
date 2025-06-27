from fastapi import APIRouter

from schemas.rooms import RoomAdd, RoomPatch
from src.repositories.rooms import RoomsRepository
from src.database import async_session_maker


router = APIRouter(prefix="/hotels/rooms", tags=["Номера"])


@router.get("/{hotel_id}/{room_id}", summary="Получение одного номера отеля")
async def get_one_room(hotel_id: int, room_id: int):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_one_or_none(hotel_id=hotel_id, id=room_id)

@router.get("/{hotel_id}", summary="Получение всех номеров отеля")
async def get_rooms(hotel_id: int):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all(hotel_id)
    
@router.post("/{hotel_id}/room")
async def create_room(hotel_id: int, room_data: RoomAdd):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(room_data, hotel_id=hotel_id)
        await session.commit()

        return {"status": "OK", "data": room}
    
@router.put("/room/{room_id}")
async def put_room(room_id: int, data: RoomAdd):
    async with async_session_maker() as session:
        edit_room = await RoomsRepository(session).edit(data, id=room_id)
        await session.commit()
        return {"status": "OK", "data": edit_room}
    
@router.patch("/room/{room_id}")
async def patch_room(room_id: int, room_data: RoomPatch):
    async with async_session_maker() as session:
        patch_room = await RoomsRepository(session).edit(room_data, exclude_unset=True, id=room_id)
        await session.commit()
        return {"status": "OK", "data": patch_room}
    
@router.delete("/room/{room_id}")
async def delete_room(room_id: int):
    async with async_session_maker() as session:
        delete_room = await RoomsRepository(session).delete(id=room_id)
        await session.commit()
        return {"status": "OK", "delete_data": delete_room}