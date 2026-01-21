"""
Retriever Agent - Document Retrieval for RAG

LEARNING NOTES:
---------------
The retriever finds relevant documents from the vector store:
1. Extract the user's query from state
2. Search the vector store for similar documents
3. Add documents to state for the response agent

KEY CONCEPTS:
-------------
1. SEMANTIC SEARCH: Finding documents by meaning, not keywords
2. STATE UPDATE: Adding retrieved documents to state
3. ASYNC OPERATIONS: Non-blocking database queries

YOUR TASK: (See roadmap.md Step 5)
----------
1. Implement Retriever class with lazy vector store initialization
2. Implement run(state) method that searches for documents
3. Return state update with documents list
"""

from typing import Optional

from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState
from portfolio_bot.core.vectorstore import get_vector_store
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Retriever Class
# =============================================================================


class Retriever:
    """
    RAG retriever that queries the vector store for relevant documents.

    The retriever:
    - Lazily initializes the shared vector store
    - Extracts the latest user query from the conversation state
    - Performs semantic search and returns matching documents
    """

    def __init__(self, num_docs: Optional[int] = None):
        # If num_docs is not provided here, the VectorStore or config
        # can decide a sensible default.
        self._num_docs = num_docs
        self._vector_store = None  # Lazy init

    async def run(self, state: NodeState) -> dict:
        """
        Retrieve documents relevant to the latest user query.

        Args:
            state: The current graph state, including conversation messages.

        Returns:
            dict: Partial state update containing a "documents" list.
        """
        # 1. Get vector store (lazy initialization)
        if self._vector_store is None:
            logger.info("Initializing vector store in Retriever")
            self._vector_store = await get_vector_store()

        # 2. Extract query from last HumanMessage in state["messages"]
        messages = state.get("messages", [])
        query = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if not query:
            logger.warning(
                "Retriever.run called with no HumanMessage in state; returning empty documents."
            )
            return {"documents": []}

        # 3. Search vector store
        documents = await self._vector_store.similarity_search(query, k=self._num_docs)
        logger.info(
            "Retriever found %d documents for query: %s",
            len(documents),
            query[:50],
        )

        # 4. Return state update
        return {"documents": documents}

