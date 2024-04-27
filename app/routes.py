from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.db import DataBase

from app.config import host, port, user, database, password
from app.models import User, UserToToken, Token

from app.auth import hash_password, authentificate_user, create_access_token

from asyncpg.exceptions import UniqueViolationError

router = APIRouter()

# обработка аутетификаций по токену
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db = DataBase(host, port, user, database, password)

@router.post("/registration")
async def registration(user_data: User):
    try:
        user = await db.add_user(user_data.email, 
                                (await hash_password(user_data.password)).decode('utf-8'), 
                                user_data.last_name, 
                                user_data.first_name, 
                                user_data.patronymic)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/token")
async def login_for_access_token(user_data: UserToToken):
    user = await authentificate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer")


