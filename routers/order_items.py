from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Product, Order, OrderItem
from schemas import  ProductSpecificationResponse, OrderWithItems, OrderResponse, OrderCreate, OrderItemResponse, OrderItemCreate
import logging
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/order_items",
    tags=["order_items"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")

@router.get("", response_model=List[OrderItemResponse])
def get_order_items(db: Session = Depends(get_db)):
    db_orders = db.query(OrderItem).all()
    return db_orders

@router.get("/{order_id}", response_model=OrderItemResponse, status_code=status.HTTP_200_OK)
async def get_order_item(order_id: int, db: db_dependency): # type: ignore
    order_item = db.query(OrderItem).filter(OrderItem.order_id == order_id).first()
    if not order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    return order_item


@router.post("/add", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_item_data: OrderItemCreate, db: db_dependency): # type: ignore

    order_item_data_dict = order_item_data.dict()

    new_order_item = OrderItem(**order_item_data_dict)

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    return new_order_item


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: db_dependency):
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    if not order_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Items not found")

    for order_item in order_items:
        db.delete(order_item)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)