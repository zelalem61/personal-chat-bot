"""
Response Agent - Final Response Generation

LEARNING NOTES:
---------------
The response agent generates user-facing responses using:
- Retrieved documents (from RAG path)
- Tool results (from TOOL path)
- Or just the query (DIRECT path)

KEY CONCEPTS:
-------------
1. CONTEXT INTEGRATION: Combining multiple information sources
2. PROMPT TEMPLATING: Filling prompts with dynamic content
3. MESSAGE HANDLING: Returning AIMessage to conversation history

YOUR TASK: (See roadmap.md Step 5)
----------
1. Implement ResponseAgent class with a chain for response generation
2. Implement run(state) that uses documents/tool_result as context
3. Return state update with messages (AIMessage) and final_response
"""

from langchain_core.messages import HumanMessage, AIMessage

from portfolio_bot.core.state import NodeState
from portfolio_bot.core.chain import ChainBuilder
from portfolio_bot.core.prompts.response import RESPONSE_SYSTEM_PROMPT, RESPONSE_HUMAN_PROMPT
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# TODO: Implement ResponseAgent Class
# =============================================================================
# class ResponseAgent:
#     def __init__(self, owner_name: str = "Portfolio Owner"):
#         self._owner_name = owner_name
#         # Create chain with RESPONSE_SYSTEM_PROMPT.format(owner_name=owner_name)
#         # self._chain = ChainBuilder(temperature=0.7).build_chain(...)
#         pass
#
#     async def run(self, state: NodeState) -> dict:
#         # 1. Extract query from messages, documents from state, tool_result from state
#         # 2. Format documents into a context string
#         # 3. Invoke chain with {"query": ..., "context": ..., "tool_results": ...}
#         # 4. Return {"messages": [AIMessage(content=response)], "final_response": response}
#         pass
pass
