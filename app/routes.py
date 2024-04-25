from fastapi import APIRouter
from app.db import DataBase

from app.config import host, port, user, database, password

router = APIRouter()
db = DataBase(host, port, user, database, password)

@router.get("/insert")
async def insert():
    # Пример запроса на вставку данных в таблицу
    #insert_query = "INSERT INTO CITY (REGION, CITY_NAME) VALUES ($1, $2)"
    #await db.exec_query(insert_query, "Республика Коми", "Сыктывкар")
    result = await db.select_query('SELECT * FROM CITY;')
    await db.close_connection()
    return {"message": f'{result}'}

@router.post("/registration")
async def registration():
    pass