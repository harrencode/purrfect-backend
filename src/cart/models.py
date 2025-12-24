from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class CartItem(BaseModel):
    product_id: UUID
    quantity: int = 1


class CreateOrderRequest(BaseModel):
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    items: List[CartItem]


class CreateOrderResponse(BaseModel):
    order_id: UUID
    whatsapp_url: str