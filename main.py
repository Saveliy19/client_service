from fastapi import FastAPI

from app.routes import router

from app.logger import logger, LoggingMiddleware
import time
from starlette.requests import Request
import time


app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Добавление логирующего middleware
app.add_middleware(LoggingMiddleware)

app.include_router(router)