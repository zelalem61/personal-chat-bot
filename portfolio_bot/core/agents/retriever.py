"""
Retriever Agent - Document Retrieval for RAG

LEARNING NOTES:
---------------
The retriever is responsible for finding relevant documents from the
vector store. It's a key component of RAG (Retrieval-Augmented Generation).

The retrieval process:
1. Extract the user's query from state
2. Search the vector store for similar documents
3. Add the documents to state for the response agent

This is a relatively simple node - it wraps the vector store's search
functionality and formats results for the graph state.

KEY CONCEPTS:
-------------
1. SEMANTIC SEARCH: Finding documents by meaning, not just keywords
2. STATE UPDATE: Adding retrieved documents to state
3. ASYNC OPERATIONS: Non-blocking database queries

WHAT YOU'LL LEARN:
- Integrating external services (vector store) into graph nodes
- Passing data between nodes via state
- Error handling in async nodes
"""

from typing import Optional

from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState
from portfolio_bot.core.vectorstore import get_vector_store
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class Retriever:
    """
    Retriever agent that performs semantic search on the portfolio documents.

    This node runs when the router decides the query needs RAG processing.
    It searches for relevant documents and adds them to state.

    Usage in graph:
        retriever = Retriever()
        graph.add_node("retriever", retriever.run)
        graph.add_edge("retriever", "response_agent")

    LEARNING NOTE: The retriever doesn't generate any response - it just
    finds relevant context. The response_agent will use this context to
    craft the final answer.
    """

    def __init__(self, num_docs: Optional[int] = None):
        """
        Initialize the retriever.

        Args:
            num_docs: Number of documents to retrieve. Uses config default if None.
        """
        self._num_docs = num_docs
        self._vector_store = None  # Initialized lazily
        logger.info("Retriever initialized")

    async def run(self, state: NodeState) -> dict:
        """
        Retrieve relevant documents for the user's query.

        Args:
            state: Current graph state with messages.

        Returns:
            State update with retrieved documents.

        LEARNING NOTE: This demonstrates the typical pattern for a
        retrieval node:
        1. Extract query from messages
        2. Call external service (vector store)
        3. Return state update with results
        """
        # Get vector store (lazy initialization)
        if self._vector_store is None:
            self._vector_store = await get_vector_store()

        # Get the user's query
        messages = state.get("messages", [])
        query = self._extract_query(messages)

        if not query:
            logger.warning("No query found for retrieval")
            return {"documents": []}

        # Perform similarity search
        logger.debug(f"Retrieving documents for: {query[:50]}...")

        try:
            documents = await self._vector_store.similarity_search(
                query=query,
                k=self._num_docs,
            )

            logger.info(f"Retrieved {len(documents)} documents")

            # Log document scores for debugging
            for i, doc in enumerate(documents):
                logger.debug(
                    f"  Doc {i+1}: score={doc.get('score', 'N/A'):.3f}, "
                    f"content={doc['content'][:50]}..."
                )

            return {"documents": documents}

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {"documents": []}

    def _extract_query(self, messages: list) -> str:
        """
        Extract the query from the message history.

        Args:
            messages: List of conversation messages.

        Returns:
            The user's query string.

        LEARNING NOTE: We get the last human message because that's
        what we want to find documents for. In more complex systems,
        you might combine multiple messages or use query rewriting.
        """
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                return msg.content
        return ""


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the retriever agent.

    Make sure ChromaDB is running and has documents:
        docker-compose up -d
        python scripts/ingest_documents.py

    Then run:
        python -m portfolio_bot.core.agents.retriever
    """
    import asyncio
    from langchain_core.messages import HumanMessage

    async def test_retriever():
        print("=== Testing Retriever ===\n")

        retriever = Retriever(num_docs=3)

        test_queries = [
            "What programming languages do you know?",
            "Tell me about your experience",
            "How can I contact you?",
        ]

        for query in test_queries:
            print(f"Query: {query}")

            state: NodeState = {
                "messages": [HumanMessage(content=query)],
            }

            result = await retriever.run(state)
            documents = result.get("documents", [])

            print(f"Retrieved {len(documents)} documents:")
            for i, doc in enumerate(documents):
                score = doc.get("score", "N/A")
                content = doc["content"][:80]
                print(f"  {i+1}. (score: {score:.3f}) {content}...")
            print()

    asyncio.run(test_retriever())
