# Prime (Portfolio Bot)
> Understand the current state of the personal portfolio chat bot project and what work is in progress.

## Your Task

You are priming yourself to work effectively on **this repo**:
- A LangGraph‑powered **portfolio chatbot** in `portfolio_bot/`
- Backed by **ChromaDB** (via Docker Compose) for RAG
- Exposed via **FastAPI** with a built‑in chat UI at `/chat`

### 1. Analyze Recent Work

Use git to understand what has been happening:
- `git log --oneline -10` – last 10 commits
- `git diff --stat HEAD~5..HEAD` – summary of recent file changes
- `git diff HEAD~5..HEAD` – skim changes for intent (not every line)

From this, identify:
- What feature(s) or learning tasks are being worked on (e.g., tools, agents, UI, deployment)
- Which parts of the system are changing:
  - `portfolio_bot/core/**` – state, graph, agents, tools, vectorstore
  - `portfolio_bot/api/**` – FastAPI API + static chat UI
  - `scripts/**` – ingestion/visualization/utilities
  - `docs/**`, `roadmap.md` – learning docs and implementation plan

### 2. Read Core Specs & Learning Docs

Focus on the sources of truth for this project:
- `roadmap.md` – step‑by‑step implementation roadmap
- `docs/LEARNING_GUIDE.md` – detailed learning walkthrough
- Key inline "YOUR TASK" blocks inside:
  - `portfolio_bot/core/state.py`
  - `portfolio_bot/core/graph.py`
  - `portfolio_bot/core/agents/*.py`
  - `portfolio_bot/core/vectorstore.py`
  - `portfolio_bot/core/tools/__init__.py`
  - `portfolio_bot/api/main.py`

Understand:
- The overall architecture (router → retriever/tool_agent → response_agent)
- How RAG is wired (vectorstore + ChromaDB + `portfolio_bot/data/portfolio.md`)
- How the API and UI expose the bot (`/api/chat`, `/chat`, `/static/**`)

### 3. Map Current Changes to the Roadmap

Using what you learned from git + docs:
- Determine **which roadmap step(s)** the recent work corresponds to
- For each changed area, answer:
  - Is this implementing a roadmap step, fixing a bug, or adding UX polish?
  - Is the work complete, or are there obvious TODOs left?
  - Are there follow‑up items implied (e.g., tests, docs, deployment)?

If relevant, also:
- Check `scripts/ingest_documents.py` usage (RAG ingestion flow)
- Check `docker-compose.yml` to see how ChromaDB is expected to run

### 4. Provide a Focused Summary

After analysis, summarize:
- **Current feature/theme** being worked on (e.g., “deployment and chat UI for portfolio bot”)
- **Files and modules most affected**, grouped by area (core, api, scripts, docs)
- **What appears complete vs. in‑progress**, including any obvious TODO comments
- **How the changes impact the portfolio bot** from a client’s perspective
- **Next logical steps** to continue the work, tied back to `roadmap.md`

Be ready to continue working on this project with full context of:
- The LangGraph architecture
- The RAG setup and ingestion story
- The FastAPI API + chat UI
- The intended learning path and remaining roadmap items.