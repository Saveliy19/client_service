import asyncpg


class DataBase:
    def __init__(self, host, port, user, database, password):
        self.host = host
        self.port = port
        self.user = user
        self.database = database
        self.password = password
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(host=self.host, 
                                                  port=self.port, 
                                                  user=self.user, 
                                                  database=self.database, 
                                                  password=self.password, 
                                                  min_size=6,
                                                  max_size=10)
            print('Successful CONNECTION!')
        except asyncpg.PostgresError as e:
            print(f'Failed to connect to database: {e}')

    async def select_query(self, query, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            try:
                async with connection.transaction():
                    result = await connection.fetch(query, *args)
                    return result
            except asyncpg.PostgresError as e:
                print(f'Error executing SELECT query: {e}')
                return None
    
    async def select_one(self, query, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            try:
                async with connection.transaction():
                    result = await connection.fetchrow(query, *args)
                    return result
            except asyncpg.PostgresError as e:
                print(f'Error executing SELECT query: {e}')
                return None

    async def exec_query(self, query, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            try:
                async with connection.transaction():
                    await connection.execute(query, *args)
            except asyncpg.PostgresError as e:
                print(f'Error executing query: {e}')

    async def insert_returning(self, query, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            try:
                async with connection.transaction():
                    result = await connection.fetchval(query, *args)
                    return result
            except asyncpg.PostgresError as e:
                print(f'Error executing INSERT query: {e}')


    