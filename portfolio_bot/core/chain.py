"""
Chain Builder - LCEL Chain Construction

LEARNING NOTES:
---------------
LangChain Expression Language (LCEL) composes LLM pipelines using the
pipe operator (|):

    prompt | llm | output_parser

KEY CONCEPTS:
-------------
1. PROMPT TEMPLATES: ChatPromptTemplate with system and human messages
2. THE PIPE OPERATOR (|): Chains components together
3. OUTPUT PARSERS: StrOutputParser for text, with_structured_output for Pydantic
4. STRUCTURED OUTPUT: LLM returns a validated Pydantic model

YOUR TASK: (See roadmap.md Step 3)
----------
1. Implement ChainBuilder class with __init__(temperature)
2. Add build_chain() for simple text chains: prompt | llm | StrOutputParser()
3. Add build_structured_chain() for Pydantic output: prompt | llm.with_structured_output(model)
"""

from typing import Optional, Type, TypeVar

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from portfolio_bot.core.llm import get_llm_manager
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


# =============================================================================
# TODO: Implement ChainBuilder Class
# =============================================================================
# class ChainBuilder:
#     def __init__(self, temperature: float = 0.7):
#         self._llm_manager = get_llm_manager()
#         self._temperature = temperature
#
#     def build_chain(self, system_prompt: str, human_prompt: str, temperature: Optional[float] = None):
#         # 1. Create ChatPromptTemplate.from_messages([("system", ...), ("human", ...)])
#         # 2. Get LLM from llm_manager
#         # 3. Return: prompt | llm | StrOutputParser()
#         pass
#
#     def build_structured_chain(self, system_prompt: str, human_prompt: str,
#                                output_model: Type[T], temperature: Optional[float] = None):
#         # 1. Create prompt template
#         # 2. Get LLM and call llm.with_structured_output(output_model)
#         # 3. Return: prompt | structured_llm
#         pass
pass
