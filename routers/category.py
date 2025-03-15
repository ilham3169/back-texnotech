from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore

import logging
from datetime import datetime
import pytz 

from database import sessionLocal
from models import Category, Specification, Product
from schemas import CategoryResponse, CategoryBase, CategoryCreate, ChildCategoryCreate


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


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_all_categories(db: db_dependency): # type: ignore
    category = db.query(Category).order_by(text("date_created DESC")).all()
    return category
 

@router.get("/parent", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_parent_categories(db: db_dependency): # type: ignore
    category = db.query(Category).filter(Category.parent_category_id == None).order_by(text("date_created DESC")).all()
    return category


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, db: db_dependency): # type: ignore
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: db_dependency):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    try:
        db.query(Specification).filter(Specification.category_id == category_id).delete(synchronize_session=False)
        db.query(Product).filter(Product.category_id == category_id).delete(synchronize_session=False)
        db.delete(category)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting category: {str(e)}")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/add", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: db_dependency): # type: ignore
    
    category = db.query(Category).filter(Category.name == category_data.name).first()               
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {category_data.name} exists."
        )
    
    if category_data.num_category < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category number cannot be negative"
        )
    
    new_category = Category(**category_data.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.post("/child/add", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_child_category(category_data: ChildCategoryCreate, db: db_dependency): # type: ignore
    
    category = db.query(Category).filter(Category.name == category_data.name).first()               
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {category_data.name} exists."
        )
    
    if category_data.num_category < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category number cannot be negative"
        )
    
    new_category = Category(**category_data.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category_data: CategoryBase, db: db_dependency): # type: ignore

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
 
    
    category_name = db.query(Category).filter(Category.name == category_data.name).first()
    if category_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {category_data.name} exists."
        )
    
    if category_data.num_category < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category number cannot be negative"
        )
    
    for key, value in category_data.dict().items():
        setattr(category, key, value)

    category.updated_at = datetime.now(TIMEZONE)
    db.commit()
    db.refresh(category)
    return category


# Get all specifications of a Category
@router.get("/values/{category_id}",  status_code=status.HTTP_200_OK)
async def get_category_specifications(category_id: int, db: db_dependency): 

    category_specifications = (
        db.query(Specification).filter(Specification.category_id == category_id).all()
    )

    data = [
        {
            "id": category_specification.id,
            "name": category_specification.name,
        }
        for category_specification in category_specifications
    ]

    return data
