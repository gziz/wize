import os

import aioredis
import httpx
from dotenv import load_dotenv
import json
from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError
from typing import List
load_dotenv()

from . import schemas
from .ai.agent import Agent
from .audio import get_voice_text
from .text import send_message
from .utils import logger

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.agent = Agent()


@app.post("/chat")
async def receive_data(request: Request):
    try:
        # data = await request.json()
        body = await request.body()
        print(type(body))
        data = json.loads(body)

        print("\n")
        print(type(data))
        print("\n")

        history = format_messages(data)
        ai_msg = handle_chat(history[-1], history[:-1])

        return ai_msg

    except ValidationError as e:
        logger.error(e.errors())
        return {"status": "error"}

@app.get("/tokens")
def get_spent_tokens():
    return app.state.agent.total_tokens


async def validate_data(data) -> schemas.Message:
    try:
        msg = schemas.Message(**data["message"])
        return msg
    except ValidationError as e:
        logger.error(e.errors())
        raise HTTPException(status_code=400, detail="Invalid data.")


def handle_chat(user_msg: schemas.Message, chat_history: List) -> schemas.AiChatMessage:
    """Retrieve chat history, generate reply, update history and reply to user."""

    user_msg, ai_msg, ai_msg_telegram = app.state.agent(user_msg, chat_history)

    return ai_msg_telegram


def format_messages(data):

    formatted_messages = []
    for msg in data:
        is_ai = msg["from_user"]["profile"]["admin"] or msg["from_user"]["profile"]["AI"]
        sender = "assistant" if is_ai else "user"
        msg_text = msg["message"]
        
        formatted_messages.append(f"{sender}: {msg_text}")
    
    return formatted_messages