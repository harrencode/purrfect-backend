from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base




class Order(Base):
    __tablename__ = "orders"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_name = Column(String, nullable=True)
    buyer_phone = Column(String, nullable=True)
    total_amount = Column(Numeric(10,2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    sent_to_whatsapp = Column(Boolean, nullable=False, default=False)


    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10,2), nullable=False, default=0)


    order = relationship("Order", back_populates="items")