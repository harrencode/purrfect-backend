from sqlalchemy.orm import Session
from ..entities.order import Order, OrderItem
from ..entities.product import Product
from .models import CreateOrderRequest
from decimal import Decimal
from fastapi import HTTPException, status
import os
import urllib.parse

WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")  # e.g. 94771234567 (no plus)

if not WHATSAPP_NUMBER:
    print("Warning: WHATSAPP_NUMBER not set in environment variables; WhatsApp integration disabled")


def create_order(db: Session, payload: CreateOrderRequest):
    # Basic validation
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
        )

    try:
        total = Decimal("0.00")

        # Create order but DON'T commit yet
        order = Order(
            buyer_name=payload.buyer_name,
            buyer_phone=payload.buyer_phone,
        )
        db.add(order)
        db.flush()  # get order.id without committing

        # Create order items + update stock
        for it in payload.items:
            product = (
                db.query(Product)
                # .with_for_update()  
                .filter(Product.id == it.product_id)
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {it.product_id} not found",
                )

            # Check available stock
            if product.stock < it.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for {product.name}. "
                           f"Available: {product.stock}, requested: {it.quantity}",
                )

            unit = Decimal(str(product.price))
            line_total = unit * it.quantity
            total += line_total

            # Subtract stock
            product.stock -= it.quantity

            # Create order item
            oi = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=it.quantity,
                unit_price=unit,
            )
            db.add(oi)

        # Set total and WhatsApp message
        order.total_amount = total

        lines = []
        lines.append("New order from webstore:")
        if payload.buyer_name:
            lines.append(f"Name: {payload.buyer_name}")
        if payload.buyer_phone:
            lines.append(f"Phone: {payload.buyer_phone}")
        lines.append("")
        for item in order.items:
            lines.append(
                f"- {item.product_name} x{item.quantity} @ {item.unit_price} = {item.unit_price * item.quantity}"
            )
        lines.append("")
        lines.append(f"Total: {order.total_amount}")
        lines.append(f"Order ID: {order.id}")

        message = "\n".join(lines)
        encoded = urllib.parse.quote(message)

        if WHATSAPP_NUMBER:
            whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"
            order.sent_to_whatsapp = True
        else:
            whatsapp_url = "about:blank"

        # Single commit for order + items + stock changes
        db.commit()
        db.refresh(order)

        return order, whatsapp_url

    except HTTPException:
        # propagate business errors but rollback DB
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {e}",
        )
