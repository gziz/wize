import io
import os

import httpx
import openai
import soundfile as sf
from aiofile import AIOFile

from . import schemas
from .utils import logger

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


async def get_voice_text(msg: schemas.Message):
    try:
        chat_id = msg.chat.id
        file_id = msg.voice.file_id
        downloaded = await download_file(chat_id, file_id)

        if downloaded:
            await process_file(chat_id)
            transcript = await whisper_voice(chat_id)
        return transcript
    except Exception as e:
        logger.error(f"Error in get_voice_text: {str(e)}")
        return None


async def download_file(chat_id: int, file_id: str):
    GET_FILE_PATH_URL = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(GET_FILE_PATH_URL)

    file_path = response.json()["result"]["file_path"]

    DOWNLOAD_FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(DOWNLOAD_FILE_URL)

    if response.status_code == 200:
        logger.info("Received audio")
        async with AIOFile(f"voice/{chat_id}.ogg", "wb") as file:
            await file.write(response.content)
        return True
    else:
        logger.error("Failed to download the audio file.")
        return None


async def process_file(chat_id):
    data, sr = sf.read(f"voice/{chat_id}.ogg")
    sf.write(f"voice/{chat_id}.wav", data, sr, "PCM_16")


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


async def whisper_voice(chat_id: int):
    try:
        async with AIOFile(f"voice/{chat_id}.wav", "rb") as audio_file:
            content = await audio_file.read()
            buffered_content = NamedBytesIO(content, f"voice/{chat_id}.wav")

        transcript = openai.Audio.transcribe("whisper-1", buffered_content)

        # Delete files after processing
        os.remove(f"voice/{chat_id}.ogg")
        os.remove(f"voice/{chat_id}.wav")

        return transcript["text"]

    except Exception as e:
        logger.error(f"Error in whisper_voice: {str(e)}")
        return None
