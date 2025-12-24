from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.core import get_db
from .models import CreateOrderRequest, CreateOrderResponse
from .service import create_order
from ..entities.order import Order


router = APIRouter(prefix="/cart", tags=["Cart & Orders"])


@router.post("/checkout", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(payload: CreateOrderRequest, db: Session = Depends(get_db)):
    order, whatsapp_url = create_order(db, payload)
    return CreateOrderResponse(order_id=order.id, whatsapp_url=whatsapp_url)


@router.get("/recent")
def get_recent_orders(db: Session = Depends(get_db)):
    
    #Returns the 10 most recent orders with their items.
   
    # change the logic to show only last week’s orders 
    orders = (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    )

    # Convert SQLAlchemy objects to JSON-serializable dicts
    result = []
    for o in orders:
        result.append({
            "id": str(o.id),
            "buyer_name": o.buyer_name,
            "date": o.created_at.isoformat(),
            "total": float(o.total_amount),
            "items": [
                {
                    "product_id": str(i.product_id),
                    "name": i.product_name,
                    "quantity": i.quantity,
                    "price": float(i.unit_price)
                }
                for i in o.items
            ],
        })

    return result