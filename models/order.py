from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)