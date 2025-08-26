from typing import Sequence, Any

from asyncpg.exceptions import UniqueViolationError

from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError
from pydantic import BaseModel

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    schema: BaseModel = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filters, **filter_by):
        query = select(self.model).filter(*filters).filter_by(**filter_by)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> BaseModel | None | Any:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException

        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel, **kwargs):
        try:
            add_data_stmt = (
                insert(self.model).values({**data.model_dump(), **kwargs}).returning(self.model)
            )
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex
            else:
                raise ex

    async def add_bulk(self, data: Sequence[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by):
        edit_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self.session.execute(edit_stmt)
        model = result.scalar_one()

        return self.mapper.map_to_domain_entity(model)

    async def edit_bulk(
        self, data: list[BaseModel], exclude_unset: bool = False, **filter_by
    ) -> None:
        edit_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values([item.model_dump(exclude_unset=exclude_unset) for item in data])
        )
        await self.session.execute(edit_stmt)

    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
