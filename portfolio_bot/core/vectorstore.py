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

from typing import Any, Dict, List, Optional
from uuid import uuid4

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.core.llm import get_llm_manager
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# VectorStore Class
# =============================================================================


class VectorStore:
    """
    Thin wrapper around a ChromaDB collection for RAG.

    Responsibilities:
    - Connect to ChromaDB and get/create a collection
    - Embed and store documents
    - Perform similarity search over stored documents
    """

    def __init__(self):
        self._config = get_config()
        self._client: Optional[chromadb.HttpClient] = None
        self._collection = None
        self._embeddings = None

    async def initialize(self):
        """
        Initialize the ChromaDB client, collection, and embeddings model.
        """
        if (
            self._client is not None
            and self._collection is not None
            and self._embeddings is not None
        ):
            # Already initialized
            return

        logger.info(
            "Connecting to ChromaDB at %s:%s",
            self._config.chroma_host,
            self._config.chroma_port,
        )

        # Connect to ChromaDB HTTP server
        self._client = chromadb.HttpClient(
            host=self._config.chroma_host,
            port=self._config.chroma_port,
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create the collection
        self._collection = self._client.get_or_create_collection(
            name=self._config.chroma_collection_name
        )

        # Get embeddings model from LLM manager
        llm_manager = get_llm_manager()
        self._embeddings = llm_manager.get_embeddings()

        logger.info(
            "VectorStore initialized with collection '%s'",
            self._config.chroma_collection_name,
        )

    async def add_documents(
        self, documents: List[Dict[str, Any]], chunk: bool = True
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of dicts with at least a 'content' field and
                optionally 'id' and 'metadata'.
            chunk: Whether to chunk documents before embedding.

        Returns:
            int: Number of chunks actually stored.
        """
        if not documents:
            return 0

        # Ensure initialized
        await self.initialize()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._config.chunk_size,
            chunk_overlap=self._config.chunk_overlap,
        )

        all_ids: List[str] = []
        all_texts: List[str] = []
        all_metadatas: List[Dict[str, Any]] = []

        for doc in documents:
            base_id = str(doc.get("id") or uuid4())
            content: str = doc.get("content", "")
            metadata: Dict[str, Any] = doc.get("metadata", {}) or {}

            if not content:
                continue

            if chunk:
                chunks = text_splitter.split_text(content)
                for idx, chunk_text in enumerate(chunks):
                    chunk_id = f"{base_id}_{idx}"
                    all_ids.append(chunk_id)
                    all_texts.append(chunk_text)
                    # Store original metadata plus chunk index
                    all_metadatas.append({**metadata, "chunk": idx})
            else:
                all_ids.append(base_id)
                all_texts.append(content)
                all_metadatas.append(metadata)

        if not all_texts:
            return 0

        # 3. Generate embeddings
        logger.info(
            "Embedding %d text chunks for storage in ChromaDB", len(all_texts)
        )
        embeddings = await self._embeddings.aembed_documents(all_texts)

        # 4. Add to collection
        self._collection.add(
            ids=all_ids,
            documents=all_texts,
            metadatas=all_metadatas,
            embeddings=embeddings,
        )

        logger.info(
            "Stored %d chunks in ChromaDB collection '%s'",
            len(all_texts),
            self._config.chroma_collection_name,
        )
        return len(all_texts)

    async def clear(self) -> None:
        """
        Remove all documents from the underlying ChromaDB collection.

        LEARNING NOTE: This is useful during development when you want
        to re-ingest your portfolio from scratch.
        """
        await self.initialize()

        logger.info(
            "Clearing all documents from ChromaDB collection '%s'",
            self._config.chroma_collection_name,
        )

        # Simplest approach: delete and recreate the collection
        self._client.delete_collection(name=self._config.chroma_collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._config.chroma_collection_name
        )

        logger.info(
            "Collection '%s' cleared",
            self._config.chroma_collection_name,
        )

    async def similarity_search(
        self, query: str, k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a similarity search over the stored documents.

        Args:
            query: User query string.
            k: Number of results to return. If None, uses config.num_docs_to_retrieve.

        Returns:
            List of dicts with keys: id, content, metadata, distance.
        """
        if not query:
            return []

        # Ensure initialized
        await self.initialize()

        if k is None:
            k = self._config.num_docs_to_retrieve

        # 1. Generate query embedding
        query_embedding = await self._embeddings.aembed_query(query)

        # 2. Search in ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["distances", "metadatas", "documents"],
        )

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        logger.info(
            "Similarity search returned %d results for query '%s'",
            len(docs),
            query[:50],
        )

        formatted: List[Dict[str, Any]] = []
        for doc_id, text, meta, dist in zip(ids, docs, metadatas, distances):
            formatted.append(
                {
                    "id": doc_id,
                    "content": text,
                    "metadata": meta or {},
                    "distance": dist,
                }
            )

        return formatted

    async def get_document_count(self) -> int:
        """
        Get the total number of documents (vectors) stored in the collection.
        """
        await self.initialize()
        return self._collection.count()


# =============================================================================
# get_vector_store() singleton function
# =============================================================================

_vector_store: Optional[VectorStore] = None


async def get_vector_store() -> VectorStore:
    """
    Get a singleton instance of VectorStore, initializing it on first use.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        await _vector_store.initialize()
    return _vector_store

