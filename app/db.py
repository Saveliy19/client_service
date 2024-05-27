import asyncpg  # Библиотека для асинхронной работы с PostgreSQL

# Класс для управления подключением к базе данных и выполнения запросов
class DataBase:
    def __init__(self, host, port, user, database, password):
        self.host = host  
        self.port = port  
        self.user = user  
        self.database = database  
        self.password = password  
        self.pool = None  # Пул соединений, будет инициализирован при подключении

    # функция для подключения к базе данных и создания пула соединений
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            database=self.database,
            password=self.password,
            min_size=6,  # Минимальное количество соединений в пуле
            max_size=10  # Максимальное количество соединений в пуле
        )

    async def select_query(self, query, *args):
        if not self.pool:  # Проверка, создан ли пул соединений
            await self.connect()  # Подключение к базе данных, если еще не подключены
        async with self.pool.acquire() as connection:  # Захват соединения из пула
            async with connection.transaction():  # Создание транзакции
                result = await connection.fetch(query, *args)  # Выполнение запроса
                return result  

    # функция для выполнения SELECT запроса, возвращающего только 1 строку
    async def select_one(self, query, *args):
        if not self.pool:  
            await self.connect()  
        async with self.pool.acquire() as connection: 
            async with connection.transaction():  
                result = await connection.fetchrow(query, *args)  
                return result 


    async def exec_query(self, query, *args):
        if not self.pool:  
            await self.connect() 
        async with self.pool.acquire() as connection:  
            async with connection.transaction():  
                await connection.execute(query, *args) 

    # функция для выполнения INSERT запроса, возвращающего значение
    async def make_user(self, query, *args):
        if not self.pool:  
            await self.connect()  
        async with self.pool.acquire() as connection:  
            async with connection.transaction():
                new_user_id = await connection.fetchval(query, *args[0:6])
                query2 = f"""INSERT INTO USER_CITY (CITY_ID, USER_ID) VALUES ($1, {new_user_id});"""
                # Выполнение запроса на добавление данных о городе для нового пользователя
                await connection.execute(query2, args[-1])
