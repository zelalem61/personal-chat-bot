"""
LangGraph StateGraph - The Core of the Multi-Agent System

LEARNING NOTES:
---------------
This is the heart of the portfolio bot! LangGraph is a framework for building
stateful, multi-actor applications with LLMs. Think of it as a flowchart
where each box (node) is an AI agent or function.

KEY CONCEPTS:
-------------
1. STATGRAPH: The main class that defines your application's flow
   - Nodes: Processing steps (agents, functions)
   - Edges: Connections between nodes
   - State: Data that flows through the graph

2. NODES: Functions that process state
   - Receive current state as input
   - Return partial state updates
   - Can be sync or async

3. EDGES: Define the flow between nodes
   - Regular edges: Always go to specified node
   - Conditional edges: Choose based on state values

4. STATE: TypedDict that flows through the graph
   - Reducers determine how updates are merged
   - add_messages for conversation history
   - replace for simple values

THE GRAPH ARCHITECTURE:
----------------------
```
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
```

WHAT YOU'LL LEARN:
- Building a StateGraph
- Adding nodes and edges
- Conditional routing
- Compiling and running the graph
"""

from langgraph.graph import StateGraph, START, END

from portfolio_bot.core.state import NodeState, InputState, OutputState, RouteType
from portfolio_bot.core.agents.router import Router
from portfolio_bot.core.agents.retriever import Retriever
from portfolio_bot.core.agents.response_agent import ResponseAgent
from portfolio_bot.core.agents.tool_agent import ToolAgent
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


def create_graph():
    """
    Create and compile the portfolio bot graph.

    Returns:
        Compiled StateGraph ready for execution.

    LEARNING NOTE: This function demonstrates the typical pattern for
    creating a LangGraph:
    1. Create a StateGraph with your state type
    2. Add nodes (your agents/functions)
    3. Add edges (connections between nodes)
    4. Compile the graph

    The compiled graph is a runnable that you can invoke with input.
    """

    # =========================================================================
    # Step 1: Create the StateGraph
    # =========================================================================
    # We specify InputState and OutputState to define the external interface.
    # NodeState is the internal state that flows between nodes.

    graph = StateGraph(
        NodeState,
        input=InputState,   # What callers provide
        output=OutputState,  # What callers receive
    )

    # =========================================================================
    # Step 2: Initialize agents
    # =========================================================================
    # Create instances of our agents. In production, you might inject
    # dependencies or use dependency injection frameworks.

    router = Router()
    retriever = Retriever()
    response_agent = ResponseAgent(owner_name="Portfolio Owner")  # Customize this!
    tool_agent = ToolAgent()

    # =========================================================================
    # Step 3: Add nodes to the graph
    # =========================================================================
    # Each node is a function that takes state and returns a state update.
    # The string name is how we reference the node in edges.

    graph.add_node("router", router.run)
    graph.add_node("retriever", retriever.run)
    graph.add_node("response_agent", response_agent.run)
    graph.add_node("tool_agent", tool_agent.run)

    logger.debug("Added 4 nodes to graph")

    # =========================================================================
    # Step 4: Add edges
    # =========================================================================

    # Start → Router: All queries start at the router
    graph.add_edge(START, "router")

    # Router → Conditional: Route based on classification
    # This is where the magic happens! Based on route_type, we go different paths.
    graph.add_conditional_edges(
        "router",  # Source node
        lambda state: state.get("route_type", RouteType.DIRECT).value,  # Condition function
        {
            # Map condition results to target nodes
            RouteType.RAG.value: "retriever",
            RouteType.TOOL.value: "tool_agent",
            RouteType.DIRECT.value: "response_agent",
        },
    )

    # RAG path: Retriever → Response Agent → End
    graph.add_edge("retriever", "response_agent")

    # Tool path: Tool Agent → Response Agent → End
    graph.add_edge("tool_agent", "response_agent")

    # All paths end at response_agent → END
    graph.add_edge("response_agent", END)

    logger.debug("Added edges to graph")

    # =========================================================================
    # Step 5: Compile the graph
    # =========================================================================
    # Compilation validates the graph and creates a runnable.
    # You can add checkpointing here for conversation memory.

    compiled_graph = graph.compile()

    logger.info("Graph compiled successfully")
    return compiled_graph


class PortfolioBot:
    """
    High-level interface for the portfolio bot.

    This class wraps the LangGraph and provides a clean API for:
    - Processing user messages
    - Streaming responses
    - Managing conversation state

    Usage:
        bot = PortfolioBot()
        await bot.initialize()
        response = await bot.chat("Tell me about your experience")

    LEARNING NOTE: This class demonstrates a common pattern - wrapping
    the compiled graph in a higher-level class that handles:
    - Initialization
    - Message formatting
    - Error handling
    - Configuration
    """

    def __init__(self):
        """Initialize the portfolio bot (doesn't start the graph yet)."""
        self._graph = None
        self._initialized = False
        logger.info("PortfolioBot created (not yet initialized)")

    async def initialize(self) -> None:
        """
        Initialize the bot by creating and compiling the graph.

        Call this before using the bot.

        LEARNING NOTE: We separate initialization from __init__ because
        graph creation might be slow or async. This also allows for
        error handling during initialization.
        """
        if self._initialized:
            logger.debug("PortfolioBot already initialized")
            return

        logger.info("Initializing PortfolioBot...")

        # Initialize vector store (needs to be done before graph creation)
        from portfolio_bot.core.vectorstore import get_vector_store
        await get_vector_store()

        # Create and compile the graph
        self._graph = create_graph()

        self._initialized = True
        logger.info("PortfolioBot initialized successfully")

    async def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message and get a response.

        Args:
            message: The user's message.
            thread_id: Conversation thread ID (for memory, not implemented yet).

        Returns:
            The bot's response string.

        LEARNING NOTE: This is the main entry point for chat interactions.
        The message is wrapped in a HumanMessage and passed to the graph.
        The graph processes it through the nodes and returns a response.
        """
        if not self._initialized:
            raise RuntimeError("PortfolioBot not initialized. Call initialize() first.")

        from langchain_core.messages import HumanMessage

        logger.debug(f"Processing message: {message[:50]}...")

        # Create input state with the message
        input_state = {
            "messages": [HumanMessage(content=message)],
        }

        # Run the graph
        try:
            result = await self._graph.ainvoke(input_state)

            # Extract the response
            response = result.get("final_response", "I couldn't generate a response.")

            logger.debug(f"Generated response: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I encountered an error processing your message. Please try again."

    async def stream_chat(self, message: str, thread_id: str = "default"):
        """
        Stream a response token by token.

        Args:
            message: The user's message.
            thread_id: Conversation thread ID.

        Yields:
            Chunks of the response as they're generated.

        LEARNING NOTE: Streaming provides better UX by showing the response
        as it's generated rather than waiting for the entire response.
        LangGraph supports streaming via astream().
        """
        if not self._initialized:
            raise RuntimeError("PortfolioBot not initialized. Call initialize() first.")

        from langchain_core.messages import HumanMessage

        logger.debug(f"Streaming response for: {message[:50]}...")

        input_state = {
            "messages": [HumanMessage(content=message)],
        }

        try:
            # Stream the graph execution
            async for event in self._graph.astream(input_state):
                # Events contain node outputs
                for node_name, node_output in event.items():
                    logger.debug(f"Stream event from {node_name}")

                    # Yield the final response when response_agent completes
                    if node_name == "response_agent" and "final_response" in node_output:
                        yield node_output["final_response"]

        except Exception as e:
            logger.error(f"Error streaming response: {e}", exc_info=True)
            yield "I encountered an error. Please try again."


# =============================================================================
# GRAPH VISUALIZATION
# =============================================================================

def visualize_graph(output_path: str = "graph_structure.png") -> None:
    """
    Generate a visual diagram of the graph structure.

    Args:
        output_path: Path to save the PNG image.

    LEARNING NOTE: Visualization helps understand and debug your graph.
    LangGraph uses Mermaid syntax which can be rendered to images.
    """
    try:
        graph = create_graph()

        # Get the Mermaid diagram
        mermaid_png = graph.get_graph().draw_mermaid_png()

        with open(output_path, "wb") as f:
            f.write(mermaid_png)

        logger.info(f"Graph visualization saved to {output_path}")
        print(f"Graph visualization saved to {output_path}")

    except Exception as e:
        logger.error(f"Failed to generate visualization: {e}")
        print(f"Failed to generate visualization: {e}")
        print("Make sure you have the required dependencies:")
        print("  pip install grandalf")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the portfolio bot.

    Make sure ChromaDB is running and has documents:
        docker-compose up -d
        python scripts/ingest_documents.py

    Then run:
        python -m portfolio_bot.core.graph
    """
    import asyncio

    async def test_bot():
        print("=== Testing PortfolioBot ===\n")

        # Initialize the bot
        bot = PortfolioBot()
        await bot.initialize()

        # Test queries
        test_queries = [
            "Hello!",
            "What programming languages do you know?",
            "Tell me about your experience",
            "Can you send me an email?",
        ]

        for query in test_queries:
            print(f"User: {query}")
            response = await bot.chat(query)
            print(f"Bot: {response}")
            print("-" * 50)

        # Also generate visualization
        print("\nGenerating graph visualization...")
        visualize_graph()

    asyncio.run(test_bot())
