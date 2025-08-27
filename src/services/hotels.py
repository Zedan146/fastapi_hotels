from datetime import date

from src.api.dependencies import PaginationDep
from src.exceptions import check_date_to_after_date_from
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_hotels_by_time(
            self,
            pagination: PaginationDep,
            title: str | None,
            location: str | None,
            date_from: date,
            date_to: date,
    ):
        per_page = pagination.per_page or 5
        check_date_to_after_date_from(date_from, date_to)
        return await self.db.hotels.get_hotels_by_time(
            title=title,
            location=location,
            date_from=date_from,
            date_to=date_to,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: int):
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, hotel_data: HotelAdd):
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.session_commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        self.db.hotels.get_one(id=hotel_id)

        await self.db.hotels.edit(hotel_data, id=hotel_id)
        await self.db.session_commit()

    async def edit_hotel_partially(self, hotel_id: int, hotel_data: HotelPATCH):
        self.db.hotels.get_one(id=hotel_id)

        await self.db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
        await self.db.session_commit()

    async def delete_hotel(self, hotel_id: int):
        self.db.hotels.get_one(id=hotel_id)

        await self.db.hotels.delete(id=hotel_id)
        await self.db.session_commit()
