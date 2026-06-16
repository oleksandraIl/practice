from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)