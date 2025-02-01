from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Product, Category, Brand, User, Category, ProductSpecification, Specification
from schemas import  ProductSpecificationResponse, ProductSpecificationCreate, ProductSpecificationBase
import logging
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/p_specification",
    tags=["p_specification"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")

@router.get("", response_model=List[ProductSpecificationResponse], status_code=status.HTTP_200_OK)
async def get_all_p_specification(db: db_dependency): # type: ignore
    p_specification = db.query(ProductSpecification).all()
    return p_specification


@router.get("/{p_specification_id}", response_model=ProductSpecificationResponse, status_code=status.HTTP_200_OK)
async def get_p_specification(p_specification_id: int, db: db_dependency):
    p_specification = db.query(ProductSpecification).filter(ProductSpecification.id == p_specification_id).first()
    
    if not p_specification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product specification is not found")
    
    return p_specification


@router.delete("/{p_specification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_p_specification(p_specification_id: int, db: db_dependency): # type: ignore
    p_specification = db.query(ProductSpecification).filter(ProductSpecification.id == p_specification_id).first()
    if not p_specification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Specification not found")
    
    db.delete(p_specification)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post("", response_model=ProductSpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_product_specification(p_specification_data: ProductSpecificationCreate, db: db_dependency):  # type: ignore
    product = db.query(Product).filter(Product.id == p_specification_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found with the specified ID."
        )

    specification = db.query(Specification).filter(Specification.id == p_specification_data.specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Specification not found with the specified ID."
        )
    
    new_p_specification = ProductSpecification(**p_specification_data.dict())
    db.add(new_p_specification)
    db.commit()
    db.refresh(new_p_specification)
    return new_p_specification


@router.put("/{p_specification_id}", response_model=ProductSpecificationResponse, status_code=status.HTTP_200_OK)
async def update_p_specification(p_specification_id: int, p_specification_data: ProductSpecificationBase, db: db_dependency):  # type: ignore

    p_specification = db.query(ProductSpecification).filter(ProductSpecification.id == p_specification_id).first()
    if not p_specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product specification not found with the specified ID."
        )

    product = db.query(Product).filter(Product.id == p_specification_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found with the specified ID."
        )

    specification = db.query(Specification).filter(Specification.id == p_specification_data.specification_id).first()
    if not specification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Specification not found with the specified ID."
        )
    

    if int(p_specification_data.value) < 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Value cannot be negative"
        )
    
    for key, value in p_specification_data.dict().items():
        setattr(p_specification, key, value)

    p_specification.updated_at = datetime.now(TIMEZONE)
    db.commit()
    db.refresh(p_specification)
    return p_specification


# Get all specifications of a Product with id = product_id
@router.get("/values/{product_id}",  status_code=status.HTTP_200_OK)
async def get_product_specifications(product_id: int, db: db_dependency): 

    p_specifications = (
        db.query(ProductSpecification)
        .join(Specification, ProductSpecification.specification_id == Specification.id)
        .filter(ProductSpecification.product_id == product_id)
        .options(joinedload(ProductSpecification.specification)) 
        .all()
    )

    data = [
        {
            "id": p_specification.id,
            "name": p_specification.specification.name,
            "value": p_specification.value,
            "category_id": p_specification.specification.category_id,
        }
        for p_specification in p_specifications
    ]

    return data
