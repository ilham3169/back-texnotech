from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response  # type: ignore
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text  # type: ignore
from database import sessionLocal
from models import Product, Order, OrderItem
from schemas import OrderWithItems, OrderResponse, OrderCreate, OrderPaymentUpdate, OrderStatusUpdate
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
async def get_order(order_id: int, db: db_dependency):  # type: ignore
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.post("/add", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: db_dependency):  # type: ignore
    order_data_dict = order_data.dict()
    order_data_dict['user_id'] = 1  # Hardcoded user_id, replace with actual logic if needed

    new_order = Order(**order_data_dict)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: db_dependency):

    order = db.query(Order).filter(Order.id == order_id).first()
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    db.delete(order_items)
    db.delete(order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{order_id}/status", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def update_order_status(order_id: int, update_data: OrderStatusUpdate, db: db_dependency):
    """
    Update the status of an existing order.
    Expects a JSON payload with 'status' field, e.g., {"status": "shipped"}
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Validate status
    valid_statuses = ["pending", "processing", "shipped", "delivered", "canceled"]
    if update_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {valid_statuses}"
        )

    # Update the order's status
    order.status = update_data.status
    order.updated_at = datetime.now(TIMEZONE)  # Update timestamp
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/payment", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def update_order_payment(order_id: int, update_data: OrderPaymentUpdate, db: db_dependency):
    """
    Update the status of an existing order.
    Expects a JSON payload with 'status' field, e.g., {"status": "shipped"}
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


    # Update the order's status
    order.payment_status = update_data.payment_status
    order.updated_at = datetime.now(TIMEZONE)  # Update timestamp
    db.commit()
    db.refresh(order)
    return order
