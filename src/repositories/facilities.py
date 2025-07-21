from src.models.facilities import FacilitiesModel
from src.repositories.base import BaseRepository
from src.schemas.facilities import Facilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    schema = Facilities
