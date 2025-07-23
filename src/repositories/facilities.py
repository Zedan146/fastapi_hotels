from src.models.facilities import FacilitiesModel, RoomFacilitiesModel
from src.repositories.base import BaseRepository
from src.schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    schema = Facility


class RoomFacilitiesRepository(BaseRepository):
    model = RoomFacilitiesModel
    schema = RoomFacility
