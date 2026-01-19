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

from portfolio_bot.core.state import NodeState, InputState, OutputState, RouteType
from portfolio_bot.core.agents.router import Router
from portfolio_bot.core.agents.retriever import Retriever
from portfolio_bot.core.agents.response_agent import ResponseAgent
from portfolio_bot.core.agents.tool_agent import ToolAgent
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement create_graph() function
# =============================================================================
# def create_graph():
#     # 1. Create StateGraph: graph = StateGraph(NodeState, input=InputState, output=OutputState)
#
#     # 2. Initialize agents
#     # router = Router()
#     # retriever = Retriever()
#     # response_agent = ResponseAgent(owner_name="Your Name")
#     # tool_agent = ToolAgent()
#
#     # 3. Add nodes
#     # graph.add_node("router", router.run)
#     # graph.add_node("retriever", retriever.run)
#     # graph.add_node("response_agent", response_agent.run)
#     # graph.add_node("tool_agent", tool_agent.run)
#
#     # 4. Add edges
#     # graph.add_edge(START, "router")
#     # graph.add_conditional_edges("router",
#     #     lambda state: state.get("route_type", RouteType.DIRECT).value,
#     #     {"rag": "retriever", "tool": "tool_agent", "direct": "response_agent"})
#     # graph.add_edge("retriever", "response_agent")
#     # graph.add_edge("tool_agent", "response_agent")
#     # graph.add_edge("response_agent", END)
#
#     # 5. Compile and return
#     # return graph.compile()
#     pass
pass


# =============================================================================
# TODO: Implement PortfolioBot Class
# =============================================================================
# class PortfolioBot:
#     def __init__(self):
#         self._graph = None
#         self._initialized = False
#
#     async def initialize(self):
#         # 1. Initialize vector store: from portfolio_bot.core.vectorstore import get_vector_store
#         # 2. Create graph: self._graph = create_graph()
#         # 3. Set _initialized = True
#         pass
#
#     async def chat(self, message: str, thread_id: str = "default") -> str:
#         # 1. Check initialized
#         # 2. Create input: {"messages": [HumanMessage(content=message)]}
#         # 3. Run graph: result = await self._graph.ainvoke(input_state)
#         # 4. Return result.get("final_response")
#         pass
pass
