from typing import TypeVar

from pydantic import BaseModel

from src.database import Base

DBModel = TypeVar("DBModel", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper:
    db_model: type[DBModel] = None
    schema: type[SchemaType] = None

    @classmethod
    def map_to_domain_entity(cls, data):
        """Принимаем данные из ОРМ модели и превращаем их в Pydantic схему"""
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        """Принимаем данные из Pydantic схемы и превращаем их в ОРМ модель"""
        return cls.db_model(**data.model_dump())
