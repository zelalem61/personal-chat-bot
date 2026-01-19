"""
Tools Module - PLACEHOLDER FOR LEARNER IMPLEMENTATION

LEARNING NOTES:
---------------
This module is intentionally empty! Your task is to implement tools here.

Tools are functions that the chatbot can execute to interact with external
systems. In LangChain, you create tools using the @tool decorator.

WHAT ARE TOOLS?
---------------
Tools give LLMs the ability to take actions in the real world:
- Send emails
- Query databases
- Call APIs
- Interact with calendars
- Process files
- And much more!

HOW TO CREATE A TOOL
--------------------
1. Create a new file in this directory (e.g., email_tool.py)
2. Import the @tool decorator from langchain_core.tools
3. Write your function and decorate it with @tool
4. Add a clear docstring - the LLM uses this to understand when to use the tool

EXAMPLE: Email Tool (email_tool.py)
-----------------------------------
```python
from langchain_core.tools import tool
import httpx

@tool
async def send_contact_email(
    sender_name: str,
    sender_email: str,
    message: str,
) -> str:
    '''
    Send a contact email to the portfolio owner.

    Use this tool when someone wants to get in touch, send a message,
    or inquire about collaboration opportunities.

    Args:
        sender_name: Name of the person sending the email
        sender_email: Email address of the sender for replies
        message: The message content they want to send

    Returns:
        Confirmation message or error description
    '''
    # Implementation using your preferred email service
    # Examples: SendGrid, Mailjet, AWS SES, or SMTP

    # Placeholder implementation:
    print(f"Would send email from {sender_name} ({sender_email}): {message}")
    return f"Message from {sender_name} has been sent successfully!"
```

EXAMPLE: Calendar Tool (calendar_tool.py)
-----------------------------------------
```python
from langchain_core.tools import tool
from datetime import datetime

@tool
async def check_availability(
    date: str,
    duration_minutes: int = 30,
) -> str:
    '''
    Check calendar availability for a meeting.

    Use this tool when someone wants to schedule a meeting or check
    when the portfolio owner is available.

    Args:
        date: The date to check (YYYY-MM-DD format)
        duration_minutes: How long the meeting would be (default 30 min)

    Returns:
        Available time slots or message if no availability
    '''
    # Implementation using Google Calendar API or similar

    # Placeholder implementation:
    return f"Available slots on {date}: 10:00 AM, 2:00 PM, 4:00 PM"


@tool
async def schedule_meeting(
    date: str,
    time: str,
    attendee_email: str,
    subject: str,
) -> str:
    '''
    Schedule a meeting on the calendar.

    Use this tool after checking availability to book a meeting.

    Args:
        date: Meeting date (YYYY-MM-DD format)
        time: Meeting time (HH:MM format, 24-hour)
        attendee_email: Email of the person to meet with
        subject: Meeting subject/title

    Returns:
        Confirmation with meeting details
    '''
    # Implementation to create calendar event

    # Placeholder implementation:
    return f"Meeting '{subject}' scheduled for {date} at {time} with {attendee_email}"
```

REGISTERING TOOLS
-----------------
After creating your tools, register them in the ToolAgent:

1. Open portfolio_bot/core/agents/tool_agent.py
2. Import your tools at the top
3. Add them to the self._tools dictionary in __init__

Example:
```python
from portfolio_bot.core.tools.email_tool import send_contact_email
from portfolio_bot.core.tools.calendar_tool import check_availability, schedule_meeting

class ToolAgent:
    def __init__(self):
        self._tools = {
            "email": send_contact_email,
            "check_availability": check_availability,
            "schedule_meeting": schedule_meeting,
        }
```

TOOL BEST PRACTICES
-------------------
1. Clear Docstrings: The LLM reads these to decide when to use the tool
2. Typed Parameters: Use type hints for all parameters
3. Descriptive Names: Tool name should describe what it does
4. Error Handling: Return helpful error messages, don't raise exceptions
5. Async When Needed: Use async for I/O operations (API calls, etc.)

RESOURCES
---------
- LangChain Tools: https://python.langchain.com/docs/modules/tools/
- Tool Decorator: https://python.langchain.com/docs/how_to/custom_tools/
- Tool Calling: https://python.langchain.com/docs/modules/model_io/chat/function_calling/

Happy building! 🛠️
"""

# When you create tools, export them here for easy importing:
#
# from portfolio_bot.core.tools.email_tool import send_contact_email
# from portfolio_bot.core.tools.calendar_tool import check_availability, schedule_meeting
#
# __all__ = ["send_contact_email", "check_availability", "schedule_meeting"]
