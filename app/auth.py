import bcrypt

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Depends
import jwt


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

async def authentificate_user(db, email, password):
    user = await db.get_user_by_email(email)
    #print(user.password)
    if not user:
        return False
    if not await check_password(password, (user.password).encode('utf-8')):
        return False
    print('PROVERKA PROSHLA!!!')
    return user