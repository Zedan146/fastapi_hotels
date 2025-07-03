from src.repositories.base import BaseRepository
from src.models.rooms import RoomsModel
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room
