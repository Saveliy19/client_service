from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegistration(BaseModel):   
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    is_moderator: bool
    city: int

class City(BaseModel):
    pass

# передача данных пользователя для аутентификации и получения токена
class UserToToken(BaseModel):
    email: EmailStr
    password: str   

# получение данных пользователя из бд для аутентификации и создания токена
class UserToken(BaseModel):
    id: int
    email: EmailStr
    password: str
    is_moderator: bool

class Token(BaseModel):
    access_token: str
    token_type: str
