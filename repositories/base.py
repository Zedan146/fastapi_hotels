from sqlalchemy import select, insert

from src.models.hotels import HotelsModel


class BaseRepository:
    model = HotelsModel

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
            query = select(self.model)
            result = await self.session.execute(query)
            return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
            query = select(self.model).filter_by(**filter_by)
            result = await self.session.execute(query)
            return result.scalars().one_or_none()

    async def add(self, hotel_data):
        add_hotel_stmt = insert(self.model).values(**hotel_data.model_dump())
        await self.session.execute(add_hotel_stmt)
        return hotel_data
