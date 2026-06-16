from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import Base
from settings.db import engine
from routers.products import router as products_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Автоматичне створення таблиць в базі даних при запуску додатку [cite: 108-111]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Ініціалізація додатку з налаштуванням lifespan [cite: 115]
app = FastAPI(lifespan=lifespan)

# Підключення роутера з ендпойнтами продуктів [cite: 271]
app.include_router(products_router)

@app.get("/")
def index_root():
    return {"message": "Hello World!"}