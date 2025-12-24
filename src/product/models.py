from pydantic import BaseModel, HttpUrl
from uuid import UUID
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None  
    affiliated_url: Optional[str] = None  
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: UUID


    class Config:
        orm_mode = True