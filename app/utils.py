from app.db import DataBase
from asyncpg import Record
from typing import List
from app.models import UserToken

from app.config import host, port, user, database, password

import asyncio

db = DataBase(host, port, user, database, password)

#
async def add_user(*args):
    query = '''INSERT INTO USERS (EMAIL, PASSWORD_HASH, LAST_NAME, FIRST_NAME, PATRONYMIC) VALUES ($1, $2, $3, $4, $5) RETURNING ID;'''
    new_user_id = await db.insert_returning(query, *args[0:5])
    query = f"""INSERT INTO USER_CITY (CITY_ID, USER_ID) VALUES ($1, {new_user_id});"""
    await db.exec_query(query, args[-1])
    

#
async def get_user_by_email(email):
    query = '''SELECT ID, EMAIL, PASSWORD_HASH, IS_MODERATOR FROM USERS WHERE EMAIL = $1;'''
    result: List[Record]  = await db.select_query(query, email)
    #print(result[0]["id"])
    if result:
        user_data = result[0]
        user_token = UserToken(id=user_data["id"], email=user_data["email"], password=user_data["password_hash"], is_moderator=user_data["is_moderator"])
        return user_token
    else:
        return None

#    
async def get_user_by_id(id):
    query = '''SELECT * FROM USERS WHERE ID = $1;'''
    result: List[Record]  = await db.select_query(query, id)
    if result:
        data = result[0]
        return data
    else:
        return None
    
# 
async def update_user_password_by_user_id(new_password_hash, user_id):
    query = '''UPDATE USERS
                SET PASSWORD_HASH = $1
                WHERE ID = $2;'''
    await db.exec_query(query, new_password_hash, user_id)


async def get_city_by_user_id(id):
    query = '''SELECT CITY_NAME, REGION
                FROM USERS JOIN USER_CITY
                ON USERS.ID = USER_CITY.USER_ID
                JOIN CITY
                ON CITY.ID = USER_CITY.CITY_ID
                WHERE USERS.ID = $1;'''
    result: List[Record]  = await db.select_query(query, id)
    data = result[0]
    return data