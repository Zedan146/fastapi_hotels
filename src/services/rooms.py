from datetime import date

from src.exceptions import ObjectNotFoundException, RoomNotFoundException, \
    ValidationException, FacilityNotFoundCustomException
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch, Room
from src.services.base import BaseService
from src.services.facilities import FacilityService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_room(self, hotel_id: int, room_id: int):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        return await self.db.rooms.get_one(hotel_id=hotel_id, id=room_id)

    async def get_filtered_by_time(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ):
        await self.db.hotels.get_one(id=hotel_id)

        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def add_room(self, hotel_id: int, room_data: RoomAddRequest):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.check_missing_facilities_ids(room_data)

        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)

        if room_data.facilities_ids:
            room_facilities_data = [
                RoomFacilityAdd(room_id=room.id, facility_id=facility)
                for facility in room_data.facilities_ids
            ]
            await self.db.room_facilities.add_bulk(room_facilities_data)
        await self.db.session_commit()
        return await self.db.rooms.get_one(id=room.id)

    async def edit_room(self, hotel_id: int, room_id: int, room_data: RoomAddRequest):
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        await self.check_missing_facilities_ids(room_data)

        await self.db.rooms.edit(_room_data, id=room_id)
        await self.db.room_facilities.edit_room_with_facilities(
            room_id, facilities_ids=room_data.facilities_ids
        )
        await self.db.session_commit()
        return await self.db.rooms.get_one(id=room_id)

    async def edit_room_partially(self, hotel_id: int, room_id: int, room_data: RoomPatchRequest):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        await self.check_missing_facilities_ids(room_data)

        _room_data_dict = room_data.model_dump(exclude_unset=True)
        if not _room_data_dict:
            raise ValidationException
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)

        await self.db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)

        if "facilities_ids" in _room_data_dict:
            await self.db.room_facilities.edit_room_with_facilities(
                room_id, facilities_ids=_room_data_dict["facilities_ids"]
            )
        await self.db.session_commit()
        return await self.db.rooms.get_one(hotel_id=hotel_id, id=room_id)

    async def delete_room(self, hotel_id: int, room_id: int):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.session_commit()

    async def get_room_with_check(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException

    async def check_missing_facilities_ids(self, data: RoomAddRequest | RoomPatchRequest) -> None:
        missing_ids = await FacilityService(self.db).get_missing_facility_with_check(
            facilities_ids=data.facilities_ids
        )
        if missing_ids:
            raise FacilityNotFoundCustomException(f"Удобства с ID {missing_ids} не найдены")
