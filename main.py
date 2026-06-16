from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import Base  # Імпортуємо Base, який "знає" про всі наші таблиці
from settings.db import engine  # Твій двигун бази даних

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Команда, яка створює таблиці в PostgreSQL, якщо їх ще немає
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Передаємо lifespan у FastAPI
app = FastAPI(lifespan=lifespan)

@app.get("/")
def index_root():
    return {"message": "Hello World!"}