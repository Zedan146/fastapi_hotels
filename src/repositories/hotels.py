from datetime import date

from sqlalchemy import select, func

from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel
from src.models.hotels import HotelsModel


class HotelsRepository(BaseRepository):
    model = HotelsModel
    mapper = HotelDataMapper

    async def get_hotels_by_time(
        self,
        date_from: date,
        date_to: date,
        title: str,
        location: str,
        limit: int,
        offset: int,
    ) -> list[Hotel]:
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)

        hotels_ids_to_get = (
            select(RoomsModel.hotel_id)
            .select_from(RoomsModel)
            .filter(RoomsModel.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsModel).filter(HotelsModel.id.in_(hotels_ids_to_get))

        if title:
            query = query.filter(func.lower(HotelsModel.title).contains(title.strip().lower()))
        if location:
            query = query.filter(
                func.lower(HotelsModel.location).contains(location.strip().lower())
            )
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
