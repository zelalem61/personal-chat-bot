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

from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState
from portfolio_bot.core.vectorstore import get_vector_store
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement Retriever Class
# =============================================================================
# class Retriever:
#     def __init__(self, num_docs: Optional[int] = None):
#         self._num_docs = num_docs
#         self._vector_store = None  # Lazy init
#
#     async def run(self, state: NodeState) -> dict:
#         # 1. Get vector store: if self._vector_store is None: self._vector_store = await get_vector_store()
#         # 2. Extract query from last HumanMessage in state["messages"]
#         # 3. Search: documents = await self._vector_store.similarity_search(query, k=self._num_docs)
#         # 4. Return {"documents": documents}
#         pass
pass
