"""
LangGraph StateGraph - The Core of the Multi-Agent System

LEARNING NOTES:
---------------
LangGraph models your application as a graph where:
- Nodes: Processing steps (your agents)
- Edges: Connections between nodes
- State: Data that flows through the graph

THE GRAPH ARCHITECTURE:
----------------------
START
  │
  ▼
[router] ──────► Classifies query: RAG, TOOL, or DIRECT
  │
  ├──► RAG path:    [retriever] ──► [response_agent] ──► END
  │
  ├──► TOOL path:   [tool_agent] ──► [response_agent] ──► END
  │
  └──► DIRECT path: [response_agent] ──► END

YOUR TASK: (See roadmap.md Step 6)
----------
1. Implement create_graph() function
2. Implement PortfolioBot class with initialize() and chat() methods
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState, InputState, OutputState, RouteType
from portfolio_bot.core.agents.router import Router
from portfolio_bot.core.agents.retriever import Retriever
from portfolio_bot.core.agents.response_agent import ResponseAgent
from portfolio_bot.core.agents.tool_agent import ToolAgent
from portfolio_bot.core.vectorstore import get_vector_store
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement create_graph() function
# =============================================================================
def create_graph():
    """
    Create and compile the LangGraph StateGraph for the portfolio bot.

    Graph topology:
        START -> router
            rag   -> retriever -> response_agent -> END
            tool  -> tool_agent -> response_agent -> END
            direct-> response_agent -> END
    """
    # 1. Create StateGraph
    graph = StateGraph(NodeState, input=InputState, output=OutputState)

    # Add in-memory checkpointer so conversations can maintain state across turns
    checkpointer = MemorySaver()

    # 2. Initialize agents
    router = Router()
    retriever = Retriever()
    response_agent = ResponseAgent(owner_name="Zelalem")
    tool_agent = ToolAgent()

    # 3. Add nodes
    graph.add_node("router", router.run)
    graph.add_node("retriever", retriever.run)
    graph.add_node("response_agent", response_agent.run)
    graph.add_node("tool_agent", tool_agent.run)

    # 4. Add edges
    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router",
        lambda state: state.get("route_type", RouteType.DIRECT).value,
        {"rag": "retriever", "tool": "tool_agent", "direct": "response_agent"},
    )
    graph.add_edge("retriever", "response_agent")
    graph.add_edge("tool_agent", "response_agent")
    graph.add_edge("response_agent", END)

    # 5. Compile and return
    compiled_graph = graph.compile(checkpointer=checkpointer)
    logger.info("LangGraph compiled successfully for PortfolioBot with MemorySaver checkpointer")
    
    return compiled_graph


# =============================================================================
# TODO: Implement PortfolioBot Class
# =============================================================================
class PortfolioBot:
    """
    High-level interface for interacting with the portfolio chat bot.

    Usage:
        bot = PortfolioBot()
        await bot.initialize()
        response = await bot.chat("Tell me about your experience.")
    """

    def __init__(self):
        self._graph = None
        self._initialized = False

    async def initialize(self):
        """
        Initialize underlying resources (vector store, graph).

        LEARNING NOTE: This is separated from __init__ so you can control
        when I/O-heavy initialization happens (e.g., during app startup).
        """
        # 1. Initialize vector store (ensures collection & embeddings are ready)
        try:
            await get_vector_store()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to initialize vector store: %s", exc)
            raise

        # 2. Create graph
        self._graph = create_graph()

        # 3. Mark as initialized
        self._initialized = True
        logger.info("PortfolioBot initialized successfully")

    async def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a user message through the graph and return the final response.

        Args:
            message: User's query/message.
            thread_id: Conversation identifier (reserved for future use).
        """
        # 1. Check initialized
        if not self._initialized or self._graph is None:
            raise RuntimeError(
                "PortfolioBot is not initialized. Call `await bot.initialize()` first."
            )

        # 2. Create input state
        input_state = {"messages": [HumanMessage(content=message)]}

        # 3. Run graph with thread-specific memory
        result = await self._graph.ainvoke(
            input_state,
            config={"configurable": {"thread_id": thread_id}},
        )

        # 4. Return final response
        return result.get("final_response", "")

