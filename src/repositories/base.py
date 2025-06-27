from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

from schemas.hotels import Hotel


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs) -> list[Hotel]:
            query = select(self.model)
            result = await self.session.execute(query)
            return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by) -> Hotel|None:
            query = select(self.model).filter_by(**filter_by)
            result = await self.session.execute(query)
            model = result.scalars().one_or_none()
            if model is None:
                  return None
            return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel, **kwargs):
        add_data_stmt = insert(self.model).values({**data.model_dump(), **kwargs}).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)
    
    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
          edit_stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**data.model_dump(exclude_unset=exclude_unset))
                .returning(self.model)
           )
          result = await self.session.execute(edit_stmt)
          return result.scalars().all()


    async def delete(self, **filter_by) -> None:
          delete_stmt =  (
                delete(self.model)
                .filter_by(**filter_by)
                .returning(self.model)
          )
          result = await self.session.execute(delete_stmt)
          return result.scalars().all()