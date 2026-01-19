"""
Vector Store - ChromaDB Integration for RAG

LEARNING NOTES:
---------------
This module implements RAG (Retrieval-Augmented Generation) using ChromaDB
as the vector store. RAG is a technique that improves LLM responses by:

1. Converting documents into embeddings (numerical vectors)
2. Storing these vectors in a database (ChromaDB)
3. When a user asks a question, finding similar documents
4. Passing those documents to the LLM as context

KEY CONCEPTS:
-------------
1. EMBEDDINGS: Convert text → numbers that capture meaning
   "I love Python" → [0.1, 0.3, -0.2, 0.5, ...]
   Similar texts have similar vectors (close in vector space)

2. VECTOR STORE: Database optimized for similarity search
   - Stores document text + embedding vectors
   - Supports fast similarity queries
   - ChromaDB: Open-source, easy to use, runs in Docker

3. CHUNKING: Breaking documents into smaller pieces
   - LLMs have context limits
   - Smaller chunks = more precise retrieval
   - Overlap ensures context isn't lost at boundaries

4. SIMILARITY SEARCH: Finding relevant documents
   - Query text → embedding
   - Find k nearest vectors in the database
   - Return those documents as context

WHAT YOU'LL LEARN:
- ChromaDB client setup and operations
- Document chunking strategies
- Semantic similarity search
- Async operations for web applications
"""

from typing import Optional
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.core.llm import get_llm_manager
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Vector store implementation using ChromaDB.

    This class handles:
    - Connecting to ChromaDB (Docker container)
    - Adding documents with embeddings
    - Semantic similarity search

    Usage:
        vs = VectorStore()
        await vs.initialize()

        # Add documents
        await vs.add_documents([
            {"content": "Python is great", "metadata": {"source": "intro.md"}},
        ])

        # Search
        docs = await vs.similarity_search("Tell me about Python", k=3)

    LEARNING NOTE: ChromaDB runs as a separate service (Docker container).
    This is good practice because:
    1. Data persists between app restarts
    2. Can scale independently
    3. Multiple app instances can share the same store
    """

    def __init__(self):
        """Initialize the vector store (doesn't connect yet)."""
        self._config = get_config()
        self._llm_manager = get_llm_manager()
        self._client: Optional[chromadb.HttpClient] = None
        self._collection = None
        self._embeddings = None

    async def initialize(self) -> None:
        """
        Connect to ChromaDB and get/create the collection.

        Call this before using the vector store.

        LEARNING NOTE: We separate initialization from __init__ because:
        1. Network operations can fail - better to handle explicitly
        2. Async initialization doesn't work well in __init__
        3. Allows for lazy initialization
        """
        try:
            # Connect to ChromaDB running in Docker
            self._client = chromadb.HttpClient(
                host=self._config.chroma_host,
                port=self._config.chroma_port,
                settings=Settings(anonymized_telemetry=False),
            )

            # Get or create our collection
            # A collection is like a table in a traditional database
            self._collection = self._client.get_or_create_collection(
                name=self._config.chroma_collection_name,
                metadata={"description": "Portfolio documents for RAG"},
            )

            # Get embeddings model
            self._embeddings = self._llm_manager.get_embeddings()

            logger.info(
                f"Connected to ChromaDB at {self._config.chroma_host}:{self._config.chroma_port}, "
                f"collection: {self._config.chroma_collection_name}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise ConnectionError(
                f"Could not connect to ChromaDB at {self._config.chroma_host}:{self._config.chroma_port}. "
                "Make sure the ChromaDB container is running (docker-compose up -d)"
            ) from e

    async def add_documents(
        self,
        documents: list[dict],
        chunk: bool = True,
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of dicts with 'content' and optional 'metadata' keys.
            chunk: Whether to split documents into smaller chunks.

        Returns:
            Number of chunks/documents added.

        LEARNING NOTE: Chunking Strategy
        ---------------------------------
        We use RecursiveCharacterTextSplitter because:
        1. It tries to split on natural boundaries (paragraphs, sentences)
        2. Falls back to character-level if needed
        3. Maintains overlap to preserve context

        Chunk size of 1000 chars with 200 overlap is a good starting point.
        Tune based on your documents and retrieval quality.
        """
        if not self._collection:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")

        all_chunks = []
        all_metadatas = []
        all_ids = []

        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            if chunk:
                # Split into chunks
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                    separators=["\n\n", "\n", ". ", " ", ""],  # Try these in order
                )
                chunks = splitter.split_text(content)

                for j, chunk_text in enumerate(chunks):
                    all_chunks.append(chunk_text)
                    all_metadatas.append({**metadata, "chunk_index": j})
                    all_ids.append(f"doc_{i}_chunk_{j}")
            else:
                all_chunks.append(content)
                all_metadatas.append(metadata)
                all_ids.append(f"doc_{i}")

        if not all_chunks:
            logger.warning("No documents to add")
            return 0

        # Generate embeddings for all chunks
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        embeddings = await self._embeddings.aembed_documents(all_chunks)

        # Add to ChromaDB
        self._collection.add(
            ids=all_ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas,
        )

        logger.info(f"Added {len(all_chunks)} chunks to vector store")
        return len(all_chunks)

    async def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> list[dict]:
        """
        Find documents similar to the query.

        Args:
            query: The search query.
            k: Number of results to return (default from config).

        Returns:
            List of dicts with 'content', 'metadata', and 'score' keys.

        LEARNING NOTE: How Similarity Search Works
        -------------------------------------------
        1. Convert query text to embedding vector
        2. Find k vectors in the database closest to query vector
        3. "Closest" is measured by cosine similarity or L2 distance
        4. Return the documents associated with those vectors

        The 'score' indicates how similar the document is:
        - Lower distance = more similar (for L2 distance)
        - Results are sorted by similarity
        """
        if not self._collection:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")

        k = k or self._config.num_docs_to_retrieve

        # Generate embedding for query
        query_embedding = await self._embeddings.aembed_query(query)

        # Search in ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if results["distances"] else 0,
                })

        logger.debug(f"Found {len(documents)} documents for query: {query[:50]}...")
        return documents

    async def clear(self) -> None:
        """
        Clear all documents from the collection.

        Useful for re-indexing or testing.
        """
        if not self._client:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")

        # Delete and recreate collection
        self._client.delete_collection(self._config.chroma_collection_name)
        self._collection = self._client.create_collection(
            name=self._config.chroma_collection_name,
            metadata={"description": "Portfolio documents for RAG"},
        )
        logger.info("Cleared vector store collection")

    def get_document_count(self) -> int:
        """Get the number of documents in the collection."""
        if not self._collection:
            return 0
        return self._collection.count()


# Singleton instance
_vector_store: Optional[VectorStore] = None


async def get_vector_store() -> VectorStore:
    """
    Get the singleton VectorStore instance.

    This ensures all parts of the application share the same
    connection to ChromaDB.

    LEARNING NOTE: We use a function instead of just a global
    variable because we need async initialization. The function
    handles creating and initializing on first call.
    """
    global _vector_store

    if _vector_store is None:
        _vector_store = VectorStore()
        await _vector_store.initialize()

    return _vector_store


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the vector store.

    Make sure ChromaDB is running:
        docker-compose up -d

    Then run:
        python -m portfolio_bot.core.vectorstore
    """
    import asyncio

    async def test_vectorstore():
        print("=== Testing VectorStore ===\n")

        # Initialize
        vs = VectorStore()
        await vs.initialize()
        print(f"Document count: {vs.get_document_count()}")

        # Add some test documents
        test_docs = [
            {
                "content": "John is a software engineer with 5 years of experience in Python and machine learning. He has worked on various AI projects including chatbots and recommendation systems.",
                "metadata": {"source": "portfolio.md", "section": "experience"},
            },
            {
                "content": "Skills include Python, JavaScript, React, FastAPI, LangChain, and Docker. Proficient in machine learning frameworks like PyTorch and scikit-learn.",
                "metadata": {"source": "portfolio.md", "section": "skills"},
            },
            {
                "content": "Contact: john@example.com. Available for freelance projects and consulting. Based in San Francisco, CA.",
                "metadata": {"source": "portfolio.md", "section": "contact"},
            },
        ]

        # Clear and add fresh documents
        await vs.clear()
        count = await vs.add_documents(test_docs)
        print(f"Added {count} chunks")
        print(f"Total documents: {vs.get_document_count()}\n")

        # Test similarity search
        queries = [
            "What programming languages does John know?",
            "How can I contact John?",
            "What is John's experience with AI?",
        ]

        for query in queries:
            print(f"Query: {query}")
            results = await vs.similarity_search(query, k=2)
            for i, doc in enumerate(results):
                print(f"  Result {i+1} (score: {doc['score']:.3f}):")
                print(f"    {doc['content'][:100]}...")
            print()

    asyncio.run(test_vectorstore())
