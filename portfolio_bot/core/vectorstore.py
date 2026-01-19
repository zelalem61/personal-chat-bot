"""
Vector Store - ChromaDB Integration for RAG

LEARNING NOTES:
---------------
RAG (Retrieval-Augmented Generation) improves LLM responses by:
1. Converting documents into embeddings (numerical vectors)
2. Storing vectors in ChromaDB
3. Finding similar documents when user asks a question
4. Passing documents to LLM as context

KEY CONCEPTS:
-------------
1. EMBEDDINGS: Text → numbers that capture meaning
2. CHUNKING: Breaking documents into smaller pieces (RecursiveCharacterTextSplitter)
3. SIMILARITY SEARCH: Find k nearest vectors to query

YOUR TASK: (See roadmap.md Step 4)
----------
1. Implement VectorStore class connecting to ChromaDB
2. Add initialize() to connect and get/create collection
3. Add add_documents() to chunk, embed, and store documents
4. Add similarity_search() to find relevant documents
5. Create get_vector_store() singleton function
"""

from typing import Optional

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.core.llm import get_llm_manager
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement VectorStore Class
# =============================================================================
# class VectorStore:
#     def __init__(self):
#         self._config = get_config()
#         self._client = None
#         self._collection = None
#         self._embeddings = None
#
#     async def initialize(self):
#         # Connect: chromadb.HttpClient(host=..., port=...)
#         # Get collection: self._client.get_or_create_collection(name=...)
#         # Get embeddings: self._llm_manager.get_embeddings()
#         pass
#
#     async def add_documents(self, documents: list[dict], chunk: bool = True) -> int:
#         # 1. Loop through documents
#         # 2. If chunk: use RecursiveCharacterTextSplitter to split content
#         # 3. Generate embeddings: await self._embeddings.aembed_documents(chunks)
#         # 4. Add to collection: self._collection.add(ids=..., documents=..., embeddings=...)
#         pass
#
#     async def similarity_search(self, query: str, k: Optional[int] = None) -> list[dict]:
#         # 1. Generate query embedding: await self._embeddings.aembed_query(query)
#         # 2. Search: self._collection.query(query_embeddings=[...], n_results=k)
#         # 3. Format and return results
#         pass
pass


# =============================================================================
# TODO: Implement get_vector_store() singleton function
# =============================================================================
# _vector_store = None
#
# async def get_vector_store() -> VectorStore:
#     global _vector_store
#     if _vector_store is None:
#         _vector_store = VectorStore()
#         await _vector_store.initialize()
#     return _vector_store
pass
