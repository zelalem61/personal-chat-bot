"""
Response Agent - Final Response Generation

LEARNING NOTES:
---------------
The response agent is the final node that generates user-facing responses.
It receives context from previous nodes:
- Retrieved documents (from RAG path)
- Tool results (from TOOL path)
- Or just the query (DIRECT path)

And generates a natural, helpful response.

KEY CONCEPTS:
-------------
1. CONTEXT INTEGRATION: Combining multiple sources of information
2. PROMPT TEMPLATING: Filling in prompts with dynamic content
3. MESSAGE HANDLING: Returning properly formatted messages

WHAT YOU'LL LEARN:
- Building response generation chains
- Using retrieved context effectively
- Returning messages to the conversation
"""

from langchain_core.messages import HumanMessage, AIMessage

from portfolio_bot.core.state import NodeState
from portfolio_bot.core.chain import ChainBuilder
from portfolio_bot.core.prompts.response import (
    RESPONSE_SYSTEM_PROMPT,
    RESPONSE_HUMAN_PROMPT,
    GREETING_RESPONSE_PROMPT,
)
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)

# Default owner name - replace with your name or load from config
DEFAULT_OWNER_NAME = "Portfolio Owner"


class ResponseAgent:
    """
    Response agent that generates final responses to users.

    This is the final node in all paths. It takes context from
    previous nodes and generates a helpful, natural response.

    Usage in graph:
        response_agent = ResponseAgent()
        graph.add_node("response_agent", response_agent.run)
        graph.add_edge("response_agent", END)

    LEARNING NOTE: All paths in the graph eventually lead here.
    The response agent must handle different scenarios:
    - RAG: Use retrieved documents
    - TOOL: Report tool results
    - DIRECT: Answer without context
    """

    def __init__(self, owner_name: str = DEFAULT_OWNER_NAME):
        """
        Initialize the response agent.

        Args:
            owner_name: Name of the portfolio owner for personalization.
        """
        self._owner_name = owner_name
        self._chain = ChainBuilder(temperature=0.7).build_chain(
            system_prompt=RESPONSE_SYSTEM_PROMPT.format(owner_name=owner_name),
            human_prompt=RESPONSE_HUMAN_PROMPT,
        )
        logger.info(f"ResponseAgent initialized for {owner_name}")

    async def run(self, state: NodeState) -> dict:
        """
        Generate a response based on the current state.

        Args:
            state: Current graph state with messages, documents, tool_result, etc.

        Returns:
            State update with the AI response message and final_response.

        LEARNING NOTE: The return value includes:
        - messages: New AI message to add to history (uses add_messages reducer)
        - final_response: Plain text for API responses
        """
        # Extract components from state
        messages = state.get("messages", [])
        documents = state.get("documents", [])
        tool_result = state.get("tool_result")

        # Get the user's query
        query = self._get_last_human_message(messages)

        # Build context from retrieved documents
        context = self._format_documents(documents)

        # Build conversation history (excluding current query)
        conversation_history = self._format_conversation(messages[:-1] if messages else [])

        # Generate response
        logger.debug(f"Generating response for: {query[:50]}...")

        try:
            response = await self._chain.ainvoke({
                "query": query,
                "context": context or "No relevant documents found.",
                "tool_results": tool_result or "No tools were used.",
                "conversation_history": conversation_history or "No previous conversation.",
            })

            logger.info(f"Generated response: {response[:50]}...")

            # Return state update with new message
            return {
                "messages": [AIMessage(content=response)],
                "final_response": response,
            }

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            error_response = (
                "I apologize, but I encountered an error generating a response. "
                "Please try again or rephrase your question."
            )
            return {
                "messages": [AIMessage(content=error_response)],
                "final_response": error_response,
            }

    def _get_last_human_message(self, messages: list) -> str:
        """Extract the last human message content."""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                return msg.content
        return ""

    def _format_documents(self, documents: list) -> str:
        """
        Format retrieved documents for the prompt.

        Args:
            documents: List of document dicts with 'content' and 'metadata'.

        Returns:
            Formatted string of documents.

        LEARNING NOTE: Good formatting helps the LLM use context effectively.
        Include relevant metadata (source, section) to help with attribution.
        """
        if not documents:
            return ""

        formatted = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "unknown")
            section = metadata.get("section", "")

            header = f"[Document {i}]"
            if section:
                header += f" ({section})"

            formatted.append(f"{header}\n{content}\n")

        return "\n".join(formatted)

    def _format_conversation(self, messages: list, max_messages: int = 6) -> str:
        """
        Format conversation history for context.

        Args:
            messages: List of previous messages.
            max_messages: Maximum messages to include.

        Returns:
            Formatted conversation string.
        """
        if not messages:
            return ""

        recent = messages[-max_messages:]
        formatted = []

        for msg in recent:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{role}: {msg.content}")

        return "\n".join(formatted)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the response agent.

    Run: python -m portfolio_bot.core.agents.response_agent
    """
    import asyncio
    from langchain_core.messages import HumanMessage

    async def test_response_agent():
        print("=== Testing ResponseAgent ===\n")

        agent = ResponseAgent(owner_name="Jane Developer")

        # Test with documents (RAG scenario)
        print("--- RAG Scenario ---")
        state: NodeState = {
            "messages": [HumanMessage(content="What programming languages do you know?")],
            "documents": [
                {
                    "content": "Jane is proficient in Python, JavaScript, and TypeScript. She has 5 years of experience with Python and uses it for backend development and machine learning projects.",
                    "metadata": {"source": "portfolio.md", "section": "skills"},
                },
                {
                    "content": "Technical stack includes React, FastAPI, PostgreSQL, and Docker. Jane also has experience with cloud platforms like AWS and GCP.",
                    "metadata": {"source": "portfolio.md", "section": "tech"},
                },
            ],
        }

        result = await agent.run(state)
        print(f"Query: What programming languages do you know?")
        print(f"Response: {result['final_response']}\n")

        # Test direct scenario (no documents)
        print("--- Direct Scenario ---")
        state: NodeState = {
            "messages": [HumanMessage(content="Hello!")],
            "documents": [],
        }

        result = await agent.run(state)
        print(f"Query: Hello!")
        print(f"Response: {result['final_response']}\n")

        # Test with tool result
        print("--- Tool Result Scenario ---")
        state: NodeState = {
            "messages": [HumanMessage(content="Send an email to request more info")],
            "documents": [],
            "tool_result": "Email sent successfully to jane@example.com",
        }

        result = await agent.run(state)
        print(f"Query: Send an email to request more info")
        print(f"Response: {result['final_response']}")

    asyncio.run(test_response_agent())
