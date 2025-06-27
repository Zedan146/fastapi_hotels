from sqlalchemy import select
from src.schemas.rooms import Room
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsModel


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_all(self, hotel_id: int):
        query = select(self.model)
        if hotel_id:
            query = query.filter(self.model.hotel_id==hotel_id)

        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

        