import asyncpg
from asyncpg import Record
from typing import List

from app.models import UserToken

class DataBase:
    def __init__(self, host, port, user, database, password):
        self.host = host
        self.port = port
        self.user = user
        self.database = database
        self.password = password
        self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(host=self.host, port=self.port, user=self.user, database=self.database, password=self.password)
        print('Succesful CONNECTION!')

    async def select_query(self, query, *args):
        if not self.connection:
            await self.connect()
        async with self.connection.transaction():
            result = await self.connection.fetch(query, *args)
        return result

    async def exec_query(self, query, *args):
        if not self.connection:
            await self.connect()
        async with self.connection.transaction():
            await self.connection.execute(query, *args)

    async def insert_returning(self, query, *args):
        if not self.connection:
            await self.connect()
        async with self.connection.transaction():
            result = await self.connection.fetchval(query, *args)
            return result

    async def close_connection(self):
        if self.connection:
            await self.connection.close()


    #
    async def add_user(self, *args):
        query = '''INSERT INTO USERS (EMAIL, PASSWORD_HASH, LAST_NAME, FIRST_NAME, PATRONYMIC, IS_MODERATOR) VALUES ($1, $2, $3, $4, $5, $6) RETURNING ID;'''
        new_user_id = await self.insert_returning(query, *args[0:6])
        query = f"""INSERT INTO USER_CITY (CITY_ID, USER_ID) VALUES ($1, {new_user_id});"""
        await self.exec_query(query, args[-1])
        

    #
    async def get_user_by_email(self, email):
        query = '''SELECT ID, EMAIL, PASSWORD_HASH, IS_MODERATOR FROM USERS WHERE EMAIL = $1;'''
        result: List[Record]  = await self.select_query(query, email)
        #print(result[0]["id"])
        if result:
            user_data = result[0]
            user_token = UserToken(id=user_data["id"], email=user_data["email"], password=user_data["password_hash"], is_moderator=user_data["is_moderator"])
            return user_token
        else:
            return None

    #    
    async def get_user_by_id(self, id):
        query = '''SELECT * FROM USERS WHERE ID = $1;'''
        result: List[Record]  = await self.select_query(query, id)
        if result:
            return result
        else:
            return None
        
    # 
    async def update_user_password_by_user_id(self, new_password_hash, user_id):
        query = '''UPDATE USERS
                    SET PASSWORD_HASH = $1
                    WHERE ID = $2;'''
        await self.exec_query(query, new_password_hash, user_id)