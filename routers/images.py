from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Product, Category, Brand, User, Image
from schemas import ImageResponse, ImageCreate
import logging
from datetime import datetime
import pytz # type: ignore


TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/images",
    tags=["images"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


@router.get("", response_model=List[ImageResponse], status_code=status.HTTP_200_OK)
async def get_all_images(db: db_dependency): # type: ignore
    images = db.query(Image).all()
    return images


@router.get("/{product_id}", response_model=List[ImageResponse], status_code=status.HTTP_200_OK)
async def get_images(product_id : int, db: db_dependency): # type: ignore
    images = db.query(Image).filter(Image.product_id == product_id).all()
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Images not found for products")
    return images

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int, db: db_dependency): # type: ignore

    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    db.delete(image)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/add", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(image_data: ImageCreate, db: db_dependency): # type: ignore
    
    brend = db.query(Brand).filter(Brand.id == image_data.id).first()               
    if brend:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image with id {image_data.id} exists. Existed brand name -> xxx"
        )
    
    new_image = Brand(**image_data.dict())
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@router.put("/{image_id}", response_model=ImageResponse, status_code=status.HTTP_200_OK)
async def update_image(image_id: int, image_data: ImageCreate, db: db_dependency): # type: ignore

    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    ip = db.query(Product).filter(Product.id == image_data.product_id).first()
    if not ip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    

    
    for key, value in image_data.dict().items():
        setattr(image, key, value)

    db.commit()
    db.refresh(image)
    return image