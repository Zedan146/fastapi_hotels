from fastapi import APIRouter

from passlib.context import CryptContext

from src.repositories.users import UserRepository
from src.database import async_session_maker
from schemas.users import UserAdd, UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", summary="Регистрация клиента")
async def register_user(data: UserRequestAdd):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UserAdd(
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=data.email,
        hashed_password=hashed_password
    )
    async with async_session_maker() as session:
        await UserRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "OK"}