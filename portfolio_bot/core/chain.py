"""
Chain Builder - LCEL Chain Construction

LEARNING NOTES:
---------------
LangChain Expression Language (LCEL) is a declarative way to compose
LLM pipelines. The key concept is the pipe operator (|) which chains
components together:

    prompt | llm | output_parser

This creates a pipeline where:
1. Input goes into the prompt template
2. Formatted prompt goes to the LLM
3. LLM output goes through the parser

KEY CONCEPTS:
-------------
1. PROMPT TEMPLATES: Templates with variables that get filled in
   - ChatPromptTemplate: Creates a chat-style prompt with roles

2. THE PIPE OPERATOR (|): Chains components together
   - Each component's output becomes the next component's input
   - This is the core of LCEL

3. OUTPUT PARSERS: Transform LLM output into structured data
   - StrOutputParser: Just returns the text
   - PydanticOutputParser: Parses into a Pydantic model

4. STRUCTURED OUTPUT: Getting LLMs to return specific formats
   - with_structured_output(): Makes LLM return a Pydantic model
   - Uses function calling under the hood

WHAT YOU'LL LEARN:
- Building LCEL chains
- ChatPromptTemplate usage
- Structured output with Pydantic
- Chain composition patterns
"""

from typing import Optional, Type, TypeVar

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from portfolio_bot.core.llm import get_llm_manager
from portfolio_bot.logs.logger import get_logger

logger = get_logger(__name__)

# Type variable for generic structured output
T = TypeVar("T", bound=BaseModel)


class ChainBuilder:
    """
    Builder for creating LCEL chains.

    This class provides a simplified interface for creating common
    chain patterns used in the portfolio bot.

    Usage:
        # Simple chain that returns text
        chain = ChainBuilder().build_chain(
            system_prompt="You are a helpful assistant.",
            human_prompt="Answer this: {question}"
        )
        result = await chain.ainvoke({"question": "What is Python?"})

        # Chain with structured output
        chain = ChainBuilder().build_structured_chain(
            system_prompt="Classify this query.",
            human_prompt="{query}",
            output_model=ClassificationResult
        )
        result = await chain.ainvoke({"query": "Tell me about your experience"})
        # result is a ClassificationResult instance
    """

    def __init__(self, temperature: float = 0.7):
        """
        Initialize the chain builder.

        Args:
            temperature: Default temperature for LLM calls.
        """
        self._llm_manager = get_llm_manager()
        self._temperature = temperature

    def build_chain(
        self,
        system_prompt: str,
        human_prompt: str,
        temperature: Optional[float] = None,
    ):
        """
        Build a simple chain that returns text.

        Args:
            system_prompt: The system message (instructions for the LLM).
            human_prompt: The human message template with {variables}.
            temperature: Override default temperature.

        Returns:
            A runnable chain that takes a dict and returns a string.

        LEARNING NOTE: This creates the classic LCEL pattern:
            prompt | llm | parser

        The prompt template has placeholders like {question} that get
        filled in when you call chain.invoke({"question": "..."})

        Example:
            chain = builder.build_chain(
                system_prompt="You are a pirate.",
                human_prompt="Respond to: {message}"
            )
            result = chain.invoke({"message": "Hello"})
            # Result: "Ahoy there, matey!"
        """
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])

        # Get the LLM
        llm = self._llm_manager.get_chat_model(
            temperature=temperature or self._temperature
        )

        # Build the chain: prompt | llm | output_parser
        chain = prompt | llm | StrOutputParser()

        logger.debug("Built text chain")
        return chain

    def build_structured_chain(
        self,
        system_prompt: str,
        human_prompt: str,
        output_model: Type[T],
        temperature: Optional[float] = None,
    ):
        """
        Build a chain that returns a structured Pydantic model.

        Args:
            system_prompt: The system message.
            human_prompt: The human message template.
            output_model: Pydantic model class for the output.
            temperature: Override default temperature.

        Returns:
            A runnable chain that takes a dict and returns an instance
            of output_model.

        LEARNING NOTE: This uses LLM "function calling" or "tool use"
        under the hood. The LLM is instructed to return data matching
        the Pydantic model's schema, which is then validated and parsed.

        Benefits of structured output:
        1. Type safety - you get a proper Python object
        2. Validation - Pydantic validates the LLM's response
        3. Reliability - less parsing errors than regex/string matching

        Example:
            class Sentiment(BaseModel):
                label: str
                confidence: float

            chain = builder.build_structured_chain(
                system_prompt="Analyze sentiment.",
                human_prompt="{text}",
                output_model=Sentiment
            )
            result = chain.invoke({"text": "I love this!"})
            # result.label = "positive", result.confidence = 0.95
        """
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])

        # Get the LLM with structured output capability
        llm = self._llm_manager.get_chat_model(
            temperature=temperature or self._temperature
        )

        # Add structured output - this uses function calling
        structured_llm = llm.with_structured_output(output_model)

        # Build the chain: prompt | structured_llm
        # Note: No output parser needed - structured_llm already returns the model
        chain = prompt | structured_llm

        logger.debug(f"Built structured chain with output model: {output_model.__name__}")
        return chain

    def build_chat_chain(
        self,
        system_prompt: str,
        temperature: Optional[float] = None,
    ):
        """
        Build a chain for multi-turn chat with message history.

        Args:
            system_prompt: The system message.
            temperature: Override default temperature.

        Returns:
            A runnable chain that takes {"messages": [...]} and returns text.

        LEARNING NOTE: This chain uses MessagesPlaceholder to accept
        a full conversation history. The LLM sees all previous messages,
        allowing for context-aware responses.

        Example:
            chain = builder.build_chat_chain("You are helpful.")
            result = chain.invoke({
                "messages": [
                    HumanMessage(content="My name is Alice"),
                    AIMessage(content="Nice to meet you, Alice!"),
                    HumanMessage(content="What's my name?"),
                ]
            })
            # Result: "Your name is Alice!"
        """
        from langchain_core.prompts import MessagesPlaceholder

        # Create prompt with message history placeholder
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # Get the LLM
        llm = self._llm_manager.get_chat_model(
            temperature=temperature or self._temperature
        )

        # Build the chain
        chain = prompt | llm | StrOutputParser()

        logger.debug("Built chat chain with message history")
        return chain


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Test the chain builder.

    Run: python -m portfolio_bot.core.chain
    """
    import asyncio
    from pydantic import BaseModel, Field

    # Define a test output model
    class QueryType(BaseModel):
        category: str = Field(description="Category: greeting, question, or command")
        confidence: float = Field(description="Confidence score 0-1")

    async def test_chains():
        builder = ChainBuilder(temperature=0.3)

        # Test simple chain
        print("=== Testing Simple Chain ===")
        simple_chain = builder.build_chain(
            system_prompt="You are a helpful assistant. Be concise.",
            human_prompt="Question: {question}\nAnswer:",
        )
        result = await simple_chain.ainvoke({"question": "What is 2+2?"})
        print(f"Simple chain result: {result}")

        # Test structured chain
        print("\n=== Testing Structured Chain ===")
        structured_chain = builder.build_structured_chain(
            system_prompt="Classify the user's query type.",
            human_prompt="Query: {query}",
            output_model=QueryType,
            temperature=0.0,  # Low temperature for consistent classification
        )
        result = await structured_chain.ainvoke({"query": "Hello there!"})
        print(f"Structured chain result: {result}")
        print(f"  Category: {result.category}")
        print(f"  Confidence: {result.confidence}")

        # Test chat chain
        print("\n=== Testing Chat Chain ===")
        from langchain_core.messages import HumanMessage, AIMessage

        chat_chain = builder.build_chat_chain(
            system_prompt="You are a friendly assistant. Keep responses brief."
        )
        result = await chat_chain.ainvoke({
            "messages": [
                HumanMessage(content="Hi, I'm learning about AI!"),
                AIMessage(content="That's great! AI is a fascinating field."),
                HumanMessage(content="What should I learn first?"),
            ]
        })
        print(f"Chat chain result: {result}")

    asyncio.run(test_chains())
