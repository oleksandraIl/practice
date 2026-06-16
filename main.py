from fastapi import FastAPI
from routers.products import router as products_router
from routers.files import router as files_router
from routers.auth import router as auth_router
from utils.security import security

# Ініціалізація додатку без lifespan
app = FastAPI(title="My Store API")

# Обробка помилок AuthX (повертає 401 замість 500 при невалідному токені)
security.handle_errors(app)

# Підключення роутера з ендпойнтами продуктів [cite: 71, 79]
app.include_router(products_router)
# Підключення роутера для роботи з файлами
app.include_router(files_router)
# Підключення роутера авторизації
app.include_router(auth_router)

@app.get("/")
def index_root():
    return {"message": "Hello World!"}