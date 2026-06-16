from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class OrderItems(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)