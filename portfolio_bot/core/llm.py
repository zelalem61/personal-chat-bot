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
# =============================================================================
# Requirements:
# - Singleton pattern using __new__ (see app_config.py for example)
# - __init__ should load config and set _chat_model, _embeddings to None
# - get_chat_model(temperature: float = 0.7) -> ChatOpenAI
# - get_embeddings() -> OpenAIEmbeddings
#
# Hint for ChatOpenAI:
#   ChatOpenAI(model=config.openai_model, temperature=temperature, api_key=config.openai_api_key)
#
# Hint for OpenAIEmbeddings:
#   OpenAIEmbeddings(model=config.openai_embedding_model, api_key=config.openai_api_key)
pass


# =============================================================================
# TODO: Implement get_llm_manager() function
# =============================================================================
# Hint: @lru_cache(maxsize=1)
#       def get_llm_manager() -> LLMManager:
#           return LLMManager()
pass
