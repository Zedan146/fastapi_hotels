from src.models.users import UsersModel
from src.repositories.base import BaseRepository
from src.schemas.users import User


class UserRepository(BaseRepository):
    model = UsersModel
    schema = User
    