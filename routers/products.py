from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore

from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore

import logging

import pytz
from datetime import datetime

from redis import Redis

from .utils.services import get_redis, fill_cache_products
from database import sessionLocal
from models import Product, Category, Brand, User
from schemas import ProductCreate, ProductResponse



router = APIRouter(
    prefix="/products",
    tags=["products"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
redis_dependency = Annotated[Redis, Depends(get_redis)]
logger = logging.getLogger("uvicorn.error")
TIMEZONE = pytz.timezone("Asia/Baku")


@router.get("", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def get_all_products(db: db_dependency, redis: redis_dependency): # type: ignore
    try:
        
        # If there are products' data in cache
        cached_products_keys= redis.keys("product:*")
        if cached_products_keys:

            baku_timezone = pytz.timezone("Asia/Baku")

            # Get the current time in the Baku timezone
            baku_time = datetime.now(baku_timezone).hour
            # CLear & refill the cached data at 8 AM everyday
            if baku_time == 8:

                products = db.query(Product).order_by(text("date_created DESC")).all()
                
                fill_cache_products(products, redis)
                return products

            # Get products' data tom cache
            products = []
            for key in cached_products_keys:
                product = redis.hgetall(key)
                decoded_product = {k.decode('utf-8'): v.decode('utf-8') for k, v in product.items()}

                products.append(decoded_product)

            return products

        # If no products' data in cache
        else:
            products = db.query(Product).order_by(text("date_created DESC")).all()
            
            fill_cache_products(products, redis)
                
            return products
    
    # In case of any error, retrieve data from database
    except Exception as e:

        products = db.query(Product).order_by(text("date_created DESC")).all()
        
        fill_cache_products(products, redis)

    return products


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: db_dependency): # type: ignore
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/add", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: db_dependency): # type: ignore
    new_product = Product(**product_data.dict())
    
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {product_data.category_id} does not exist."
        )
    
    # Checking brend_id
    brend = db.query(Brand).filter(Brand.id == product_data.brend_id).first()
    if not brend:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brend with id {product_data.brend_id} does not exist."
        )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_data: ProductCreate, db: db_dependency):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {product_data.category_id} does not exist."
        )
    
    brend = db.query(Brand).filter(Brand.id == product_data.brend_id).first()
    if not brend:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brend with id {product_data.brend_id} does not exist."
        )
    
    for key, value in product_data.dict().items():
        setattr(product, key, value)

    product.updated_at = datetime.now(TIMEZONE)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: db_dependency): # type: ignore

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
