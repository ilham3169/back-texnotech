from typing import List, Annotated, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, status, Response # type: ignore

from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from sqlalchemy import and_

import logging

import pytz
from datetime import datetime, timedelta

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
    search_query: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1), 
    page_size: Optional[int] = Query(None, ge=1, le=100)
):
    logger.info(f"Request: page={page}, page_size={page_size}")
    try:
        # Clear Redis cache before every request
        redis.flushall()
        logger.info("Redis cache cleared")

        if (page and page_size):
            offset = (page - 1) * page_size
        else:
            offset = 0
        
        # Since Redis is cleared, skip the caching check
        if search_query:
            query = db.query(Product).filter(Product.search_string.ilike(f"%{search_query}%"))\
                .order_by(text("date_created DESC"))\
                .offset(offset)
            products = query.limit(page_size).all() if page_size else query.all()
            logger.info(f"Search query, fetched {len(products)} products")
            fill_cache_products(products, redis)
            return products

        else:
            if category_id:
                categories = db.query(Category).filter(Category.parent_category_id == category_id).all()
                category_ids = [category.id for category in categories]
                category_ids.append(category_id)
                logger.info(f"Category IDs: {category_ids}")
            filters = check_filters_products(brand_id, available, discount, max_price)
            logger.info(f"Filters applied: {filters}")
            
            if category_id:
                query = db.query(Product).filter(Product.category_id.in_(category_ids), *filters)\
                    .order_by(text("date_created DESC"))\
                    .offset(offset)
            else:
                query = db.query(Product).filter(and_(*filters))\
                    .order_by(text("date_created DESC"))\
                    .offset(offset)
            
            logger.info(f"Query: {str(query)}")
            products = query.limit(page_size).all() if page_size else query.all()
            logger.info(f"Fetched {len(products)} products")
            fill_cache_products(products, redis)
            return products
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        # Clear Redis in case of exception too
        redis.flushall()
        logger.info("Redis cache cleared in exception block")
        # Repeat logic
        if category_id:
            categories = db.query(Category).filter(Category.parent_category_id == category_id).all()
            category_ids = [category.id for category in categories]
            category_ids.append(category_id)
        filters = check_filters_products(brand_id, available, discount, max_price)
        if category_id:
            query = db.query(Product).filter(Product.category_id.in_(category_ids), *filters)\
                .order_by(text("date_created DESC"))\
                .offset(offset)
        else:
            query = db.query(Product).filter(and_(*filters))\
                .order_by(text("date_created DESC"))\
                .offset(offset)
        products = query.limit(page_size).all() if page_size else query.all()
        logger.info(f"Exception block fetched {len(products)} products")
        fill_cache_products(products, redis)
        return products


@router.get("/new-arrivals", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def get_new_products(
        db: db_dependency,
    ):

    products = db.query(
        Product
        ).filter(Product.date_created > (datetime.now() - timedelta(days=7))
        ).order_by(text("date_created DESC")
        ).limit(10).all()
    
    return products

@router.get("/is_super", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def get_super_products(
        db: db_dependency,
    ):

    products = db.query(
        Product
        ).filter(Product.is_super
        ).order_by(text("date_created DESC")
        ).limit(10).all()
    
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

    db.execute(text("UNLOCK TABLES;"))
    
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
