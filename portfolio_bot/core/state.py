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
   - Custom reducers: you define the merge logic

2. ANNOTATED TYPES: Python's Annotated[] lets us attach metadata to types.
   LangGraph uses this to specify reducers:
   - Annotated[list, add_messages] = "append new messages to this list"
   - Annotated[str, lambda old, new: new] = "replace old with new"

3. STATE FLOW:
   Input → Node1 → State Update → Node2 → State Update → Output

WHAT YOU'LL LEARN:
- TypedDict for type-safe dictionaries
- Annotated types with reducers
- Enum for routing decisions
- Pydantic models for structured data
"""

from enum import Enum
from typing import Annotated, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# =============================================================================
# ROUTE TYPE ENUM
# =============================================================================


class RouteType(str, Enum):
    """
    Enum defining the possible routing decisions.

    The router agent classifies each query into one of these types:
    - RAG: Answer using retrieved documents (portfolio info)
    - TOOL: Execute a tool (email, calendar, etc.)
    - DIRECT: Answer directly without retrieval or tools

    LEARNING NOTE: Using an Enum instead of plain strings provides:
    1. Type safety - IDE/linter catches typos
    2. Autocomplete - easier to discover valid values
    3. Documentation - all valid values in one place
    """

    RAG = "rag"
    TOOL = "tool"
    DIRECT = "direct"


# =============================================================================
# STATE DEFINITIONS
# =============================================================================


class NodeState(TypedDict, total=False):
    """
    The main state that flows through the LangGraph.

    LEARNING NOTE: TypedDict with total=False means all fields are optional.
    This is important because:
    1. Different nodes may only need certain fields
    2. State updates only include changed fields
    3. New fields can be added without breaking existing nodes

    REDUCER EXPLANATION:
    --------------------
    The Annotated[type, reducer] syntax tells LangGraph how to merge updates.

    For `messages`:
        Annotated[list[BaseMessage], add_messages]

        This means: when a node returns {"messages": [new_message]},
        LangGraph will APPEND new_message to the existing messages list,
        not replace the entire list. This preserves conversation history.

    For other fields:
        No annotation means "replace" - the new value overwrites the old.
    """

    # ----- Conversation History -----
    # This is the chat history. The add_messages reducer appends new messages.
    messages: Annotated[list[BaseMessage], add_messages]

    # ----- Routing Information -----
    # Set by the router to determine which path to take
    route_type: RouteType

    # ----- Retrieved Documents -----
    # Documents retrieved from ChromaDB for RAG
    # Each document is a dict with 'content' and 'metadata' keys
    documents: list[dict]

    # ----- Tool Execution -----
    # Name of the tool to execute (if route_type is TOOL)
    tool_name: Optional[str]

    # Arguments for the tool (if applicable)
    tool_args: Optional[dict]

    # Result from tool execution
    tool_result: Optional[str]

    # ----- Response -----
    # The final response to send back to the user
    final_response: Optional[str]


class InputState(TypedDict):
    """
    Schema for the input to the graph.

    This is what external callers provide when invoking the graph.
    It's simpler than NodeState because callers only need to provide
    the user's message.

    LEARNING NOTE: Separating InputState from NodeState is a LangGraph
    best practice. It:
    1. Documents what external callers should provide
    2. Hides internal state fields from the API
    3. Makes the interface cleaner and more stable
    """

    messages: Annotated[list[BaseMessage], add_messages]


class OutputState(TypedDict):
    """
    Schema for the output from the graph.

    This defines what the graph returns after processing.

    LEARNING NOTE: Similar to InputState, this provides a clean
    interface and hides internal implementation details.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    final_response: str


# =============================================================================
# STRUCTURED OUTPUT MODELS
# =============================================================================


class RouteDecision(BaseModel):
    """
    Pydantic model for the router's structured output.

    The router LLM returns this model directly, which LangGraph
    can then use to make routing decisions.

    LEARNING NOTE: Using Pydantic models for LLM output provides:
    1. Type validation - ensures LLM returns expected structure
    2. Clear schema - LLM knows exactly what to return
    3. Easy access - use dot notation (decision.route_type)

    This is called "structured output" or "function calling" depending
    on the LLM provider.
    """

    route_type: RouteType = Field(
        description="The type of routing to perform: 'rag' for document retrieval, "
        "'tool' for tool execution, or 'direct' for immediate response"
    )

    tool_name: Optional[str] = Field(
        default=None,
        description="If route_type is 'tool', the name of the tool to execute. "
        "Options: 'email', 'calendar'. None for other route types.",
    )

    reasoning: str = Field(
        description="Brief explanation of why this route was chosen. "
        "This helps with debugging and understanding the bot's decisions."
    )


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Quick test to verify state definitions work correctly.

    Run this file directly to see how state updates work:
        python -m portfolio_bot.core.state
    """
    from langchain_core.messages import HumanMessage, AIMessage

    # Create initial state
    initial_state: NodeState = {
        "messages": [HumanMessage(content="Hello!")],
        "route_type": RouteType.DIRECT,
        "documents": [],
        "tool_name": None,
        "tool_args": None,
        "tool_result": None,
        "final_response": None,
    }

    print("Initial state:")
    print(f"  Messages: {len(initial_state['messages'])} message(s)")
    print(f"  Route type: {initial_state['route_type']}")

    # Simulate a state update (what a node might return)
    state_update = {
        "messages": [AIMessage(content="Hi there! How can I help?")],
        "final_response": "Hi there! How can I help?",
    }

    print("\nState update from node:")
    print(f"  New messages: {len(state_update['messages'])}")

    # In LangGraph, the add_messages reducer would append the new message
    # to the existing messages list, resulting in 2 messages total.
    print("\nAfter LangGraph applies reducers:")
    print("  Messages would have 2 messages (original + new)")

    # Test RouteDecision structured output
    decision = RouteDecision(
        route_type=RouteType.RAG,
        tool_name=None,
        reasoning="User is asking about portfolio experience, need to retrieve documents",
    )

    print("\nRouteDecision example:")
    print(f"  Route: {decision.route_type}")
    print(f"  Reasoning: {decision.reasoning}")
