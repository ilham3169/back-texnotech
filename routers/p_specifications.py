from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import text
from database import sessionLocal
from models import Product, Category, Brand, User, Category, ProductSpecification 
from schemas import ProductSpecificationResponse
import logging
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/p_specifications",
    tags=["p_specifications"]
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
async def get_all_p_specification(db: db_dependency):
    p_specification = db.query(ProductSpecification).all()
    return p_specification


@router.get("/{p_specification_id}", response_model=ProductSpecificationResponse, status_code=status.HTTP_200_OK)
async def get_p_specification(p_specification_id: int, db: db_dependency):
    p_specification = db.query(ProductSpecification).filter(ProductSpecification.id == p_specification_id).first()
    if not p_specification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Specification is not found")
    return p_specification