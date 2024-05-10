import bcrypt

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils import get_user_by_email


from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Depends
import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError
#from jose import JWTError



async def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

async def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

async def create_access_token(data: dict, expires_delta = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authentificate_user(email, password):
    user = await get_user_by_email(email)
    #print(user.password)
    if not user:
        return False
    if not await check_password(password, (user.password).encode('utf-8')):
        return False
    print('PROVERKA PROSHLA!!!')
    return user

async def verify_token(token: str):
    credentials_exception1 = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception2 = HTTPException(
        status_code=401,
        detail="Signature has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        id: int = payload.get("sub")
        if id is None:
            raise credentials_exception1
    except InvalidSignatureError:
        raise credentials_exception1
    except ExpiredSignatureError:
        raise credentials_exception2
    return id