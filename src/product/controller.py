from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..database.core import get_db
from .models import ProductCreate, ProductResponse
from . import service as product_service
from fastapi import UploadFile, File
from ..utils.s3_service import upload_image_to_s3

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, payload)


@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return product_service.list_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)

@router.post("/upload-s3")
async def upload_product_image(
    file: UploadFile = File(...),
    folder: str = "products",  
):
    try:
        url = upload_image_to_s3(file, folder=folder)
        return {"url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e}",
        )