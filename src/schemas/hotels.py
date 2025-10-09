from pydantic import BaseModel, Field, ConfigDict

from src.schemas.mixin import NonEmptyStringMixin


class HotelAdd(BaseModel):
    title: str = Field(min_length=1)
    location: str = Field(min_length=1)


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelPATCH(NonEmptyStringMixin):
    title: str | None = Field(None)
    location: str | None = Field(None)

