"""FastAPI application entrypoint and route registration."""

import asyncio
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chat import chat_service
from ingest import ingest_service
from instagram import router as instagram_router
from whatsapp import router as whatsapp_router


class ChatMessageRequest(BaseModel):
    """Incoming chat payload for web widget/API clients."""

    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    """Outgoing chat reply payload."""

    reply: str


app = FastAPI(title="Multi-Platform AI Support Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(whatsapp_router)
app.include_router(instagram_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Load environment variables when the application starts."""
    load_dotenv()


@app.get("/health")
async def health_check() -> dict:
    """Return a simple health status response."""
    try:
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Health check failed: {exc}") from exc


@app.post("/chat/message", response_model=ChatMessageResponse)
async def chat_message(payload: ChatMessageRequest) -> ChatMessageResponse:
    """Handle website/widget chat requests."""
    try:
        reply = await asyncio.to_thread(chat_service.get_reply, payload.user_id, payload.message, "web")
        return ChatMessageResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat request failed: {exc}") from exc


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)) -> dict:
    """Ingest a PDF or TXT document into the vector store."""
    temp_path = None
    try:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".txt"}:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

        data = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            temp_path = tmp.name

        text = ingest_service.load_document(temp_path)
        chunks = ingest_service.chunk_text(text)
        stored = ingest_service.embed_and_store(chunks)
        return {"status": "ok", "chunks_stored": stored}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc
    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()


def get_port() -> int:
    """Return server port from environment variable PORT or default to 8000."""
    return int(os.getenv("PORT", "8000"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=get_port(), reload=True)
