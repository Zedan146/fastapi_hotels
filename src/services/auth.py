from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext
import jwt
from pydantic import ValidationError

from src.config import settings
from src.exceptions import (
    IncorrectTokenException,
    ObjectAlreadyExistsException,
    UserAlreadyExistsException,
    EmailNotRegisteredException,
    IncorrectPasswordException,
    ValidationException,
)
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise IncorrectTokenException

    async def register_user(self, data: UserRequestAdd) -> None:
        if not data.password:
            raise ValidationException
        hashed_password = AuthService().hash_password(data.password)
        try:
            new_user_data = UserAdd(
                first_name=data.first_name,
                last_name=data.last_name,
                username=data.username,
                email=data.email,
                hashed_password=hashed_password,
            )
        except ValidationError as ex:
            raise ValidationException from ex
        try:
            await self.db.users.add(new_user_data)
            await self.db.session_commit()

        except ObjectAlreadyExistsException as ex:
            raise UserAlreadyExistsException from ex

    async def login_user(self, data: UserLogin) -> str:
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException
        return AuthService().create_access_token({"user_id": user.id})

    async def get_one_or_none_user(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)
