from pydantic import BaseModel, ConfigDict

from src.schemas.mixin import NonEmptyStringMixin


class FacilityAdd(NonEmptyStringMixin):
    title: str


class Facility(FacilityAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilityAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomFacility(RoomFacilityAdd):
    id: int
