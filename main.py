from fastapi import FastAPI
from routers.products import router as products_router
from routers.files import router as files_router

# Ініціалізація додатку без lifespan
app = FastAPI(title="My Store API")

# Підключення роутера з ендпойнтами продуктів [cite: 71, 79]
app.include_router(products_router)
# Підключення роутера для роботи з файлами
app.include_router(files_router)

@app.get("/")
def index_root():
    return {"message": "Hello World!"}