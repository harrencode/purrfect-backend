from sqlalchemy.orm import Session
from ..entities.product import Product
from .models import ProductCreate
from uuid import UUID
from fastapi import HTTPException, status




def create_product(db: Session, product_in: ProductCreate) -> Product:
    p = Product(**product_in.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p




def list_products(db: Session):
    return db.query(Product).filter(Product.is_active == True).all()




def get_product(db: Session, product_id: UUID) -> Product:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return p