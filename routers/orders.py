from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Product, Order
from schemas import  ProductSpecificationResponse, OrderWithItems, OrderResponse, OrderCreate
import logging
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")

@router.get("", response_model=List[OrderWithItems])
def get_orders(db: Session = Depends(get_db)):
    db_orders = db.query(Order).all()
    return db_orders

@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order(order_id: int, db: db_dependency): # type: ignore
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/add", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: db_dependency): # type: ignore

    order_data_dict = order_data.dict()
    order_data_dict['user_id'] = 1

    new_order = Order(**order_data_dict)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: db_dependency):

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db.delete(order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

