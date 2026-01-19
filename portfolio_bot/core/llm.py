"""
LLM Manager - Centralized LLM Access

LEARNING NOTES:
---------------
This module provides a centralized way to access LLM instances. In production
systems, you might have multiple LLM providers with fallback logic. For this
learning project, we keep it simple with just OpenAI.

The LLMManager class uses the Singleton pattern (like AppConfig) to ensure
only one set of LLM instances exists, avoiding unnecessary resource usage.

KEY CONCEPTS:
-------------
1. LangChain's ChatOpenAI: A wrapper around OpenAI's chat completion API
2. Temperature: Controls randomness (0 = deterministic, 1 = creative)
3. Caching: LLM instances are created once and reused

WHAT YOU'LL LEARN:
- LangChain's LLM abstractions
- Configuring LLM parameters
- Singleton pattern for resource management
"""

from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """
    Centralized manager for LLM instances.

    Provides access to:
    - Chat model (for generating responses)
    - Embeddings model (for vector store)

    Usage:
        llm_manager = LLMManager()
        llm = llm_manager.get_chat_model()
        response = llm.invoke("Hello!")

    LEARNING NOTE: This class creates LLM instances lazily (on first use)
    and caches them. This is more efficient than creating new instances
    for every request.
    """

    _instance = None

    def __new__(cls) -> "LLMManager":
        """Singleton implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the LLM manager."""
        if self._initialized:
            return

        self._config = get_config()
        self._chat_model: Optional[ChatOpenAI] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._initialized = True

        logger.info(f"LLMManager initialized with model: {self._config.openai_model}")

    def get_chat_model(self, temperature: float = 0.7) -> ChatOpenAI:
        """
        Get a ChatOpenAI instance.

        Args:
            temperature: Controls randomness in responses.
                        0.0 = deterministic (good for classification)
                        0.7 = balanced (good for conversation)
                        1.0 = creative (good for brainstorming)

        Returns:
            ChatOpenAI: Configured LLM instance.

        LEARNING NOTE: The ChatOpenAI class is LangChain's wrapper around
        OpenAI's chat completion API. It provides:
        - Consistent interface across LLM providers
        - Automatic retry logic
        - Streaming support
        - Tool/function calling support
        """
        # Create new instance if temperature differs or not yet created
        # In production, you might cache instances by temperature
        if self._chat_model is None or self._chat_model.temperature != temperature:
            self._chat_model = ChatOpenAI(
                model=self._config.openai_model,
                temperature=temperature,
                api_key=self._config.openai_api_key,
                # Additional useful parameters:
                # max_tokens=1000,  # Limit response length
                # timeout=30,       # Request timeout in seconds
            )
            logger.debug(f"Created ChatOpenAI with temperature={temperature}")

        return self._chat_model

    def get_embeddings(self) -> OpenAIEmbeddings:
        """
        Get an OpenAI embeddings instance.

        Returns:
            OpenAIEmbeddings: Configured embeddings model.

        LEARNING NOTE: Embeddings convert text into numerical vectors.
        These vectors capture semantic meaning, allowing us to find
        similar documents using vector similarity (cosine similarity).

        Example:
            "What is Python?" → [0.1, 0.3, -0.2, ...] (1536 dimensions)
            "Tell me about Python" → [0.12, 0.28, -0.19, ...] (similar vector!)
        """
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=self._config.openai_embedding_model,
                api_key=self._config.openai_api_key,
            )
            logger.debug(f"Created OpenAIEmbeddings with model={self._config.openai_embedding_model}")

        return self._embeddings


# Convenience function for quick access
@lru_cache(maxsize=1)
def get_llm_manager() -> LLMManager:
    """
    Get the singleton LLMManager instance.

    Usage:
        from portfolio_bot.core.llm import get_llm_manager
        llm = get_llm_manager().get_chat_model()
    """
    return LLMManager()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Quick test of the LLM manager.

    Run this file directly:
        python -m portfolio_bot.core.llm

    Make sure OPENAI_API_KEY is set in your .env file!
    """
    import asyncio

    async def test_llm():
        # Get the LLM manager
        llm_manager = get_llm_manager()

        # Get a chat model
        llm = llm_manager.get_chat_model(temperature=0.7)

        print("Testing ChatOpenAI...")
        print(f"Model: {llm.model_name}")
        print(f"Temperature: {llm.temperature}")

        # Make a simple call
        response = await llm.ainvoke("Say 'Hello, I am working!' in exactly those words.")
        print(f"Response: {response.content}")

        # Test embeddings
        print("\nTesting OpenAIEmbeddings...")
        embeddings = llm_manager.get_embeddings()

        # Get embedding for a sample text
        vector = await embeddings.aembed_query("Hello, world!")
        print(f"Embedding dimensions: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")

    asyncio.run(test_llm())
