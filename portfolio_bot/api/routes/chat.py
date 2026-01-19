"""
Chat Routes - API Endpoints

LEARNING NOTES:
---------------
Defines the chat API endpoints with Pydantic validation.

YOUR TASK: (See roadmap.md Step 8)
----------
This file is mostly complete. Works once PortfolioBot is implemented.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    thread_id: Optional[str] = Field(default="default")


class ChatResponse(BaseModel):
    response: str
    thread_id: str


def get_bot(request: Request):
    bot = getattr(request.app.state, "bot", None)
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    return bot


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """Send a message and get a response."""
    bot = get_bot(request)
    response = await bot.chat(message=chat_request.message, thread_id=chat_request.thread_id)
    return ChatResponse(response=response, thread_id=chat_request.thread_id)


@router.get("/health")
async def chat_health(request: Request):
    try:
        get_bot(request)
        return {"status": "healthy", "bot_initialized": True}
    except HTTPException:
        return {"status": "unhealthy", "bot_initialized": False}
