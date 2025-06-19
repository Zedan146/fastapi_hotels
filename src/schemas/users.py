from pydantic import BaseModel, EmailStr


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    hashed_password: str


class UserRequestAdd(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
