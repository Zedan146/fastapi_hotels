from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.repositories.base import BaseRepository
from src.models.rooms import RoomsModel
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.rooms import Room, RoomWithRels


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_filtered_by_time(self, hotel_id, date_from: date, date_to: date):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id=hotel_id)

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsModel.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [RoomWithRels.model_validate(model) for model in result.scalars().all()]
