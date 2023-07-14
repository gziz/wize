import os

import httpx

from . import schemas
from .utils import logger

TOKEN = os.environ.get("TELEGRAM_TOKEN")
SEND_MSG_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


async def send_message(chat_id: int, ai_msg: str) -> None:
    data = {"chat_id": chat_id, "text": ai_msg}

    async with httpx.AsyncClient() as client:
        response = await client.post(SEND_MSG_URL, data=data)

    if response.status_code == 200:
        logger.info(f"Message sent to chat ID '{chat_id}'")
    else:
        logger.info(f"Error sending message to chat ID '{chat_id}'")
