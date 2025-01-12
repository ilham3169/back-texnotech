from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import text
from database import sessionLocal
from models import Product, Category, Brand, User
from schemas import ProductBase, ProductCreate, ProductResponse
import logging
# import pytz
from datetime import datetime


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
logger = logging.getLogger("uvicorn.error")
# TIMEZONE = pytz.timezone("Asia/Baku")

# Create a Product
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: db_dependency):
    new_product = Product(**product_data.dict())
    
    # Checking category_id 
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

    # Checking author_id
    # author_id = db.query(User).filter(User.id == product_data.author_id).first()
    # if not author_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Author id : {product_data.brend_id} does not exist."
    #     )
    # ????
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# Retrieve all Products 
@router.get("", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def get_all_products(db: db_dependency):
    products = db.query(Product).order_by(text("date_created DESC")).all()
    return products


# Retrieve single Product
@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: db_dependency):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# Update single Product
@router.put("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_data: ProductCreate, db: db_dependency):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
     # Checking category_id 
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
    
    for key, value in product_data.dict().items():
        setattr(product, key, value)

    # product.updated_at = datetime.now(TIMEZONE)


    db.commit()
    db.refresh(product)
    return product


# Delete single Product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: db_dependency):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
