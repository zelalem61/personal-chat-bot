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
# TODO: Implement Router Class
# =============================================================================
# class Router:
#     def __init__(self):
#         # Create a structured chain that returns RouteDecision
#         # self._chain = ChainBuilder(temperature=0.0).build_structured_chain(
#         #     system_prompt=ROUTER_SYSTEM_PROMPT,
#         #     human_prompt=ROUTER_HUMAN_PROMPT,
#         #     output_model=RouteDecision,
#         # )
#         pass
#
#     async def run(self, state: NodeState) -> dict:
#         # 1. Get the last HumanMessage from state["messages"]
#         # 2. Invoke the chain with {"query": query, "context": "..."}
#         # 3. Return {"route_type": decision.route_type, "tool_name": decision.tool_name}
#         pass
pass
