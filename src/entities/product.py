
from sklearn import base
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database.core import Base



class Product(Base):
    __tablename__ = "products"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)

    stock = Column(Integer, nullable=False, default=0)  
    image_url = Column(String, nullable=True)
    affiliated_url = Column(String, nullable=True) # external link
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


def __repr__(self):
    return f"<Product name={self.name} price={self.price}>"