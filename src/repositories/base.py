from fastapi import HTTPException

from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
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
        delete_stmt = (
            delete(self.model)
            .filter_by(**filter_by)
            .returning(self.model)
        )
        try:

            result = await self.session.execute(delete_stmt)

        except IntegrityError:
            raise HTTPException(400, detail="Нельзя удалить: есть связанные ссылки. Сначала удалите их.")

        return result.scalars().all()
