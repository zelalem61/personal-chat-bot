"""
Chat Routes - API Endpoints for Chat Functionality

LEARNING NOTES:
---------------
This module defines the chat-related API endpoints. It demonstrates:
- Pydantic models for request/response validation
- FastAPI routing and dependency injection
- Async endpoint handlers
- Streaming responses (Server-Sent Events)

KEY CONCEPTS:
-------------
1. PYDANTIC MODELS: Define the shape of requests and responses
   - Automatic validation
   - Clear API documentation
   - Type safety

2. DEPENDENCY INJECTION: Get the bot instance from app.state
   - Clean separation of concerns
   - Easy testing/mocking

3. STREAMING: Server-Sent Events for real-time responses
   - Better UX for long responses
   - Shows response as it generates

WHAT YOU'LL LEARN:
- Creating FastAPI routes
- Request/response models
- Async endpoint handlers
- SSE streaming responses
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)

# Create the router
router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    LEARNING NOTE: Pydantic models provide:
    1. Automatic validation - FastAPI returns 422 if invalid
    2. Type coercion - "123" becomes 123 for int fields
    3. Documentation - Shows up in Swagger UI
    4. IDE support - Autocomplete and type hints
    """

    message: str = Field(
        ...,  # Required field
        min_length=1,
        max_length=4000,
        description="The user's message to send to the bot",
        examples=["Tell me about your experience with Python"],
    )

    thread_id: Optional[str] = Field(
        default="default",
        description="Conversation thread ID for context (future feature)",
        examples=["user-123-session-456"],
    )


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    """

    response: str = Field(
        description="The bot's response to the user's message",
    )

    thread_id: str = Field(
        description="The conversation thread ID",
    )


class ErrorResponse(BaseModel):
    """
    Error response model.
    """

    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_bot(request: Request):
    """
    Get the bot instance from the application state.

    LEARNING NOTE: This is a simple dependency function. In more complex
    apps, you might use FastAPI's Depends() for more sophisticated
    dependency injection.
    """
    bot = getattr(request.app.state, "bot", None)
    if bot is None:
        raise HTTPException(
            status_code=503,
            detail="Bot not initialized. Server may still be starting up.",
        )
    return bot


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response", "model": ChatResponse},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error", "model": ErrorResponse},
        503: {"description": "Service unavailable", "model": ErrorResponse},
    },
    summary="Send a chat message",
    description="Send a message to the portfolio bot and receive a response.",
)
async def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - send a message and get a response.

    LEARNING NOTE: This is a standard request/response endpoint.
    The entire response is generated before being sent.

    For long responses, consider using the streaming endpoint instead.
    """
    bot = get_bot(request)

    logger.info(f"Chat request: {chat_request.message[:50]}...")

    try:
        response = await bot.chat(
            message=chat_request.message,
            thread_id=chat_request.thread_id,
        )

        logger.info(f"Chat response generated: {response[:50]}...")

        return ChatResponse(
            response=response,
            thread_id=chat_request.thread_id,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}",
        )


@router.post(
    "/chat/stream",
    response_class=StreamingResponse,
    summary="Send a chat message (streaming)",
    description="Send a message and receive a streaming response via Server-Sent Events.",
)
async def chat_stream(request: Request, chat_request: ChatRequest):
    """
    Streaming chat endpoint - receive response as it's generated.

    LEARNING NOTE: This endpoint uses Server-Sent Events (SSE) to
    stream the response. The client receives chunks as they're
    generated, providing better UX for long responses.

    Example client code (JavaScript):
    ```javascript
    const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: "Tell me about your projects"})
    });

    const reader = response.body.getReader();
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        console.log(new TextDecoder().decode(value));
    }
    ```
    """
    bot = get_bot(request)

    logger.info(f"Streaming chat request: {chat_request.message[:50]}...")

    async def generate():
        """
        Async generator that yields SSE-formatted chunks.

        LEARNING NOTE: The SSE format is:
            data: <content>\n\n

        The double newline marks the end of an event.
        """
        try:
            async for chunk in bot.stream_chat(
                message=chat_request.message,
                thread_id=chat_request.thread_id,
            ):
                # Format as Server-Sent Event
                yield f"data: {chunk}\n\n"

            # Send completion event
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get(
    "/health",
    summary="Chat service health check",
    description="Check if the chat service is ready to handle requests.",
)
async def chat_health(request: Request):
    """
    Health check for the chat service.

    Verifies that the bot is initialized and ready.
    """
    try:
        bot = get_bot(request)
        return {
            "status": "healthy",
            "bot_initialized": True,
        }
    except HTTPException:
        return {
            "status": "unhealthy",
            "bot_initialized": False,
        }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

"""
TESTING THE API
===============

1. Start the server:
   python -m portfolio_bot.api.main

2. Open Swagger UI:
   http://localhost:8004/docs

3. Test with curl:

   # Regular chat
   curl -X POST http://localhost:8004/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about your experience"}'

   # Streaming chat
   curl -X POST http://localhost:8004/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"message": "What are your skills?"}'

4. Test with Python:

   import httpx
   import asyncio

   async def test_chat():
       async with httpx.AsyncClient() as client:
           response = await client.post(
               "http://localhost:8004/api/chat",
               json={"message": "Hello!"}
           )
           print(response.json())

   asyncio.run(test_chat())
"""
