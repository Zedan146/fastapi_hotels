from fastapi import APIRouter, HTTPException, Response, status

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import ObjectAlreadyExistsException
from src.services.auth import AuthService
from src.schemas.users import UserAdd, UserLogin, UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", summary="Регистрация клиента")
async def register_user(data: UserRequestAdd, db: DBDep):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
    )
    try:
        await db.users.add(new_user_data)
        await db.session_commit()

    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует!",
        )

    return {"status": "OK"}


@router.post("/login", summary="Авторизация клиента")
async def login_user(data: UserLogin, response: Response, db: DBDep):
    user = await db.users.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me", summary="Получение текущего пользователя")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post("/logout", summary="Выход из системы")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"status": "logout success"}
