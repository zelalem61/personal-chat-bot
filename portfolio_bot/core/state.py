"""
State Management for LangGraph

LEARNING NOTES:
---------------
State is the most important concept in LangGraph. It's a TypedDict that flows
between nodes (agents) in the graph. Each node:
1. Receives the current state
2. Does some processing
3. Returns a partial state update (only the fields it wants to change)

LangGraph then MERGES the update into the existing state using "reducers".

KEY CONCEPTS:
-------------
1. REDUCERS: Functions that determine HOW state fields are updated
   - Default behavior: replace the old value with new value
   - add_messages: appends messages to the conversation history

2. ANNOTATED TYPES: Python's Annotated[] lets us attach metadata to types.
   LangGraph uses this to specify reducers:
   - Annotated[list, add_messages] = "append new messages to this list"

3. STATE FLOW:
   Input → Node1 → State Update → Node2 → State Update → Output

YOUR TASK: (See roadmap.md Step 1)
----------
1. Create RouteType enum with values: RAG, TOOL, DIRECT
2. Create NodeState TypedDict with fields for messages, route_type, documents, etc.
3. Create InputState and OutputState for the graph interface
4. Create RouteDecision Pydantic model for structured router output
"""

from enum import Enum
from typing import Annotated, Any, Dict, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# =============================================================================
# RouteType Enum
# =============================================================================


class RouteType(str, Enum):
    """
    Route type selected by the router.

    - RAG:   Retrieve documents then answer
    - TOOL:  Call a tool, then answer
    - DIRECT: Answer directly with no extra context
    """

    RAG = "rag"
    TOOL = "tool"
    DIRECT = "direct"


# =============================================================================
# NodeState TypedDict
# =============================================================================


class NodeState(TypedDict, total=False):
    """
    Core graph state shared between all nodes.

    Each node reads some fields and returns a partial update with the fields
    it wants to modify. LangGraph merges those updates using reducers.
    """

    # Conversation history; add_messages appends new messages
    messages: Annotated[list[BaseMessage], add_messages]

    # Routing information
    route_type: RouteType
    tool_name: Optional[str]
    tool_args: Dict[str, Any]

    # Results from tool execution
    tool_result: Optional[Any]

    # Retrieved documents for RAG
    documents: list[Dict[str, Any]]

    # Final response text for the user
    final_response: Optional[str]


# =============================================================================
# InputState TypedDict
# =============================================================================


class InputState(TypedDict):
    """
    External input to the graph.

    For this bot, the only required input is the list of messages.
    """

    messages: Annotated[list[BaseMessage], add_messages]


# =============================================================================
# OutputState TypedDict
# =============================================================================


class OutputState(TypedDict, total=False):
    """
    External output from the graph.

    Exposes the final response and (optionally) the full message history.
    """

    messages: list[BaseMessage]
    final_response: str


# =============================================================================
# RouteDecision Pydantic Model
# =============================================================================


class RouteDecision(BaseModel):
    """
    Structured output returned by the router LLM.
    """

    route_type: RouteType = Field(
        description="How the query should be handled: 'rag', 'tool', or 'direct'."
    )
    tool_name: Optional[str] = Field(
        default=None,
        description="Name of the tool to call when route_type is 'tool'; otherwise None.",
    )
    reasoning: str = Field(
        description="Brief explanation of why this route was chosen."
    )

