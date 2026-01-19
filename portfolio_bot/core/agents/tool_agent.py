"""
Tool Agent - Tool Execution (PLACEHOLDER)

LEARNING NOTES:
---------------
This is a PLACEHOLDER for you to implement! The tool agent is responsible
for executing tools when the router decides a tool is needed.

Tools in LangChain/LangGraph are functions that the LLM can call to
interact with external systems:
- Send emails
- Check calendars
- Query databases
- Call APIs

YOUR TASK:
----------
Implement the tools in portfolio_bot/core/tools/ and wire them up here.

IMPLEMENTATION HINTS:
---------------------
1. Create tool functions in core/tools/ using the @tool decorator
2. Import and register tools in this agent
3. Execute the appropriate tool based on state["tool_name"]
4. Return the result in state["tool_result"]

WHAT YOU'LL LEARN:
- LangChain tool creation with @tool decorator
- Tool execution patterns
- Error handling for external calls
"""

from portfolio_bot.core.state import NodeState
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)


class ToolAgent:
    """
    Tool agent that executes tools based on the router's decision.

    PLACEHOLDER: This agent is intentionally incomplete for learning purposes.
    Your task is to:
    1. Create tools in portfolio_bot/core/tools/
    2. Register them in this agent
    3. Implement the execution logic

    Usage in graph:
        tool_agent = ToolAgent()
        graph.add_node("tool_agent", tool_agent.run)
        graph.add_edge("tool_agent", "response_agent")

    Example tools to implement:
    - email_tool: Send contact emails
    - calendar_tool: Check availability / schedule meetings
    """

    def __init__(self):
        """
        Initialize the tool agent.

        TODO: Register your tools here. Example:

            from portfolio_bot.core.tools.email_tool import send_email
            from portfolio_bot.core.tools.calendar_tool import check_availability

            self._tools = {
                "email": send_email,
                "calendar": check_availability,
            }
        """
        # Placeholder: No tools registered yet
        self._tools = {}
        logger.info("ToolAgent initialized (placeholder - implement tools!)")

    async def run(self, state: NodeState) -> dict:
        """
        Execute the requested tool.

        Args:
            state: Current graph state with tool_name and optionally tool_args.

        Returns:
            State update with tool_result.

        TODO: Implement tool execution. Example:

            tool_name = state.get("tool_name")
            tool_args = state.get("tool_args", {})

            if tool_name in self._tools:
                result = await self._tools[tool_name](**tool_args)
                return {"tool_result": result}
            else:
                return {"tool_result": f"Unknown tool: {tool_name}"}
        """
        tool_name = state.get("tool_name")
        tool_args = state.get("tool_args", {})

        logger.info(f"Tool requested: {tool_name} (args: {tool_args})")

        # =================================================================
        # PLACEHOLDER IMPLEMENTATION
        # =================================================================
        # This is a placeholder response. Replace with actual tool execution.
        #
        # To implement:
        # 1. Create tools in core/tools/ (see example below)
        # 2. Import and register them in __init__
        # 3. Call the tool here and return the result

        if tool_name == "email":
            # Placeholder response for email tool
            result = (
                "📧 EMAIL TOOL (Placeholder)\n"
                "This tool would send an email. To implement:\n"
                "1. Create portfolio_bot/core/tools/email_tool.py\n"
                "2. Use a service like SendGrid, Mailjet, or SMTP\n"
                "3. Register the tool in ToolAgent.__init__\n"
                "4. Execute it here and return the result"
            )
        elif tool_name == "calendar":
            # Placeholder response for calendar tool
            result = (
                "📅 CALENDAR TOOL (Placeholder)\n"
                "This tool would check calendar availability. To implement:\n"
                "1. Create portfolio_bot/core/tools/calendar_tool.py\n"
                "2. Integrate with Google Calendar API or similar\n"
                "3. Register the tool in ToolAgent.__init__\n"
                "4. Execute it here and return the result"
            )
        else:
            result = f"Unknown tool: {tool_name}. Available tools: email, calendar"

        logger.info(f"Tool result: {result[:50]}...")
        return {"tool_result": result}


# =============================================================================
# TOOL IMPLEMENTATION GUIDE
# =============================================================================
"""
HOW TO CREATE A TOOL
====================

1. Create a new file: portfolio_bot/core/tools/email_tool.py

2. Use the @tool decorator from LangChain:

    from langchain_core.tools import tool

    @tool
    async def send_email(
        recipient_email: str,
        subject: str,
        message: str
    ) -> str:
        '''
        Send an email to the specified recipient.

        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            message: Email body content

        Returns:
            Status message indicating success or failure
        '''
        # Your implementation here
        # Example using httpx to call an email API:
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "https://api.emailservice.com/send",
        #         json={
        #             "to": recipient_email,
        #             "subject": subject,
        #             "body": message,
        #         },
        #         headers={"Authorization": f"Bearer {API_KEY}"}
        #     )
        #     if response.status_code == 200:
        #         return f"Email sent successfully to {recipient_email}"
        #     else:
        #         return f"Failed to send email: {response.text}"

        return f"Email sent to {recipient_email}"

3. Register the tool in ToolAgent.__init__:

    from portfolio_bot.core.tools.email_tool import send_email

    self._tools = {
        "email": send_email,
    }

4. Update the run() method to execute the tool:

    if tool_name in self._tools:
        tool_func = self._tools[tool_name]
        result = await tool_func(**tool_args)
        return {"tool_result": result}


ADVANCED: USING LANGCHAIN TOOL CALLING
======================================

For more sophisticated tool use, you can let the LLM decide
which tool to call and with what arguments:

    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    # Define tools
    @tool
    def email_tool(...): ...

    @tool
    def calendar_tool(...): ...

    # Bind tools to LLM
    llm = ChatOpenAI(model="gpt-4")
    llm_with_tools = llm.bind_tools([email_tool, calendar_tool])

    # The LLM will return tool calls in its response
    response = await llm_with_tools.ainvoke(messages)

    # Execute the tool calls
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        result = await self._tools[tool_name](**tool_args)

This approach lets the LLM intelligently decide which tool to use
and extract arguments from the user's natural language query.
"""


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the tool agent (placeholder implementation).

    Run: python -m portfolio_bot.core.agents.tool_agent
    """
    import asyncio

    async def test_tool_agent():
        print("=== Testing ToolAgent (Placeholder) ===\n")

        agent = ToolAgent()

        # Test email tool
        print("--- Email Tool ---")
        state: NodeState = {
            "messages": [],
            "tool_name": "email",
            "tool_args": {"recipient": "test@example.com"},
        }
        result = await agent.run(state)
        print(result["tool_result"])
        print()

        # Test calendar tool
        print("--- Calendar Tool ---")
        state: NodeState = {
            "messages": [],
            "tool_name": "calendar",
            "tool_args": {},
        }
        result = await agent.run(state)
        print(result["tool_result"])
        print()

        # Test unknown tool
        print("--- Unknown Tool ---")
        state: NodeState = {
            "messages": [],
            "tool_name": "unknown",
            "tool_args": {},
        }
        result = await agent.run(state)
        print(result["tool_result"])

    asyncio.run(test_tool_agent())
