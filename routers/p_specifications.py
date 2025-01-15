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
    prefix="/categories",
    tags=["categories"]
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
async def get_all_p_specifications(db: db_dependency):
    p_specification = db.query(Category).order_by(text("date_created DESC")).all()
    return p_specification


