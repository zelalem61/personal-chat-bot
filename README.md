# Portfolio Bot - LangGraph Learning Project

A simplified multi-agent chatbot that teaches LangGraph concepts through building a personal portfolio assistant.

## What You'll Learn

This project teaches you:
- **LangGraph** - Building stateful multi-agent applications
- **RAG (Retrieval-Augmented Generation)** - Using documents to enhance LLM responses
- **LCEL (LangChain Expression Language)** - Composing LLM chains
- **Structured Output** - Getting LLMs to return typed data
- **Tool Calling** - Extending LLMs with external capabilities
- **FastAPI** - Serving your bot as an API

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker (for ChromaDB)
- OpenAI API key

### 2. Setup

```bash
# Clone/copy this project
cd chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
```

### 3. Start ChromaDB

```bash
docker-compose up -d
```

### 4. Fill In Your Portfolio

Edit `portfolio_bot/data/portfolio.md` with your information.

### 5. Ingest Documents

```bash
python scripts/ingest_documents.py
```

### 6. Run the Bot

```bash
python -m portfolio_bot.api.main
```

Open http://localhost:8004/docs to see the API documentation.

### 7. Test It

```bash
# Using curl
curl -X POST http://localhost:8004/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your experience"}'
```

## Project Structure

```
chatbot/
├── portfolio_bot/
│   ├── configs/          # Configuration
│   ├── core/
│   │   ├── agents/       # LangGraph nodes (router, retriever, etc.)
│   │   ├── prompts/      # LLM prompt templates
│   │   ├── tools/        # Tool implementations (for you to build!)
│   │   ├── graph.py      # The LangGraph StateGraph
│   │   ├── state.py      # State definitions
│   │   └── vectorstore.py # ChromaDB integration
│   ├── api/              # FastAPI application
│   ├── services/         # Business logic
│   └── data/             # Your portfolio document
├── scripts/              # Utility scripts
├── tests/                # Test files
└── docs/                 # Learning documentation
```

## The Graph Architecture

```
START
  │
  ▼
[router] ──────► Classifies query: RAG, TOOL, or DIRECT
  │
  ├──► RAG:     [retriever] ──► [response_agent] ──► END
  │
  ├──► TOOL:    [tool_agent] ──► [response_agent] ──► END
  │
  └──► DIRECT:  [response_agent] ──► END
```

## Your Learning Tasks

### 1. Understand the Graph (Start Here!)
- Read `core/state.py` - Understand state and reducers
- Read `core/graph.py` - See how nodes connect
- Run `python scripts/visualize_graph.py` to see the diagram

### 2. Experiment with Prompts
- Modify prompts in `core/prompts/`
- See how different prompts affect responses

### 3. Implement Tools (Challenge!)
- Open `core/tools/__init__.py` for instructions
- Create `email_tool.py` to send contact emails
- Create `calendar_tool.py` to check availability
- Wire them up in `core/agents/tool_agent.py`

### 4. Add Features
- Add conversation memory (checkpointing)
- Add streaming responses
- Add more routes (e.g., smalltalk, unknown)

## Key Files to Study

| File | What It Teaches |
|------|-----------------|
| `core/state.py` | TypedDict, reducers, state management |
| `core/graph.py` | StateGraph, nodes, edges, routing |
| `core/chain.py` | LCEL chains, structured output |
| `core/vectorstore.py` | ChromaDB, embeddings, RAG |
| `core/agents/router.py` | Query classification with structured output |
| `api/main.py` | FastAPI lifespan, dependency injection |

## Useful Commands

```bash
# Start ChromaDB
docker-compose up -d

# Stop ChromaDB
docker-compose down

# Re-ingest documents
python scripts/ingest_documents.py --clear

# Visualize the graph
python scripts/visualize_graph.py

# Run the API server
python -m portfolio_bot.api.main

# Test individual modules
python -m portfolio_bot.core.state
python -m portfolio_bot.core.llm
python -m portfolio_bot.core.vectorstore
python -m portfolio_bot.core.agents.router
```

## Next Steps

1. Read `docs/LEARNING_GUIDE.md` for a detailed walkthrough
2. Study the code in order (state → chain → agents → graph)
3. Implement the tools
4. Customize for your portfolio
5. Deploy it!

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Based On

This project is a simplified version of [Algorise-Lyntel](https://github.com/Algorise-Ltd/algorise-lyntel), a production multi-agent RAG chatbot. The production version includes:
- 15+ specialized agents
- Multiple LLM providers with fallbacks
- Conversation checkpointing with PostgreSQL
- Celery for async processing
- Advanced routing and query enrichment

Happy learning!
