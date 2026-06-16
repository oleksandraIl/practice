from typing import Optional
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(max_length=100)
    price: float = Field(gt=0)

class ProductRead(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True # дозволяє читати дані з SQLAlchemy моделей

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    price: Optional[float] = Field(default=None, gt=0)