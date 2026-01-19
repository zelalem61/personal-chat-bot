"""
Prompt templates for Portfolio Bot agents.

Each module contains system and human prompts for its respective agent.
Prompts are designed to be clear and educational, showing best practices
for prompt engineering.
"""

from portfolio_bot.core.prompts.router import ROUTER_SYSTEM_PROMPT, ROUTER_HUMAN_PROMPT
from portfolio_bot.core.prompts.response import RESPONSE_SYSTEM_PROMPT, RESPONSE_HUMAN_PROMPT

__all__ = [
    "ROUTER_SYSTEM_PROMPT",
    "ROUTER_HUMAN_PROMPT",
    "RESPONSE_SYSTEM_PROMPT",
    "RESPONSE_HUMAN_PROMPT",
]
