"""
Chat Service - Business Logic Layer

LEARNING NOTES:
---------------
The service layer sits between the API routes and the core bot logic.
It provides:
- A clean interface for the API layer
- Business logic that doesn't belong in routes or core
- Validation and error handling
- Caching and optimization

In this simple example, the service is a thin wrapper. In production,
you might add:
- Rate limiting
- Usage tracking
- Conversation history management
- User authentication

KEY CONCEPTS:
-------------
1. SEPARATION OF CONCERNS: Routes handle HTTP, services handle logic
2. TESTABILITY: Services are easier to unit test than routes
3. REUSABILITY: Services can be used by multiple interfaces (API, CLI, etc.)

WHAT YOU'LL LEARN:
- Service layer pattern
- Wrapping core functionality
- Adding business logic to bot interactions
"""

from typing import AsyncGenerator, Optional

from portfolio_bot.core.graph import PortfolioBot
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """
    Service layer for chat functionality.

    Wraps the PortfolioBot and adds business logic like:
    - Message validation
    - Error handling
    - Logging and metrics

    Usage:
        service = ChatService()
        await service.initialize()
        response = await service.send_message("Hello!")

    LEARNING NOTE: In production, this service might also handle:
    - Conversation history storage (database)
    - User context management
    - Rate limiting per user
    - Usage metrics and billing
    """

    def __init__(self):
        """Initialize the chat service."""
        self._bot: Optional[PortfolioBot] = None
        self._initialized = False
        logger.info("ChatService created")

    async def initialize(self) -> None:
        """
        Initialize the service and underlying bot.
        """
        if self._initialized:
            return

        logger.info("Initializing ChatService...")

        self._bot = PortfolioBot()
        await self._bot.initialize()

        self._initialized = True
        logger.info("ChatService initialized")

    async def send_message(
        self,
        message: str,
        thread_id: str = "default",
        user_id: Optional[str] = None,
    ) -> str:
        """
        Send a message and get a response.

        Args:
            message: The user's message.
            thread_id: Conversation thread ID.
            user_id: Optional user ID for tracking (future feature).

        Returns:
            The bot's response.

        Raises:
            RuntimeError: If service not initialized.
            ValueError: If message is empty or too long.
        """
        if not self._initialized:
            raise RuntimeError("ChatService not initialized")

        # Validate message
        self._validate_message(message)

        # Log the interaction (could send to analytics)
        logger.info(f"Message from user={user_id or 'anonymous'}, thread={thread_id}")

        # Get response from bot
        response = await self._bot.chat(
            message=message,
            thread_id=thread_id,
        )

        return response

    async def stream_message(
        self,
        message: str,
        thread_id: str = "default",
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response token by token.

        Args:
            message: The user's message.
            thread_id: Conversation thread ID.
            user_id: Optional user ID for tracking.

        Yields:
            Response chunks as they're generated.
        """
        if not self._initialized:
            raise RuntimeError("ChatService not initialized")

        self._validate_message(message)

        logger.info(f"Streaming message from user={user_id or 'anonymous'}, thread={thread_id}")

        async for chunk in self._bot.stream_chat(
            message=message,
            thread_id=thread_id,
        ):
            yield chunk

    def _validate_message(self, message: str) -> None:
        """
        Validate the message before processing.

        Args:
            message: The message to validate.

        Raises:
            ValueError: If message is invalid.
        """
        if not message:
            raise ValueError("Message cannot be empty")

        if len(message) > 4000:
            raise ValueError("Message too long (max 4000 characters)")

        # Add more validation as needed:
        # - Check for spam patterns
        # - Filter inappropriate content
        # - Check rate limits
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized


# Singleton instance for easy access
_chat_service: Optional[ChatService] = None


async def get_chat_service() -> ChatService:
    """
    Get the singleton ChatService instance.

    Creates and initializes the service on first call.
    """
    global _chat_service

    if _chat_service is None:
        _chat_service = ChatService()
        await _chat_service.initialize()

    return _chat_service


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the chat service.

    Run: python -m portfolio_bot.services.chat_service
    """
    import asyncio

    async def test_service():
        print("=== Testing ChatService ===\n")

        # Get the service
        service = await get_chat_service()

        # Test regular message
        print("Testing regular message...")
        response = await service.send_message(
            message="What are your skills?",
            thread_id="test-thread",
            user_id="test-user",
        )
        print(f"Response: {response}\n")

        # Test streaming
        print("Testing streaming...")
        print("Response: ", end="", flush=True)
        async for chunk in service.stream_message(
            message="Tell me about your experience",
            thread_id="test-thread",
        ):
            print(chunk, end="", flush=True)
        print("\n")

        # Test validation
        print("Testing validation...")
        try:
            await service.send_message("")
        except ValueError as e:
            print(f"Empty message rejected: {e}")

        try:
            await service.send_message("x" * 5000)
        except ValueError as e:
            print(f"Long message rejected: {e}")

    asyncio.run(test_service())
