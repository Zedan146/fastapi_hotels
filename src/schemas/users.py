from pydantic import BaseModel, EmailStr


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRequestAdd(UserLogin):
    first_name: str
    last_name: str
    username: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr


class UserWithHashedPassword(User):
    hashed_password: str
