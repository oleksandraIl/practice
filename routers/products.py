import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authx import RequestToken
from settings.db import get_db
from models.product import Product
from models.user import User
from schemas.product import ProductCreate, ProductRead, ProductUpdate
from services.pdf_generator import generate_simple_report
from utils.security import require_token

# Налаштування логування та роутера [cite: 71, 79, 80]
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Products"])

# Залежність для роботи з БД [cite: 81, 82]
SessionDepend = Annotated[AsyncSession, Depends(get_db)]

# Залежність: доступ лише для адміністратора
async def require_admin(token: Annotated[RequestToken, Depends(require_token)], session: SessionDepend) -> User:
    result = await session.execute(select(User).where(User.id == int(token.sub)))
    user = result.scalars().first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

# 1. Отримання списку товарів [cite: 86-102]
@router.get("/", response_model=list[ProductRead], tags=["Products"])
async def get_products(session: SessionDepend):
    try:
        result = await session.execute(select(Product))
        return result.scalars().all()
    except Exception as exc:
        logger.exception("Failed to get products")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get products") from exc

# 2. Генерація PDF-звіту зі списком товарів (оголошено до /{product_id}, інакше "report" зловиться як id)
@router.get("/report", summary="Generate a PDF report of all products", tags=["Products"])
async def get_products_report(session: SessionDepend):
    try:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        content_lines = [f"ID: {p.id} | {p.name} - {p.price}" for p in products]
        file_path = generate_simple_report("products_report.pdf", "Products Report", content_lines)
        return FileResponse(path=file_path, media_type="application/pdf", filename="products_report.pdf")
    except Exception as exc:
        logger.exception("Failed to generate products report")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate report") from exc

# 3. Отримання товару за ID [cite: 103-123]
@router.get("/{product_id}", response_model=ProductRead, tags=["Products"])
async def get_product(product_id: int, session: SessionDepend):
    try:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get product with id %d", product_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get product") from exc

# 4. Створення нового товару [cite: 124-144]
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(product_data: ProductCreate, session: SessionDepend, token: Annotated[RequestToken, Depends(require_token)]):
    try:
        new_product = Product(**product_data.model_dump())
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product
    except Exception as exc:
        logger.exception("Failed to create product")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product") from exc

# 5. Оновлення товару [cite: 145-174]
@router.put("/{product_id}", response_model=ProductRead, tags=["Products"])
async def update_product(product_id: int, product_update: ProductUpdate, session: SessionDepend):
    try:
        result = await session.execute(select(Product).where(Product.id == product_id))
        existing_product = result.scalars().first()
        if not existing_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
        for field, value in product_update.model_dump(exclude_unset=True).items():
            setattr(existing_product, field, value)
            
        session.add(existing_product)
        await session.commit()
        await session.refresh(existing_product)
        return existing_product
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update product with id %d", product_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product") from exc

# 6. Видалення товару [cite: 175-197]
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
async def delete_product(product_id: int, session: SessionDepend, admin: Annotated[User, Depends(require_admin)]):
    try:
        result = await session.execute(select(Product).where(Product.id == product_id))
        existing_product = result.scalars().first()
        if not existing_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
        await session.delete(existing_product)
        await session.commit()
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete product with id %d", product_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete product") from exc