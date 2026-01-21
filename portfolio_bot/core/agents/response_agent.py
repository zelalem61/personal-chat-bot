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


class ResponseAgent:
    """
    Final response generator for the portfolio bot.

    Combines:
    - User query
    - Retrieved documents (RAG)
    - Tool results (TOOL path)
    - Conversation history
    into a single, user-facing answer.
    """

    def __init__(self, owner_name: str = "Portfolio Owner"):
        self._owner_name = owner_name
        system_prompt = RESPONSE_SYSTEM_PROMPT.format(owner_name=owner_name)

        # Build a text generation chain for responses
        self._chain = ChainBuilder(temperature=0.7).build_chain(
            system_prompt=system_prompt,
            human_prompt=RESPONSE_HUMAN_PROMPT,
        )
        logger.info("ResponseAgent initialized for owner '%s'", owner_name)

    async def run(self, state: NodeState) -> dict:
        """
        Generate the final response based on current state.

        Returns a state update containing:
        - messages: [AIMessage(...)]
        - final_response: str
        """
        messages = state.get("messages", [])
        documents = state.get("documents", [])
        tool_result = state.get("tool_result")

        # 1. Extract query from the last HumanMessage
        query = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if query is None:
            logger.warning(
                "ResponseAgent.run called with no HumanMessage; defaulting to empty query."
            )
            query = ""

        # 2. Format documents into a context string
        context_parts = []
        for idx, doc in enumerate(documents):
            content = doc.get("content") or doc.get("page_content") or ""
            if not content:
                continue
            metadata = doc.get("metadata", {}) or {}
            header = f"[Document {idx + 1}]"
            if metadata:
                header += f" (metadata: {metadata})"
            context_parts.append(f"{header}\n{content}")
        context = "\n\n".join(context_parts) if context_parts else "No retrieved documents."

        # 3. Format tool results
        tool_results_str = ""
        if tool_result is not None:
            tool_results_str = str(tool_result)

        # 4. Conversation history (excluding latest query for clarity)
        history_parts = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant" if isinstance(
                msg, AIMessage
            ) else getattr(msg, "type", "message")
            content = getattr(msg, "content", "")
            history_parts.append(f"{role}: {content}")
        conversation_history = "\n".join(history_parts)

        # 5. Invoke chain
        response_text: str = await self._chain.ainvoke(
            {
                "query": query,
                "context": context,
                "tool_results": tool_results_str,
                "conversation_history": conversation_history,
            }
        )

        logger.info("ResponseAgent generated response of length %d", len(response_text))

        # 6. Return state update
        ai_message = AIMessage(content=response_text)
        return {
            "messages": [ai_message],
            "final_response": response_text,
        }

