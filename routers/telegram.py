from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import sessionLocal
from schemas import TelegramMessage
import logging
import httpx
from typing import Annotated
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file for local development

router = APIRouter(
    prefix="/send-telegram-message",
    tags=["telegram"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")

@router.post("", status_code=status.HTTP_200_OK)
async def send_telegram_message(message_data: TelegramMessage, db: db_dependency):
    """
    Send order details to a Telegram group.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    logger.debug(f"Bot Token: {bot_token[:10]}... (obscured for security)")
    logger.debug(f"Chat ID: {chat_id}")

    if not bot_token or not chat_id:
        logger.error("Telegram bot token or chat ID not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Telegram configuration missing"
        )

    # telegram_items = "\n".join(
    #     [f"- {item['name']} (Qty: {item['qty']}, Price: {item['discount']} AZN)" for item in message_data.items]
    # )

    payment_method = (
        f"Kredit ({message_data.month} aylıq)"
        if message_data.payment_method == "kredit"
        else "Bank kartı ilə ödəniş"
    )
    telegram_message = (
        f"📦 *Yeni Sifariş!* 📦\n"
        f"*Sifariş ID*: {message_data.order_id}\n"
        f"*Alıcı*: {message_data.name} {message_data.surname}\n"
        f"*Telefon*: {message_data.phone_number}\n"
        f"*Ödəniş üsulu*: {message_data.payment_method}\n"
        f"*Çatdırılma*: {message_data.delivery_method.title()}\n"
        f"*Total*: {message_data.total_price} AZN \n"
        # f"*Items*:\n{telegram_items}"
    )

    # Send message to Telegram
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": telegram_message,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(telegram_url, json=payload)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully for order {message_data.order_id}")
            return {"message": "Telegram message sent successfully"}
        except httpx.HTTPStatusError as e:
            logger.error(f"Telegram API error: {e.response.status_code} - {e.response.text}")
            if "chat not found" in e.response.text.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telegram chat not found. Verify chat_id and bot permissions."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send Telegram message: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Telegram request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to Telegram API"
            )