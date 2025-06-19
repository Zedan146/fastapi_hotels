from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel
from fastapi import HTTPException


class BaseRepository:
    model = None

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

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalars().one()
    
    async def edit(self, data: BaseModel, **filter_by) -> None:
          edit_data = (
                update(self.model)
                .where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
                .values(**data.model_dump())
                .returning(self.model)
           )
          result = await self.session.execute(edit_data)
          return result.scalars().all()


    async def delete(self, **filter_by) -> None:
          delete_data =  (
                delete(self.model)
                .where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
                .returning(self.model)
          )
          result = await self.session.execute(delete_data)
          return result.scalars().all()