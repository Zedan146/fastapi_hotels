from fastapi import APIRouter, Response, Request

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import UserAlreadyExistsException, \
    UserEmailAlreadyExistsHTTPException, EmailNotRegisteredException, EmailNotRegisteredHTTPException, \
    IncorrectPasswordException, IncorrectPasswordHTTPException, ValidationException, \
    ValidationHTTPException
from src.services.auth import AuthService
from src.schemas.users import UserLogin, UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", summary="Регистрация клиента")
async def register_user(data: UserRequestAdd, db: DBDep):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserEmailAlreadyExistsHTTPException
    except ValidationException:
        raise ValidationHTTPException

    return {"status": "OK"}


@router.post("/login", summary="Авторизация клиента")
async def login_user(data: UserLogin, response: Response, request: Request, db: DBDep):
    try:
        access_token = await AuthService(db).login_user(data)
    except EmailNotRegisteredException:
        raise EmailNotRegisteredHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
    response.set_cookie("access_token", access_token)

    if request.cookies.get("access_token"):
        return {"detail": "Вы уже авторизованы!"}
    return {"access_token": access_token}


@router.get("/me", summary="Получение текущего пользователя")
async def get_me(user_id: UserIdDep, db: DBDep):
    return await AuthService(db).get_one_or_none_user(user_id)


@router.post("/logout", summary="Выход из системы")
async def logout_user(response: Response, request: Request):
    if not request.cookies.get("access_token"):
        return {"detail": "Вы не авторизованы"}
    response.delete_cookie("access_token")
    return {"status": "OK"}
