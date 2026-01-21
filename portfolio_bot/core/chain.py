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
# ChainBuilder Class
# =============================================================================


class ChainBuilder:
    """
    Helper for constructing LCEL chains with a shared LLM manager.

    Provides:
    - `build_chain` for simple text output chains
    - `build_structured_chain` for Pydantic structured output
    """

    def __init__(self, temperature: float = 0.7):
        self._llm_manager = get_llm_manager()
        self._temperature = temperature

    def _get_llm(self, temperature: Optional[float] = None):
        """Get a chat model with the requested temperature (or default)."""
        temp = self._temperature if temperature is None else temperature
        return self._llm_manager.get_chat_model(temperature=temp)

    def build_chain(
        self,
        system_prompt: str,
        human_prompt: str,
        temperature: Optional[float] = None,
    ):
        """
        Build a simple text chain: prompt | llm | StrOutputParser().
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )

        llm = self._get_llm(temperature=temperature)

        chain = prompt | llm | StrOutputParser()
        logger.info("Built text chain with temperature=%s", temperature or self._temperature)
        return chain

    def build_structured_chain(
        self,
        system_prompt: str,
        human_prompt: str,
        output_model: Type[T],
        temperature: Optional[float] = None,
    ):
        """
        Build a structured-output chain: prompt | llm.with_structured_output(model).
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )

        llm = self._get_llm(temperature=temperature)
        structured_llm = llm.with_structured_output(output_model)

        chain = prompt | structured_llm
        logger.info(
            "Built structured chain with model=%s and temperature=%s",
            output_model.__name__,
            temperature or self._temperature,
        )
        return chain

