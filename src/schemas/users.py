from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserAdd(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    email: EmailStr
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


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

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str
