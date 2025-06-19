from sqlalchemy import select

from repositories.base import BaseRepository
from schemas.hotels import Hotel
from src.models.hotels import HotelsModel


class HotelsRepository(BaseRepository):
    model = HotelsModel
    schema = Hotel

    async def get_all(
            self,
            title,
            location,
            limit,
            offset,
    ) -> list[Hotel]:
        
        query = select(HotelsModel)
        if title:
            query = (
                query
                .filter(HotelsModel.title.ilike(f"%{title}%"))
            )
        if location:
            query = (
                query
                .filter(HotelsModel.location.ilike(f"%{location}%"))
            )
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        # Вывод сырого SQL-запроса в консоль
        print(query.compile(compile_kwargs={"literal_binds": True}))

        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
