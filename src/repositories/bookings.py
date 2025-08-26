from datetime import date

from pydantic import BaseModel
from sqlalchemy import select

from fastapi import HTTPException

from src.models import RoomsModel
from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import rooms_ids_for_booking


class BookingsRepository(BaseRepository):
    model = BookingsModel
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = (
            select(BookingsModel)
            .filter(BookingsModel.date_from == date.today())
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(
            self,
            data: BaseModel,
            hotel_id: int,
            room_id: int,
            date_from: date,
            date_to: date
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id=hotel_id)

        query = (
            select(RoomsModel.id)
            .filter(RoomsModel.id.in_(rooms_ids_to_get))

        )
        result = await self.session.execute(query)
        rooms_ids_db = result.scalars().all()

        if room_id not in rooms_ids_db:
            raise HTTPException(status_code=500, detail="Нельзя забронировать комнату на выбранные даты!")

        return await self.add(data)
