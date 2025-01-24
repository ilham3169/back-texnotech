from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Specification, Category
from schemas import SpecificationResponse, SpecificationCreate
import logging
from datetime import datetime
import pytz # type: ignore

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/specifications",
    tags=["specifications"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


@router.get("", response_model=List[SpecificationResponse], status_code=status.HTTP_200_OK)
async def get_all_specification(db: db_dependency): # type: ignore
    specification = db.query(Specification).all()
    return specification


@router.get("/{specification_id}", response_model=SpecificationResponse, status_code=status.HTTP_200_OK)
async def get_specification(specification_id: int, db: db_dependency): # type: ignore
    specification = db.query(Specification).filter(Specification.id == specification_id).first()
    if not specification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")
    return specification


@router.delete("/{specification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specification(specification_id: int, db: db_dependency): # type: ignore

    specification = db.query(Specification).filter(Specification.id == specification_id).first()
    if not specification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")
    
    db.delete(specification)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/add", response_model=SpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_specification(specification_data: SpecificationCreate, db: db_dependency): # type: ignore

    category = db.query(Category).filter(Category.id == specification_data.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category id is not found")
    
    new_specification = Specification(**specification_data.dict())
    db.add(new_specification)
    db.commit()
    db.refresh(new_specification)
    return new_specification
 