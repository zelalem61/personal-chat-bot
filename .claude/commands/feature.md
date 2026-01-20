# Feature Planning

Create a plan in `specs/02-features/_planning/` to implement the feature using the exact specified `Plan Format`.

## Instructions

- **You're writing a plan to IMPLEMENT a new feature** that adds value to the application
- **Think HARD** about requirements, design, and implementation approach
- Create plan in `specs/02-features/_planning/feat-[name].md` (or phased structure for complex features)
- Use the `Plan Format` below - replace every <placeholder> with actual content
- **Follow existing patterns** - research the codebase, don't reinvent the wheel
- Design for extensibility and maintainability
- If you need a new library, use `uv add` and note it in the `Notes` section
- Research the codebase first to understand existing patterns and architecture

## Relevant Files

Focus on:
- `CLAUDE.md` - Project overview and patterns
- `frontend/**` - Next.js/TypeScript frontend
- `algorise/**` - Python backend (claude_chat_service.py for agents, not langgraph)

Use terminal commands to find relevant files and inspect the project.

## For Complex Features

Create phased structure:
```
specs/02-features/_planning/feat-[name]/
├── overview.md          # High-level feature overview
├── phase-0-foundation.md # DB, models, types, utilities
├── phase-1-core.md      # Main implementation
├── phase-2-integration.md # UI, state, API integration
└── phase-3-polish.md    # Testing, errors, edge cases
```

## For Simple Features

Create single file: `specs/02-features/_planning/feat-[name].md`

## Plan Format

```md
# Feature: <feature name>

**Priority**: <High | Medium | Low>
**Complexity**: <High | Medium | Low>
**Estimate**: <X weeks/days>
**Status**: planning
**Created**: <YYYY-MM-DD>

## Feature Description
<describe the feature in detail, its purpose and value to users>

## User Story
**As a** <type of user>
**I want to** <action/goal>
**So that** <benefit/value>

## Problem Statement
<clearly define the problem or opportunity this feature addresses>

## Solution Statement
<describe the proposed solution approach and how it solves the problem>

## Relevant Files

### Existing Files to Modify
- `<file1>` - <why it's relevant, what will change>
- `<file2>` - <why it's relevant, what will change>

### New Files to Create
- `<new-file1>` - <purpose of this file>
- `<new-file2>` - <purpose of this file>

## Implementation Plan

### Phase 0: Foundation
<foundational work before main feature>
- Database migrations
- New models/types
- Shared utilities

### Phase 1: Core Implementation
<main implementation work>
- Backend API endpoints
- Business logic
- Data access layer

### Phase 2: Integration
<integration with existing functionality>
- Frontend components
- State management
- API integration

### Phase 3: Polish & Testing
<refinements and validation>
- Error handling
- Edge cases
- Performance optimization

## Step by Step Tasks

**IMPORTANT**: Execute in order, top to bottom.

### Step 1: <Foundation Task Group>
- [ ] <specific task>
- [ ] <specific task>
- [ ] <specific task>

### Step 2: <Core Implementation Task Group>
- [ ] <specific task>
- [ ] <specific task>

### Step 3: <Integration Task Group>
- [ ] <specific task>
- [ ] <specific task>

### Step 4: <Testing Task Group>
- [ ] <specific task>
- [ ] <specific task>

### Final Step: Validation
- [ ] Run all validation commands
- [ ] Verify zero regressions
- [ ] Update documentation

## Testing Strategy

### Unit Tests
<what functions/methods need unit tests>

### Integration Tests
<what end-to-end workflows need testing>

### Edge Cases
<edge cases to test>

## Acceptance Criteria

Feature is complete when:
- [ ] <specific, measurable criterion 1>
- [ ] <specific, measurable criterion 2>
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Documentation updated

## Validation Commands

Execute every command to validate the feature works with zero regressions.

```bash
# Backend tests
uv run pytest tests/unit/ -v --tb=short

# Frontend tests
cd frontend && npm test

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

## Notes
<additional notes, future considerations, context>
- New dependencies added: <list if any>
- Known limitations: <list if any>
- Future enhancements: <list if any>
```

## After Creating Plan

```bash
# When starting implementation
/spec-move feat-[name] in-progress

# When complete
/spec-move feat-[name] completed
```

## Feature
$ARGUMENTS
