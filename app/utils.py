from app.db import DataBase
from asyncpg import Record
from typing import List
from app.models import UserToken

from app.config import host, port, user, database, password


db = DataBase(host, port, user, database, password)

# функция для внесения данных о новом пользователе в базу данных
async def add_user(*args):
    query = '''INSERT INTO USERS (EMAIL, PASSWORD_HASH, LAST_NAME, FIRST_NAME, PATRONYMIC, IS_MODERATOR) VALUES ($1, $2, $3, $4, $5, $6) RETURNING ID;'''
    await db.make_user(query, *args)
    

# функция для получения данных пользователя по его электронному адресу
async def get_user_by_email(email):
    query = '''select users.id as id, users.password_hash, users.email, users.is_moderator, city.city_name, region.region_name
            from users join user_city on users.id = user_city.user_id
            join city on user_city.city_id = city.id
            join region on city.region_id = region.id
            WHERE users.EMAIL = $1;'''
    result: List[Record]  = await db.select_query(query, email)
    if result:
        user_data = result[0]
        user_token = UserToken(id=user_data["id"],
                               email=user_data["email"], 
                               password=user_data["password_hash"], 
                               is_moderator=user_data["is_moderator"], 
                               region=user_data["region_name"],
                               city=user_data["city_name"])
        return user_token
    else:
        return None

# функция получения данных о пользователе по его идентификатору
async def get_user_by_id(id):
    query = '''SELECT * FROM USERS WHERE ID = $1;'''
    result: List[Record]  = await db.select_query(query, id)
    if result:
        data = result[0]
        return data
    else:
        return None
    

# получение города пользователя по его индентификатору
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

# получение списка городов в регионе
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