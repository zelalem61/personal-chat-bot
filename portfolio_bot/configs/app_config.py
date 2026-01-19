"""
Application Configuration - Environment Variable Loader

LEARNING NOTES:
---------------
This module implements the Singleton pattern to ensure only one configuration
instance exists throughout the application. This is important because:

1. Configuration should be loaded once at startup
2. All modules should share the same configuration
3. Environment variables are read from .env file using python-dotenv

The pattern used here is thread-safe and lazy-loaded.

WHAT YOU'LL LEARN:
- Singleton pattern implementation in Python
- Environment variable management with python-dotenv
- Type hints and default values for configuration
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
# This should be called early in the application lifecycle
load_dotenv()


class AppConfig:
    """
    Singleton configuration class that loads settings from environment variables.

    Usage:
        config = AppConfig()
        api_key = config.openai_api_key

    All settings have sensible defaults for local development.
    """

    _instance = None

    def __new__(cls) -> "AppConfig":
        """
        Singleton implementation - returns existing instance or creates new one.

        LEARNING NOTE: __new__ is called before __init__. By overriding it,
        we ensure only one instance of AppConfig ever exists.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize configuration from environment variables.

        Only runs once due to the _initialized flag check.
        """
        if self._initialized:
            return

        # OpenAI Configuration
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

        # ChromaDB Configuration
        self.chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
        self.chroma_collection_name: str = os.getenv("CHROMA_COLLECTION", "portfolio_docs")

        # API Configuration
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8004"))

        # RAG Configuration
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.num_docs_to_retrieve: int = int(os.getenv("NUM_DOCS_TO_RETRIEVE", "5"))

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        self._initialized = True

    def validate(self) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            bool: True if configuration is valid, raises ValueError otherwise.

        LEARNING NOTE: It's good practice to validate configuration at startup
        rather than failing later when the missing value is needed.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        return True

    def __repr__(self) -> str:
        """String representation for debugging (hides sensitive values)."""
        return (
            f"AppConfig("
            f"openai_model={self.openai_model}, "
            f"chroma_host={self.chroma_host}:{self.chroma_port}, "
            f"collection={self.chroma_collection_name})"
        )


# Alternative: Function-based singleton using lru_cache
# This is another common pattern you might see in Python codebases
@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """
    Get the singleton AppConfig instance.

    LEARNING NOTE: Using @lru_cache with maxsize=1 is another way to
    implement a singleton. The first call creates the instance,
    subsequent calls return the cached instance.

    Usage:
        from portfolio_bot.configs.app_config import get_config
        config = get_config()
    """
    return AppConfig()
