"""AOCC Copilot HTTP API.

Repo kökünden çalıştırın: uvicorn backend.main:app --reload
"""

import json
import logging
from collections.abc import AsyncIterator

import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from backend.llm import MODEL, async_client
from backend.prompts import SYSTEM_INSTRUCTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TOKENS = 16000

# İstemciye yalnızca bu genel mesaj gider; hatanın ayrıntısı sunucu loguna yazılır.
ERROR_MESSAGE = "Yanıt üretilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin."

app = FastAPI(title="AOCC Copilot")


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Mesaj boş olamaz.")
        return value


def sse_event(event: str, data: dict) -> str:
    # ensure_ascii=False: Türkçe karakterler ş gibi kaçış dizilerine dönüşmeden,
    # UTF-8 olarak gönderilir.
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_reply(message: str) -> AsyncIterator[str]:
    """Model yanıtını SSE olayları olarak üretir: delta*, ardından done ya da error."""
    try:
        async with async_client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_INSTRUCTIONS,
            messages=[{"role": "user", "content": message}],
        ) as stream:
            async for text in stream.text_stream:
                yield sse_event("delta", {"text": text})
            final = await stream.get_final_message()
    except anthropic.APIError:
        logger.exception("Claude çağrısı başarısız oldu")
        yield sse_event("error", {"message": ERROR_MESSAGE})
        return

    yield sse_event("done", {"stop_reason": final.stop_reason})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    # text/event-stream için Starlette charset=utf-8'i başlığa kendisi ekler.
    return StreamingResponse(
        stream_reply(request.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
