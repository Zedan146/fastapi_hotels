from src.repositories.base import BaseRepository
from src.models.rooms import RoomsModel


class RoomsRepository(BaseRepository):
    models = RoomsModel
