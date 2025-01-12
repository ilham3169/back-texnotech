from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import text
from database import sessionLocal
from models import Product, Category, Brand, User
from schemas import BrandResponse, BrandBase, BrandCreate
import logging
from datetime import datetime
# import pytz


# TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/brands",
    tags=["brands"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


# Retrieve all Brands
@router.get("", response_model=List[BrandResponse], status_code=status.HTTP_200_OK)
async def get_all_brands(db: db_dependency):
    brands = db.query(Brand).order_by(text("date_created DESC")).all()
    return brands


# Retrieve single Brand
@router.get("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_200_OK)
async def get_brand(brand_id: int, db: db_dependency):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


# Update single Brand
@router.put("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_200_OK)
async def update_brand(brand_id: int, brand_data: BrandResponse, db: db_dependency):

    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
 
    # Checking brand_name
    brand_name = db.query(Brand).filter(Brand.name == brand_data.name).first()
    if brand_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {brand_data.name} exists."
        )
    
    for key, value in brand_data.dict().items():
        setattr(brand, key, value)

    # brand.updated_at = datetime.now(TIMEZONE)
    db.commit()
    db.refresh(brand)
    return brand


# Create a Brand
@router.post("/add", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand_data: BrandResponse, db: db_dependency):
    
    # Checking ID of Brand
    brend = db.query(Brand).filter(Brand.id == brand_data.id).first()               
    if brend:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brand with id {brand_data.id} exists. Existed brand name -> xxx"
        )
    
    new_brand = Brand(**brand_data.dict())
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand


# Delete a Brand
@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: int, db: db_dependency):

    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    
    db.delete(brand)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
