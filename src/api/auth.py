from fastapi import APIRouter, HTTPException, Response, Request

from api.dependencies import UserIdDep
from services.auth import AuthService
from src.repositories.users import UserRepository
from src.database import async_session_maker
from schemas.users import UserAdd, UserLogin, UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])

@router.post("/register", summary="Регистрация клиента")
async def register_user(data: UserRequestAdd):
    hashed_password = AuthService().hash_password(data.password)
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


@router.post("/login", summary="Авторизация клиента")
async def login_user(data: UserLogin, response: Response):
    async with async_session_maker() as session:
        user = await UserRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}
    

@router.get("/me", summary="Получение текущего пользователя")
async def get_me(user_id: UserIdDep):
    async with async_session_maker() as session:
        user = await UserRepository(session).get_one_or_none(id=user_id)
        return user
        
@router.get("/logout", summary="Выход из системы")
async def logout_user(responce: Response):
    responce.delete_cookie("access_token")
    return {"status": "logout sucсess"}