from datetime import date

from sqlalchemy import select

from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel
from src.models.hotels import HotelsModel


class HotelsRepository(BaseRepository):
    model = HotelsModel
    schema = Hotel

    # async def get_all(
    #         self,
    #         title,
    #         location,
    #         limit,
    #         offset,
    # ) -> list[Hotel]:
    #
    #     query = select(HotelsModel)
    #     if title:
    #         query = (
    #             query
    #             .filter(HotelsModel.title.ilike(f"%{title}%"))
    #         )
    #     if location:
    #         query = (
    #             query
    #             .filter(HotelsModel.location.ilike(f"%{location}%"))
    #         )
    #     query = (
    #         query
    #         .limit(limit)
    #         .offset(offset)
    #     )
    #     # Вывод сырого SQL-запроса в консоль
    #     # print(query.compile(compile_kwargs={"literal_binds": True}))
    #
    #     result = await self.session.execute(query)
    #     return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

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

        hotel_ids = (
            select(RoomsModel.hotel_id)
            .select_from(RoomsModel)
            .filter(RoomsModel.id.in_(rooms_ids_to_get))
        )

        if title:
            hotel_ids = (
                hotel_ids
                .filter(HotelsModel.title.ilike(f"%{title}%"))
            )
        if location:
            hotel_ids = (
                hotel_ids
                .filter(HotelsModel.location.ilike(f"%{location}%"))
            )
        hotel_ids = (
            hotel_ids
            .limit(limit)
            .offset(offset)
        )

        return await self.get_filtered(HotelsModel.id.in_(hotel_ids))
