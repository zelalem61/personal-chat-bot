# Portfolio Bot Implementation Roadmap

A step-by-step guide to implementing your LangGraph multi-agent chatbot.

---

## Overview

You'll build a chatbot with this architecture:

```
START → [Router] → RAG path:    [Retriever] → [ResponseAgent] → END
                 → TOOL path:   [ToolAgent] → [ResponseAgent] → END
                 → DIRECT path: [ResponseAgent] → END
```

---

## Step 1: State Management (`core/state.py`)

**Goal:** Define the data structure that flows through your graph.

### 1.1 Create RouteType Enum

```python
class RouteType(str, Enum):
    """Routing decisions for the graph."""
    RAG = "rag"
    TOOL = "tool"
    DIRECT = "direct"
```

### 1.2 Create NodeState TypedDict

```python
class NodeState(TypedDict, total=False):
    # Chat history - uses add_messages reducer to append
    messages: Annotated[list[BaseMessage], add_messages]

    # Routing
    route_type: RouteType

    # RAG
    documents: list[dict]

    # Tools
    tool_name: Optional[str]
    tool_args: Optional[dict]
    tool_result: Optional[str]

    # Response
    final_response: Optional[str]
```

### 1.3 Create Input/Output States

```python
class InputState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class OutputState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    final_response: str
```

### 1.4 Create RouteDecision Model

```python
class RouteDecision(BaseModel):
    route_type: RouteType = Field(description="The routing decision")
    tool_name: Optional[str] = Field(default=None, description="Tool to use if route_type is TOOL")
    reasoning: str = Field(description="Why this route was chosen")
```

### Test It
```bash
python -c "from portfolio_bot.core.state import RouteType, NodeState; print('Success!')"
```

---

## Step 2: LLM Manager (`core/llm.py`)

**Goal:** Create a singleton class to manage LLM instances.

### 2.1 Create LLMManager Class

```python
class LLMManager:
    _instance = None

    def __new__(cls) -> "LLMManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config = get_config()
        self._chat_model = None
        self._embeddings = None
        self._initialized = True

    def get_chat_model(self, temperature: float = 0.7) -> ChatOpenAI:
        if self._chat_model is None or self._chat_model.temperature != temperature:
            self._chat_model = ChatOpenAI(
                model=self._config.openai_model,
                temperature=temperature,
                api_key=self._config.openai_api_key,
            )
        return self._chat_model

    def get_embeddings(self) -> OpenAIEmbeddings:
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=self._config.openai_embedding_model,
                api_key=self._config.openai_api_key,
            )
        return self._embeddings
```

### 2.2 Create Helper Function

```python
@lru_cache(maxsize=1)
def get_llm_manager() -> LLMManager:
    return LLMManager()
```

### Test It
```bash
python -c "from portfolio_bot.core.llm import get_llm_manager; print(get_llm_manager())"
```

---

## Step 3: Chain Builder (`core/chain.py`)

**Goal:** Create reusable LCEL chain patterns.

### 3.1 Create ChainBuilder Class

```python
class ChainBuilder:
    def __init__(self, temperature: float = 0.7):
        self._llm_manager = get_llm_manager()
        self._temperature = temperature

    def build_chain(self, system_prompt: str, human_prompt: str, temperature: Optional[float] = None):
        """Build a chain that returns text."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])
        llm = self._llm_manager.get_chat_model(temperature or self._temperature)
        return prompt | llm | StrOutputParser()

    def build_structured_chain(self, system_prompt: str, human_prompt: str,
                               output_model: Type[T], temperature: Optional[float] = None):
        """Build a chain that returns a Pydantic model."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])
        llm = self._llm_manager.get_chat_model(temperature or self._temperature)
        structured_llm = llm.with_structured_output(output_model)
        return prompt | structured_llm
```

### Test It
```bash
python -c "
from portfolio_bot.core.chain import ChainBuilder
chain = ChainBuilder().build_chain('You are helpful.', 'Say hi')
print('Chain created:', type(chain))
"
```

---

## Step 4: Vector Store (`core/vectorstore.py`)

**Goal:** Connect to ChromaDB for document storage and retrieval.

### 4.1 Create VectorStore Class

```python
class VectorStore:
    def __init__(self):
        self._config = get_config()
        self._llm_manager = get_llm_manager()
        self._client = None
        self._collection = None
        self._embeddings = None

    async def initialize(self):
        self._client = chromadb.HttpClient(
            host=self._config.chroma_host,
            port=self._config.chroma_port,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._config.chroma_collection_name,
        )
        self._embeddings = self._llm_manager.get_embeddings()

    async def add_documents(self, documents: list[dict], chunk: bool = True) -> int:
        all_chunks, all_ids, all_metadatas = [], [], []

        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            if chunk:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                )
                chunks = splitter.split_text(content)
                for j, chunk_text in enumerate(chunks):
                    all_chunks.append(chunk_text)
                    all_metadatas.append({**metadata, "chunk_index": j})
                    all_ids.append(f"doc_{i}_chunk_{j}")
            else:
                all_chunks.append(content)
                all_metadatas.append(metadata)
                all_ids.append(f"doc_{i}")

        embeddings = await self._embeddings.aembed_documents(all_chunks)
        self._collection.add(
            ids=all_ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas,
        )
        return len(all_chunks)

    async def similarity_search(self, query: str, k: Optional[int] = None) -> list[dict]:
        k = k or self._config.num_docs_to_retrieve
        query_embedding = await self._embeddings.aembed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if results["distances"] else 0,
                })
        return documents
```

### 4.2 Create Singleton Function

```python
_vector_store = None

async def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        await _vector_store.initialize()
    return _vector_store
```

### Test It
```bash
# First, start ChromaDB
docker-compose up -d

# Then test
python -c "
import asyncio
from portfolio_bot.core.vectorstore import VectorStore
async def test():
    vs = VectorStore()
    await vs.initialize()
    print('Connected to ChromaDB!')
asyncio.run(test())
"
```

---

## Step 5: Agents (`core/agents/`)

**Goal:** Create the processing nodes for the graph.

### 5.1 Router (`agents/router.py`)

```python
class Router:
    def __init__(self):
        self._chain = ChainBuilder(temperature=0.0).build_structured_chain(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            human_prompt=ROUTER_HUMAN_PROMPT,
            output_model=RouteDecision,
        )

    async def run(self, state: NodeState) -> dict:
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if not query:
            return {"route_type": RouteType.DIRECT}

        decision = await self._chain.ainvoke({"query": query, "context": ""})

        update = {"route_type": decision.route_type}
        if decision.route_type == RouteType.TOOL and decision.tool_name:
            update["tool_name"] = decision.tool_name
        return update
```

### 5.2 Retriever (`agents/retriever.py`)

```python
class Retriever:
    def __init__(self, num_docs: Optional[int] = None):
        self._num_docs = num_docs
        self._vector_store = None

    async def run(self, state: NodeState) -> dict:
        if self._vector_store is None:
            self._vector_store = await get_vector_store()

        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        if not query:
            return {"documents": []}

        documents = await self._vector_store.similarity_search(query, k=self._num_docs)
        return {"documents": documents}
```

### 5.3 ResponseAgent (`agents/response_agent.py`)

```python
class ResponseAgent:
    def __init__(self, owner_name: str = "Portfolio Owner"):
        self._chain = ChainBuilder(temperature=0.7).build_chain(
            system_prompt=RESPONSE_SYSTEM_PROMPT.format(owner_name=owner_name),
            human_prompt=RESPONSE_HUMAN_PROMPT,
        )

    async def run(self, state: NodeState) -> dict:
        messages = state.get("messages", [])
        documents = state.get("documents", [])
        tool_result = state.get("tool_result", "")

        # Get query
        query = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break

        # Format documents
        context = "\n".join([doc["content"] for doc in documents]) or "No context"

        response = await self._chain.ainvoke({
            "query": query,
            "context": context,
            "tool_results": tool_result or "No tools used",
            "conversation_history": "",
        })

        return {
            "messages": [AIMessage(content=response)],
            "final_response": response,
        }
```

---

## Step 6: Graph (`core/graph.py`)

**Goal:** Connect all agents into a working graph.

### 6.1 Create Graph Function

```python
def create_graph():
    graph = StateGraph(NodeState, input=InputState, output=OutputState)

    # Initialize agents
    router = Router()
    retriever = Retriever()
    response_agent = ResponseAgent(owner_name="Your Name")
    tool_agent = ToolAgent()

    # Add nodes
    graph.add_node("router", router.run)
    graph.add_node("retriever", retriever.run)
    graph.add_node("response_agent", response_agent.run)
    graph.add_node("tool_agent", tool_agent.run)

    # Add edges
    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router",
        lambda state: state.get("route_type", RouteType.DIRECT).value,
        {
            "rag": "retriever",
            "tool": "tool_agent",
            "direct": "response_agent",
        },
    )
    graph.add_edge("retriever", "response_agent")
    graph.add_edge("tool_agent", "response_agent")
    graph.add_edge("response_agent", END)

    return graph.compile()
```

### 6.2 Create PortfolioBot Class

```python
class PortfolioBot:
    def __init__(self):
        self._graph = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        from portfolio_bot.core.vectorstore import get_vector_store
        await get_vector_store()
        self._graph = create_graph()
        self._initialized = True

    async def chat(self, message: str, thread_id: str = "default") -> str:
        if not self._initialized:
            raise RuntimeError("Not initialized")

        from langchain_core.messages import HumanMessage
        input_state = {"messages": [HumanMessage(content=message)]}
        result = await self._graph.ainvoke(input_state)
        return result.get("final_response", "No response")
```

### Test It
```bash
python -c "
import asyncio
from portfolio_bot.core.graph import PortfolioBot
async def test():
    bot = PortfolioBot()
    await bot.initialize()
    response = await bot.chat('Hello!')
    print('Response:', response)
asyncio.run(test())
"
```

---

## Step 7: Tools (Optional) (`core/tools/`)

**Goal:** Add custom tools like email and calendar.

### 7.1 Create Email Tool (`core/tools/email_tool.py`)

```python
from langchain_core.tools import tool

@tool
async def send_email(recipient: str, subject: str, message: str) -> str:
    """Send an email to the specified recipient."""
    # Your implementation here (SendGrid, SMTP, etc.)
    return f"Email sent to {recipient}"
```

### 7.2 Register in ToolAgent

```python
# In tool_agent.py
from portfolio_bot.core.tools.email_tool import send_email

class ToolAgent:
    def __init__(self):
        self._tools = {
            "email": send_email,
        }

    async def run(self, state: NodeState) -> dict:
        tool_name = state.get("tool_name")
        if tool_name in self._tools:
            result = await self._tools[tool_name]()
            return {"tool_result": result}
        return {"tool_result": f"Unknown tool: {tool_name}"}
```

---

## Step 8: API (`api/`)

**Goal:** Serve the bot via FastAPI.

The API files are already implemented. Just make sure your graph works, then:

```bash
python -m portfolio_bot.api.main
```

Visit http://localhost:8004/docs for the Swagger UI.

---

## Testing Checklist

- [ ] Step 1: `from portfolio_bot.core.state import RouteType, NodeState`
- [ ] Step 2: `from portfolio_bot.core.llm import get_llm_manager`
- [ ] Step 3: `from portfolio_bot.core.chain import ChainBuilder`
- [ ] Step 4: ChromaDB running, VectorStore connects
- [ ] Step 5: Each agent can be instantiated
- [ ] Step 6: `PortfolioBot().chat("Hello")` works
- [ ] Step 7: Tools return expected results (optional)
- [ ] Step 8: API responds at `/api/chat`

---

## Debugging Tips

1. **Import errors**: Check that all `__init__.py` files export the classes
2. **ChromaDB connection**: Ensure `docker-compose up -d` is running
3. **API key errors**: Check `.env` has `OPENAI_API_KEY` set
4. **Graph errors**: Make sure all edges connect properly

Good luck! 🚀
