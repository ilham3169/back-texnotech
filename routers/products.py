from typing import List, Annotated, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, status, Response # type: ignore

from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from sqlalchemy import and_

import logging

import pytz
from datetime import datetime

from redis import Redis

from .utils.services import get_redis, fill_cache_products, check_filters_products
from database import sessionLocal
from models import Product, Category, Brand, User, ProductSpecification, Image
from schemas import ProductCreate, ProductResponse, ProductUpdate



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
async def get_all_products(
        db: db_dependency, 
        redis: redis_dependency,

        category_id: Optional[int] = Query(None), 
        brand_id: Optional[int] = Query(None),
        available: Optional[bool] = Query(None),
        discount: Optional[bool] = Query(None),
        max_price: Optional[float] = Query(None),
        ): 
    
    try:
        
        # If there are products' data in cache and there is not any filter
        cached_products_keys= redis.keys("product:*")
        if cached_products_keys and not (category_id or brand_id or available or discount or max_price):

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
            # Get filters (if available)
            filters = check_filters_products(
                category_id, 
                brand_id,
                available,
                discount,
                max_price,
            )

            query = db.query(Product).filter(and_(*filters)).order_by(text("date_created DESC"))

            products = query.all()
            
            fill_cache_products(products, redis)
            return products
    
    # In case of any error, retrieve data from database
    except Exception as e:

        # Check if there any filters
        if not (category_id or brand_id or available or discount or max_price):
            products = db.query(Product).order_by(text("date_created DESC")).all()
        else:
            filters = check_filters_products(
                category_id, 
                brand_id,
                available,
                discount,
                max_price,
            )

            query = db.query(Product).filter(and_(*filters)).order_by(text("date_created DESC"))

            products = query.all()

        fill_cache_products(products, redis)

    return products


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: db_dependency): # type: ignore
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/add", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: db_dependency, redis: redis_dependency): # type: ignore
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

    redis.flushall()
    return new_product


@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_data: ProductUpdate, db: db_dependency, redis: redis_dependency):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Update only provided fields
    update_data = product_data.dict(exclude_unset=True)

    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {update_data['category_id']} does not exist."
            )

    if "brend_id" in update_data:
        brend = db.query(Brand).filter(Brand.id == update_data["brend_id"]).first()
        if not brend:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brend with id {update_data['brend_id']} does not exist."
            )

    for key, value in update_data.items():
        setattr(product, key, value)

    product.updated_at = datetime.now(TIMEZONE)

    db.commit()
    db.refresh(product)

    redis.flushall()
    return product



@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: db_dependency, redis: redis_dependency):  # type: ignore
    db.query(ProductSpecification).filter(ProductSpecification.product_id == product_id).delete()

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    redis.flushall()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
