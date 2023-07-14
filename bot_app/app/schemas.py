from typing import Dict, Optional

from pydantic import BaseModel, Field, root_validator


class Chat(BaseModel):
    id: int


class From(BaseModel):
    id: int


class Voice(BaseModel):
    duration: int
    file_id: str
    file_size: int
    file_unique_id: str
    mime_type: str


class Message(BaseModel):
    chat: Chat
    from_: From = Field(..., alias="from")
    text: Optional[str]
    voice: Optional[Voice]

    @root_validator(pre=True)
    def check_text_or_audio(cls, values):
        text, audio = values.get("text"), values.get("voice")
        if text is None and audio is None:
            raise ValueError("Either text or voice must be provided")
        return values


class AiChatMessage(BaseModel):
    role: str
    content: str

    def __str__(self):
        return f"{self.role}: {self.content}"
