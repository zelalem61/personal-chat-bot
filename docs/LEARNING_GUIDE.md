# Portfolio Bot Learning Guide

A step-by-step guide to understanding and extending the Portfolio Bot.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Part 1: Understanding State](#part-1-understanding-state)
4. [Part 2: Building Chains with LCEL](#part-2-building-chains-with-lcel)
5. [Part 3: Vector Store and RAG](#part-3-vector-store-and-rag)
6. [Part 4: The LangGraph](#part-4-the-langgraph)
7. [Part 5: Agents Deep Dive](#part-5-agents-deep-dive)
8. [Part 6: Building Tools](#part-6-building-tools)
9. [Part 7: The API Layer](#part-7-the-api-layer)
10. [Exercises](#exercises)
11. [Next Steps](#next-steps)

---

## Introduction

This project teaches you how to build multi-agent LLM applications using LangGraph. By the end, you'll understand:

- How state flows through a graph of agents
- How to use RAG to ground LLM responses in documents
- How to create tools that extend LLM capabilities
- How to serve your bot as an API

**The Architecture:**

```
User Message
     │
     ▼
┌─────────┐
│ Router  │ ─── "What kind of question is this?"
└────┬────┘
     │
     ├─── RAG ──────► [Retriever] ──► [Response Agent]
     │                    │
     │                 Find docs
     │
     ├─── TOOL ─────► [Tool Agent] ──► [Response Agent]
     │                    │
     │                Execute tool
     │
     └─── DIRECT ────────────────────► [Response Agent]
                                            │
                                       Generate response
                                            │
                                            ▼
                                      Bot Response
```

---

## Prerequisites

Before starting, make sure you have:

1. **Python 3.11+** installed
2. **Docker** installed and running
3. **OpenAI API key** (get one at https://platform.openai.com/api-keys)
4. Basic familiarity with:
   - Python async/await
   - Type hints
   - Basic LLM concepts

---

## Part 1: Understanding State

**File:** `portfolio_bot/core/state.py`

### What is State?

State is the data that flows through your graph. Think of it as a backpack that each agent can look into, use, and add things to.

```python
class NodeState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]  # Chat history
    route_type: RouteType                                  # Where to go
    documents: list[dict]                                  # Retrieved docs
    tool_result: Optional[str]                            # Tool output
    final_response: Optional[str]                         # Bot's answer
```

### Key Concept: Reducers

Reducers define HOW state fields are updated. This is crucial!

**Without reducer (default):** New value replaces old value
```python
# State has: {"count": 5}
# Node returns: {"count": 10}
# Result: {"count": 10}  # Replaced!
```

**With add_messages reducer:** New messages are appended
```python
# State has: {"messages": [HumanMessage("Hi")]}
# Node returns: {"messages": [AIMessage("Hello!")]}
# Result: {"messages": [HumanMessage("Hi"), AIMessage("Hello!")]}  # Appended!
```

### Try It!

```bash
python -m portfolio_bot.core.state
```

This runs the example code at the bottom of state.py.

### Exercises

1. Add a new field `query_count: int` to track how many queries have been made
2. What reducer would you use for this field?
3. How would a node update this field?

---

## Part 2: Building Chains with LCEL

**File:** `portfolio_bot/core/chain.py`

### What is LCEL?

LangChain Expression Language (LCEL) is a way to compose LLM pipelines using the pipe operator (`|`):

```python
chain = prompt | llm | parser
```

This reads as: "Take input, fill in the prompt, send to LLM, parse the output."

### Building a Simple Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])

# 2. Create LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# 3. Create parser
parser = StrOutputParser()

# 4. Compose the chain
chain = prompt | llm | parser

# 5. Use it!
result = await chain.ainvoke({"question": "What is Python?"})
```

### Structured Output

Instead of getting free-form text, you can get a Pydantic model:

```python
from pydantic import BaseModel

class Sentiment(BaseModel):
    label: str  # positive, negative, neutral
    confidence: float  # 0.0 to 1.0

# Use with_structured_output
structured_llm = llm.with_structured_output(Sentiment)
chain = prompt | structured_llm

result = await chain.ainvoke({"text": "I love this product!"})
print(result.label)      # "positive"
print(result.confidence) # 0.95
```

### Try It!

```bash
python -m portfolio_bot.core.chain
```

### Exercises

1. Create a chain that summarizes text in exactly 3 bullet points
2. Create a structured output model for extracting contact information
3. What happens if you remove the output parser from a chain?

---

## Part 3: Vector Store and RAG

**File:** `portfolio_bot/core/vectorstore.py`

### What is RAG?

RAG = Retrieval-Augmented Generation

Instead of asking the LLM to answer from its training data, we:
1. Find relevant documents from our database
2. Pass those documents to the LLM as context
3. Ask the LLM to answer based on that context

This grounds the LLM's responses in your specific data.

### How Embeddings Work

Text is converted to vectors (arrays of numbers) that capture meaning:

```
"Python is great" → [0.12, -0.34, 0.56, ...]  # 1536 numbers
"I love coding"   → [0.11, -0.35, 0.58, ...]  # Similar vector!
"The sky is blue" → [0.89, 0.12, -0.45, ...]  # Different vector
```

Similar texts have similar vectors. We use this for search!

### The RAG Process

```
1. INDEXING (done once)
   Document → Chunks → Embeddings → Store in ChromaDB

2. RETRIEVAL (every query)
   Query → Embedding → Find similar vectors → Return chunks

3. GENERATION
   Query + Retrieved chunks → LLM → Answer
```

### Try It!

```bash
# Make sure ChromaDB is running
docker-compose up -d

# Test the vector store
python -m portfolio_bot.core.vectorstore
```

### Exercises

1. What happens if you search with a chunk_size of 100 vs 2000?
2. How does the number of retrieved documents affect response quality?
3. Try searching for something not in the documents. What happens?

---

## Part 4: The LangGraph

**File:** `portfolio_bot/core/graph.py`

### What is LangGraph?

LangGraph is a framework for building stateful, multi-step LLM applications. It models your application as a graph where:

- **Nodes** are processing steps (your agents)
- **Edges** connect nodes (define the flow)
- **State** flows through the graph

### Building the Graph

```python
from langgraph.graph import StateGraph, START, END

# 1. Create the graph
graph = StateGraph(NodeState)

# 2. Add nodes
graph.add_node("router", router.run)
graph.add_node("retriever", retriever.run)
graph.add_node("response_agent", response_agent.run)

# 3. Add edges
graph.add_edge(START, "router")

# 4. Add conditional edges (routing)
graph.add_conditional_edges(
    "router",
    lambda state: state["route_type"].value,
    {
        "rag": "retriever",
        "direct": "response_agent",
    }
)

# 5. Compile
compiled = graph.compile()
```

### Conditional Routing

The router decides where to go based on the query:

```python
def get_route(state):
    route_type = state["route_type"]
    if route_type == RouteType.RAG:
        return "retriever"
    elif route_type == RouteType.TOOL:
        return "tool_agent"
    else:
        return "response_agent"
```

### Try It!

```bash
# Visualize the graph
python scripts/visualize_graph.py

# Test the bot
python -m portfolio_bot.core.graph
```

### Exercises

1. Add a new route type "SMALLTALK" for casual conversation
2. Add a new node that logs all messages before the router
3. What happens if you create a cycle in the graph?

---

## Part 5: Agents Deep Dive

**Files:** `portfolio_bot/core/agents/`

### What is an Agent?

In this context, an "agent" is a node in the graph - a function that:
1. Receives the current state
2. Does some processing (often involving an LLM)
3. Returns a state update

### Router Agent

**File:** `agents/router.py`

The router classifies queries:

```python
async def run(self, state: NodeState) -> dict:
    # Get the query
    query = state["messages"][-1].content

    # Classify it
    decision = await self._chain.ainvoke({"query": query})

    # Return state update
    return {
        "route_type": decision.route_type,
        "tool_name": decision.tool_name,
    }
```

### Retriever Agent

**File:** `agents/retriever.py`

Finds relevant documents:

```python
async def run(self, state: NodeState) -> dict:
    query = state["messages"][-1].content
    documents = await self._vector_store.similarity_search(query)
    return {"documents": documents}
```

### Response Agent

**File:** `agents/response_agent.py`

Generates the final response:

```python
async def run(self, state: NodeState) -> dict:
    query = state["messages"][-1].content
    context = format_documents(state["documents"])

    response = await self._chain.ainvoke({
        "query": query,
        "context": context,
    })

    return {
        "messages": [AIMessage(content=response)],
        "final_response": response,
    }
```

### Try It!

```bash
# Test each agent individually
python -m portfolio_bot.core.agents.router
python -m portfolio_bot.core.agents.retriever
python -m portfolio_bot.core.agents.response_agent
```

### Exercises

1. Modify the router to also detect the language of the query
2. Add logging to see how long each agent takes
3. What would happen if an agent raises an exception?

---

## Part 6: Building Tools

**File:** `portfolio_bot/core/tools/__init__.py`

### Your Challenge!

The tool system is intentionally incomplete. Your task is to implement tools!

### Step 1: Create a Tool

Create `portfolio_bot/core/tools/email_tool.py`:

```python
from langchain_core.tools import tool

@tool
async def send_contact_email(
    sender_name: str,
    sender_email: str,
    message: str,
) -> str:
    """
    Send a contact email to the portfolio owner.

    Use this when someone wants to get in touch or
    send a message.

    Args:
        sender_name: Name of the person
        sender_email: Their email for replies
        message: The message content

    Returns:
        Confirmation message
    """
    # For now, just simulate
    print(f"Email from {sender_name}: {message}")
    return f"Message from {sender_name} sent successfully!"
```

### Step 2: Register the Tool

Update `agents/tool_agent.py`:

```python
from portfolio_bot.core.tools.email_tool import send_contact_email

class ToolAgent:
    def __init__(self):
        self._tools = {
            "email": send_contact_email,
        }

    async def run(self, state: NodeState) -> dict:
        tool_name = state.get("tool_name")
        if tool_name in self._tools:
            result = await self._tools[tool_name]()
            return {"tool_result": result}
        return {"tool_result": "Unknown tool"}
```

### Step 3: Test It

```bash
python -m portfolio_bot.core.agents.tool_agent
```

### Exercises

1. Implement the calendar_tool with availability checking
2. Add input validation to your tools
3. Handle tool errors gracefully

---

## Part 7: The API Layer

**Files:** `portfolio_bot/api/`

### FastAPI Basics

FastAPI provides the HTTP interface:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await bot.chat(request.message)
    return {"response": response}
```

### Lifespan Management

Initialize resources at startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    bot = PortfolioBot()
    await bot.initialize()
    app.state.bot = bot

    yield  # App runs

    # Shutdown
    # Cleanup code here
```

### Try It!

```bash
# Start the server
python -m portfolio_bot.api.main

# Open docs
open http://localhost:8004/docs

# Test with curl
curl -X POST http://localhost:8004/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your skills"}'
```

### Exercises

1. Add rate limiting to the chat endpoint
2. Add request/response logging middleware
3. Add authentication (API key or JWT)

---

## Exercises

### Beginner

1. **Customize Prompts**: Change the system prompt in `response.py` to give your bot a unique personality
2. **Add Logging**: Add detailed logging to see exactly what each agent does
3. **Error Messages**: Improve error messages when something goes wrong

### Intermediate

4. **Conversation Memory**: Add checkpointing to remember previous conversations
5. **Query Rewriting**: Add a node that rewrites queries for better retrieval
6. **Grading**: Add a node that evaluates if retrieved documents are relevant

### Advanced

7. **Streaming**: Implement true streaming responses (token by token)
8. **Multiple Collections**: Support different document collections for different topics
9. **Tool Chaining**: Allow tools to call other tools

---

## Next Steps

### Learn More
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Expression Language](https://python.langchain.com/docs/expression_language/)
- [RAG Deep Dive](https://python.langchain.com/docs/tutorials/rag/)

### Extend the Bot
- Add conversation memory with PostgreSQL checkpointing
- Implement more sophisticated routing
- Add user authentication and multi-tenancy
- Deploy to production

### Study the Production Version
This project is based on [Algorise-Lyntel](https://github.com/Algorise-Ltd/algorise-lyntel), which includes:
- 15+ specialized agents
- Multiple LLM providers with fallbacks
- Query enrichment and rewriting
- Parallel processing with fan-out/fan-in

---

## Troubleshooting

### ChromaDB Connection Failed
```
docker-compose up -d
docker-compose logs chromadb
```

### OpenAI API Errors
- Check your API key is set in `.env`
- Check you have credits in your account

### Import Errors
```bash
# Make sure you're in the project directory
cd chatbot
# Make sure dependencies are installed
pip install -r requirements.txt
```

### Graph Won't Compile
- Check all edges lead somewhere (no dangling nodes)
- Check conditional edges have all required routes

---

Happy learning! 🚀
