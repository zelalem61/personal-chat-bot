"""
LLM Manager - Centralized LLM Access

LEARNING NOTES:
---------------
This module provides a centralized way to access LLM instances.
The LLMManager class uses the Singleton pattern to ensure only one
set of LLM instances exists, avoiding unnecessary resource usage.

KEY CONCEPTS:
-------------
1. LangChain's ChatOpenAI: A wrapper around OpenAI's chat completion API
2. OpenAIEmbeddings: Converts text to vectors for similarity search
3. Temperature: Controls randomness (0 = deterministic, 1 = creative)
4. Singleton Pattern: Ensures only one instance exists

YOUR TASK: (See roadmap.md Step 2)
----------
1. Implement LLMManager as a singleton class
2. Add get_chat_model(temperature) method returning ChatOpenAI
3. Add get_embeddings() method returning OpenAIEmbeddings
4. Create get_llm_manager() helper function with @lru_cache
"""

from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement LLMManager Class
class LLMManager:
    """
    Singleton manager that provides access to shared LLM resources.

    Responsibilities:
    - Lazily create and cache a `ChatOpenAI` instance
    - Lazily create and cache an `OpenAIEmbeddings` instance
    - Reuse these instances across the application to avoid unnecessary
      network handshakes and resource usage.
    """

    _instance: Optional["LLMManager"] = None

    def __new__(cls) -> "LLMManager":
        """
        Singleton implementation - returns existing instance or creates new one.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize manager with configuration.

        LEARNING NOTE: The `_initialized` flag ensures this block only
        runs once even though `__init__` may be called multiple times
        on the singleton instance.
        """
        if getattr(self, "_initialized", False):
            return

        self._config = get_config()
        self._chat_model: Optional[ChatOpenAI] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None

        self._initialized = True

    def get_chat_model(self, temperature: float = 0.7) -> ChatOpenAI:
        """
        Get (or lazily create) a ChatOpenAI model instance.

        Args:
            temperature: Controls randomness in generation.

        Returns:
            ChatOpenAI: Configured chat model instance.
        """
        # If no model exists yet, or the temperature differs, create a new one.
        if self._chat_model is None or getattr(self._chat_model, "temperature", None) != temperature:
            logger.info("Initializing ChatOpenAI model with temperature=%s", temperature)
            self._chat_model = ChatOpenAI(
                model=self._config.openai_model,
                temperature=temperature,
                api_key=self._config.openai_api_key,
            )
        return self._chat_model

    def get_embeddings(self) -> OpenAIEmbeddings:
        """
        Get (or lazily create) an OpenAIEmbeddings instance.

        Returns:
            OpenAIEmbeddings: Configured embeddings model instance.
        """
        if self._embeddings is None:
            logger.info("Initializing OpenAIEmbeddings model")
            self._embeddings = OpenAIEmbeddings(
                model=self._config.openai_embedding_model,
                api_key=self._config.openai_api_key,
            )
        return self._embeddings


# =============================================================================
# TODO: Implement get_llm_manager() function
# =============================================================================
@lru_cache(maxsize=1)
def get_llm_manager() -> LLMManager:
    """
    Get the singleton LLMManager instance.

    LEARNING NOTE: This uses the same pattern as `get_config` to provide a
    simple, function-based way to access the shared manager.
    """
    return LLMManager()

