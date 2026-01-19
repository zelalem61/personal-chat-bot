"""
Router Agent - Query Classification

LEARNING NOTES:
---------------
The router is the first decision-making node in our graph. It receives
the user's message and decides how to process it:

1. RAG path: Search documents → Generate response
2. TOOL path: Execute tool → Generate response
3. DIRECT path: Generate response immediately

This demonstrates two important LangGraph concepts:
1. NODES: Functions that process state
2. CONDITIONAL EDGES: Routing based on state values

KEY CONCEPTS:
-------------
1. STRUCTURED OUTPUT: The LLM returns a Pydantic model (RouteDecision)
   instead of free-form text. This makes routing reliable.

2. STATE UPDATES: Nodes return partial state updates (just the fields
   they want to change). LangGraph handles merging.

3. ASYNC NODES: Using async functions allows non-blocking I/O,
   important for web applications.

WHAT YOU'LL LEARN:
- Creating LangGraph node functions
- Using structured output for classification
- Extracting conversation context from messages
"""

from typing import cast

from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState, RouteDecision, RouteType
from portfolio_bot.core.chain import ChainBuilder
from portfolio_bot.core.prompts.router import ROUTER_SYSTEM_PROMPT, ROUTER_HUMAN_PROMPT
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class Router:
    """
    Router agent that classifies queries and determines the processing path.

    This is the first node in the graph after receiving user input.
    It analyzes the query and sets the route_type in state.

    Usage in graph:
        router = Router()
        graph.add_node("router", router.run)
        graph.add_conditional_edges(
            "router",
            router.get_route,  # Function that reads state and returns next node
            {
                RouteType.RAG: "retriever",
                RouteType.TOOL: "tool_agent",
                RouteType.DIRECT: "response_agent",
            }
        )

    LEARNING NOTE: This class encapsulates the router logic. In simpler
    cases, you could use a plain function instead. Classes are nice when
    you need to maintain state or configuration.
    """

    def __init__(self):
        """Initialize the router with its classification chain."""
        self._chain = ChainBuilder(temperature=0.0).build_structured_chain(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            human_prompt=ROUTER_HUMAN_PROMPT,
            output_model=RouteDecision,
        )
        logger.info("Router initialized")

    async def run(self, state: NodeState) -> dict:
        """
        Process the current state and determine the route.

        Args:
            state: Current graph state with messages.

        Returns:
            State update with route_type and optionally tool_name.

        LEARNING NOTE: This is a LangGraph node function. It:
        1. Receives the current state
        2. Does some processing (here, LLM classification)
        3. Returns a partial state update

        The return value is merged into the existing state by LangGraph.
        """
        # Get the latest user message
        messages = state.get("messages", [])
        if not messages:
            logger.warning("No messages in state")
            return {"route_type": RouteType.DIRECT}

        # Find the last human message
        query = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if not query:
            logger.warning("No human message found")
            return {"route_type": RouteType.DIRECT}

        # Build conversation context (last few messages for context)
        context = self._build_context(messages[:-1])  # Exclude current message

        # Classify the query
        logger.debug(f"Routing query: {query[:50]}...")

        try:
            decision: RouteDecision = await self._chain.ainvoke({
                "query": query,
                "context": context or "No previous context",
            })

            logger.info(
                f"Route decision: {decision.route_type.value} "
                f"(tool: {decision.tool_name}, reason: {decision.reasoning[:50]}...)"
            )

            # Build state update
            update = {
                "route_type": decision.route_type,
            }

            # Include tool_name if routing to tool
            if decision.route_type == RouteType.TOOL and decision.tool_name:
                update["tool_name"] = decision.tool_name

            return update

        except Exception as e:
            logger.error(f"Router error: {e}")
            # Default to direct response on error
            return {"route_type": RouteType.DIRECT}

    def _build_context(self, messages: list, max_messages: int = 4) -> str:
        """
        Build a context string from recent messages.

        Args:
            messages: List of conversation messages.
            max_messages: Maximum number of messages to include.

        Returns:
            Formatted string of recent conversation.

        LEARNING NOTE: Providing context helps the router make better
        decisions. For example, "yes" after "Would you like to schedule
        a meeting?" should route to the calendar tool.
        """
        if not messages:
            return ""

        recent = messages[-max_messages:]
        context_parts = []

        for msg in recent:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content[:100]  # Truncate long messages
            context_parts.append(f"{role}: {content}")

        return "\n".join(context_parts)

    @staticmethod
    def get_route(state: NodeState) -> str:
        """
        Determine the next node based on route_type.

        Args:
            state: Current graph state.

        Returns:
            Name of the next node.

        LEARNING NOTE: This function is used with add_conditional_edges().
        LangGraph calls it after the router node completes and uses the
        return value to decide which node to run next.

        The return value must match one of the keys in the routing map
        provided to add_conditional_edges().
        """
        route_type = state.get("route_type", RouteType.DIRECT)

        # Return the route type value as the edge name
        return route_type.value


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the router agent.

    Run: python -m portfolio_bot.core.agents.router
    """
    import asyncio
    from langchain_core.messages import HumanMessage, AIMessage

    async def test_router():
        router = Router()

        test_cases = [
            # RAG queries
            {"query": "What is your experience with Python?", "expected": RouteType.RAG},
            {"query": "Tell me about your projects", "expected": RouteType.RAG},
            # Tool queries
            {"query": "Can you send me an email?", "expected": RouteType.TOOL},
            {"query": "I'd like to schedule a meeting", "expected": RouteType.TOOL},
            # Direct queries
            {"query": "Hello!", "expected": RouteType.DIRECT},
            {"query": "What can you help me with?", "expected": RouteType.DIRECT},
        ]

        print("=== Testing Router ===\n")

        for case in test_cases:
            state: NodeState = {
                "messages": [HumanMessage(content=case["query"])],
            }

            result = await router.run(state)
            actual = result.get("route_type", RouteType.DIRECT)
            match = "✓" if actual == case["expected"] else "✗"

            print(f"{match} Query: {case['query'][:40]}...")
            print(f"   Expected: {case['expected'].value}, Got: {actual.value}")
            if result.get("tool_name"):
                print(f"   Tool: {result['tool_name']}")
            print()

    asyncio.run(test_router())
