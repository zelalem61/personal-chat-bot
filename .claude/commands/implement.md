# Implement Command (Portfolio Bot)

Execute a specification file and implement the plan **for this personal portfolio chat bot project**.

**Usage**: `/implement docs/path-or-roadmap-section.md`

Typical specs for this repo live in:
- `roadmap.md`
- `docs/LEARNING_GUIDE.md`
- Inline "YOUR TASK" blocks in files under `portfolio_bot/`

## Instructions

You will:
1. Read the specification file or section provided
2. Understand how it fits into the existing Portfolio Bot architecture
3. Think carefully about the implementation plan
4. Execute all steps in order
5. Report what was completed and how it affects the bot

## Implementation Process

### Phase 1: Read & Understand
- Read the entire specification
- Identify which part of the system it touches:
  - `portfolio_bot/core/**` (graph, agents, tools, vectorstore)
  - `portfolio_bot/api/**` (FastAPI API + chat UI)
  - `scripts/**` (ingestion, visualization)
- Understand goals, constraints, and any learning notes in comments
- Review all steps in the plan and identify dependencies and order

### Phase 2: Execute Plan
- Follow the plan exactly as written
- Execute steps in order (top to bottom)
- Prefer small, focused changes in:
  - Core graph/agents behavior
  - Tools and vectorstore behavior
  - API routes and chat UI (`/chat`, `/static/**`)
- Don't skip steps or make assumptions
- Track progress using the TodoWrite tool

### Phase 3: Validation
- Run all validation commands specified in the spec or roadmap, e.g.:
  - `python scripts/ingest_documents.py`
  - `python -m portfolio_bot.api.main` (local manual test)
- Verify:
  - Bot can answer a few sample portfolio questions via `/api/chat`
  - Chat UI at `/chat` still works end‑to‑end
- Ensure quality standards are met (no obvious regressions, clean logs)

### Phase 4: Report
- Summarize work completed in terms of:
  - Bot behavior changes (routing, RAG quality, tools, UI)
  - Developer experience improvements (scripts, docs)
- List all files changed (grouped by area: core, api, scripts, docs)
- Note any deviations from the original plan and why

## Implementation Guidelines

### DO
- ✅ Follow the plan exactly
- ✅ Execute steps in order
- ✅ Keep changes aligned with the learning-focused structure of this repo
- ✅ Run ingestion / API checks when touching RAG or API layers
- ✅ Track progress with TodoWrite
- ✅ Report accurately on completion

### DON'T
- ❌ Skip steps
- ❌ Add features not in the spec or roadmap
- ❌ Perform large refactors unless explicitly requested
- ❌ Ignore validation failures or noisy errors in logs

## Plan
$ARGUMENTS

## Report

After implementation, provide:

### Summary
- Bullet point list of what was accomplished
- Any issues encountered
- Deviations from plan (if any)
- How these changes improve the portfolio bot for end users/clients

### Files Changed
```bash
git diff --stat
```

### Validation Results
- All tests / scripts passing: ✅/❌
- Manual API/UI checks performed (health, `/api/chat`, `/chat`): ✅/❌
- Linting/type checks (if run): ✅/❌

### Next Steps
- What's complete
- What's remaining (if any)
- Recommendations for future roadmap items (e.g., streaming, tools, deployment/docs)
