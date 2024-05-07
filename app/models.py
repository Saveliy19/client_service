from pydantic import BaseModel, EmailStr
from typing import Optional

# класс с данными, передаваемыми при регистрации нового пользователя
class UserRegistration(BaseModel):   
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    patronymic: str
    city: int

# класс с данными переданного токена пользователя
class TokenForData(BaseModel):
    token: str

# класс с данными передаваемыми при запросе информации о пользователе
class UserAbout(BaseModel):
    id: int
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    city: str
    region: str

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

# класс с возвращаемой информации при генерации access токена
class Token(BaseModel):
    access_token: str
    token_type: str

# класс с данными для смены пароля
class NewPassword(BaseModel):
    token: str
    password: str
