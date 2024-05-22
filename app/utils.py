from app.db import DataBase
from asyncpg import Record
from typing import List
from app.models import UserToken

from app.config import host, port, user, database, password

import asyncio

db = DataBase(host, port, user, database, password)

#
async def add_user(*args):
    query = '''INSERT INTO USERS (EMAIL, PASSWORD_HASH, LAST_NAME, FIRST_NAME, PATRONYMIC, IS_MODERATOR) VALUES ($1, $2, $3, $4, $5, $6) RETURNING ID;'''
    print(*args[0:6])
    new_user_id = await db.insert_returning(query, *args[0:6])
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
    query = '''SELECT CITY_NAME, REGION_NAME
                FROM USERS JOIN USER_CITY
                ON USERS.ID = USER_CITY.USER_ID
                JOIN CITY
                ON CITY.ID = USER_CITY.CITY_ID
                JOIN REGION
                ON CITY.REGION_ID = REGION.ID
                WHERE USERS.ID = $1;'''
    result: List[Record]  = await db.select_query(query, id)
    data = result[0]
    return data

async def get_cities_per_region():
    query = '''SELECT REGION.REGION_NAME, CITY.CITY_NAME, CITY.ID
               FROM REGION JOIN CITY 
               ON REGION.ID = CITY.REGION_ID;'''
    cities_per_region = {}
    for record in (await db.select_query(query)):
        region_name = record['region_name']
        city_name = record['city_name']
        city_id = record['id']
        if region_name not in cities_per_region:
            cities_per_region[region_name] = []
        cities_per_region[region_name].append({city_name: city_id})
    
    return cities_per_region