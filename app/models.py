from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class User(BaseModel):   
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    is_moderator: bool

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

class Token(BaseModel):
    access_token: str
    token_type: str
