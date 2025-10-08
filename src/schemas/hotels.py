from pydantic import BaseModel, Field, ConfigDict, validator


class HotelAdd(BaseModel):
    title: str = Field(min_length=1)
    location: str = Field(min_length=1)


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelPATCH(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)

    @validator('title', 'location')
    def validate_non_empty(cls, v):
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError('Поле не может быть пустым')
            return stripped
        return v
