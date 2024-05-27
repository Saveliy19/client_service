import bcrypt  # Библиотека для работы с хэшированием паролей

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Импорт настроек из конфигурационного файла
from app.utils import get_user_by_email  # Импорт функции для получения пользователя по email

from datetime import datetime, timedelta, timezone  # Импорт необходимых модулей для работы с датой и временем
from fastapi import HTTPException  # Импорт HTTPException для обработки исключений
import jwt  # Библиотека для работы с JSON Web Tokens (JWT)
from jwt import InvalidSignatureError, ExpiredSignatureError  # Импорт ошибок для обработки некорректных и просроченных JWT


# функция для хэширования пароля
async def hash_password(password):
    salt = bcrypt.gensalt()  # Генерация соли
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Хэширование пароля с использованием "соли"
    return hashed_password  

# Функция для проверки пароля
async def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# функция для создания JWT токена 
async def create_access_token(data: dict):
    to_encode = data.copy()  # Копирование данных для включения в токен
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # время валидности истечения токена
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция аутентификации пользователя
async def authentificate_user(email, password):
    user = await get_user_by_email(email)
    if not user:
        return False
    if not await check_password(password, (user.password).encode('utf-8')):
        return False
    return user

# функция верификации токена
async def verify_token(token: str):
    credentials_exception1 = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )  # Исключение для недействительных учетных данных
    credentials_exception2 = HTTPException(
        status_code=401,
        detail="Signature has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )  # Исключение для просроченных токенов
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Декодирование токена
        id: int = payload.get("sub")  
        is_moderator: bool = payload.get("is_moderator")  
        email: str = payload.get("email") 
        city: str = payload.get("city")  
        region: str = payload.get("region") 
        if (id is None) or (is_moderator is None) or (email is None): 
            raise credentials_exception1 
    except InvalidSignatureError:
        raise credentials_exception1  
    except ExpiredSignatureError:
        raise credentials_exception2  
    return {"id": id, "is_moderator": is_moderator, "email": email, "city": city, "region": region}  
