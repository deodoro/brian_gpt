import os
import tornado.ioloop
import tornado.web
import tornado.escape
import asyncio
import asyncpg

pool = None

async def make_pool():
    global pool
    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

class BaseHandler(tornado.web.RequestHandler):
    async def prepare(self):
        if not pool:
            await make_pool()

class YearsHandler(BaseHandler):
    async def get(self):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT DISTINCT year FROM questions ORDER BY year')
            self.write(tornado.escape.json_encode([row['year'] for row in result]))

class ExamsHandler(BaseHandler):
    async def get(self, year):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT DISTINCT exam FROM questions WHERE year = $1 ORDER BY exam', year)
            self.write(tornado.escape.json_encode([row['exam'] for row in result]))

class PartsHandler(BaseHandler):
    async def get(self, year, exam):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT DISTINCT part FROM questions WHERE year = $1 AND exam = $2 ORDER BY part', year, exam)
            self.write(tornado.escape.json_encode([row['part'] for row in result]))

class NumbersHandler(BaseHandler):
    async def get(self, year, exam, part):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT DISTINCT number FROM questions WHERE year = $1 AND exam = $2 AND part = $3 ORDER BY number', year, exam, part)
            self.write(tornado.escape.json_encode([row['number'] for row in result]))

class QuestionsByYearHandler(BaseHandler):
    async def get(self, year):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT addr, id FROM questions WHERE year = $1 ORDER BY part, number', year)
            self.write(tornado.escape.json_encode([dict(row) for row in result]))

class QuestionsByExamHandler(BaseHandler):
    async def get(self, year, exam):
        async with pool.acquire() as connection:
            print(f"year={year}, exam={exam}")
            result = await connection.fetch('SELECT addr, id FROM questions WHERE year = $1 AND exam = $2 ORDER BY part, number', year, exam)
            self.write(tornado.escape.json_encode([dict(row) for row in result]))

class QuestionsHandler(BaseHandler):
    async def get(self, year, exam, part, number):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT * FROM questions WHERE year = $1 AND exam = $2 AND part = $3 AND number = $4', year, exam, part, number)
            self.write(tornado.escape.json_encode([dict(row) for row in result]))

class QuestionHandler(BaseHandler):
    async def get(self, id):
        async with pool.acquire() as connection:
            result = await connection.fetch('SELECT * FROM questions WHERE id = $1', id)
            if not result:
                self.write({})
            else:
                self.write(tornado.escape.json_encode(dict(result[0])))
