"""
Router Agent - Query Classification

LEARNING NOTES:
---------------
The router classifies user queries into:
1. RAG path: Search documents → Generate response
2. TOOL path: Execute tool → Generate response
3. DIRECT path: Generate response immediately

KEY CONCEPTS:
-------------
1. STRUCTURED OUTPUT: LLM returns a Pydantic model (RouteDecision)
2. STATE UPDATES: Nodes return partial updates that LangGraph merges
3. ASYNC NODES: Non-blocking I/O for web applications

YOUR TASK: (See roadmap.md Step 5)
----------
1. Implement Router class with __init__ creating a structured chain
2. Implement run(state) method that classifies the query
3. Return state update with route_type (and tool_name if applicable)
"""

from langchain_core.messages import HumanMessage

from portfolio_bot.core.state import NodeState, RouteDecision, RouteType
from portfolio_bot.core.chain import ChainBuilder
from portfolio_bot.core.prompts.router import ROUTER_SYSTEM_PROMPT, ROUTER_HUMAN_PROMPT
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Router Class
# =============================================================================


class Router:
    """
    Classifies incoming user queries into RAG, TOOL, or DIRECT routes.

    Uses a structured-output chain that returns a `RouteDecision` Pydantic model.
    """

    def __init__(self):
        # Create a structured chain that returns RouteDecision
        self._chain = ChainBuilder(temperature=0.0).build_structured_chain(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            human_prompt=ROUTER_HUMAN_PROMPT,
            output_model=RouteDecision,
        )
        logger.info("Router initialized with structured routing chain")

    async def run(self, state: NodeState) -> dict:
        """
        Classify the latest user message and decide the processing route.

        Args:
            state: Current graph state including conversation messages.

        Returns:
            dict: Partial state update with `route_type` and optional `tool_name`.
        """
        messages = state.get("messages", [])

        # 1. Get the last HumanMessage from state["messages"]
        query = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if not query:
            logger.warning(
                "Router.run called with no HumanMessage in state; defaulting to DIRECT route."
            )
            return {"route_type": RouteType.DIRECT}

        # Build a lightweight textual context from previous messages (excluding latest).
        context_parts = []
        for msg in messages[:-1]:
            role = getattr(msg, "type", "message")
            content = getattr(msg, "content", "")
            context_parts.append(f"{role}: {content}")
        context = "\n".join(context_parts).strip()

        # 2. Invoke the chain with {"query": query, "context": "..."}
        decision: RouteDecision = await self._chain.ainvoke(
            {"query": query, "context": context}
        )

        logger.info(
            "Router decision: route_type=%s, tool_name=%s",
            decision.route_type,
            getattr(decision, "tool_name", None),
        )

        # 3. Return state update
        return {
            "route_type": decision.route_type,
            "tool_name": getattr(decision, "tool_name", None),
        }

