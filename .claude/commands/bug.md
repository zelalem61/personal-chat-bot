# Bug Planning

Create a surgical plan in `specs/03-bugs/_open/` to resolve the bug using the exact specified `Plan Format`.

## Instructions

- **You're writing a plan to FIX a bug** - be thorough, precise, and surgical
- **Think HARD** about the bug, its root cause, and the minimal fix needed
- Create the plan in `specs/03-bugs/_open/bug-[description].md`
- Use the `Plan Format` below - replace every <placeholder> with actual content
- **Be surgical**: Fix the bug at hand with minimal changes, don't refactor unrelated code
- Research the codebase first to understand the bug fully
- Follow existing patterns - don't introduce new architecture

## Relevant Files

Focus on:
- `CLAUDE.md` - Project overview and patterns
- `frontend/**` - Next.js/TypeScript frontend
- `algorise/**` - Python backend (claude_chat_service.py for agents, not langgraph)

Use terminal commands to find relevant files and inspect the project.

## Plan Format

```md
# Bug: <bug name>

**Severity**: <Critical | High | Medium | Low>
**Status**: open
**Created**: <YYYY-MM-DD>

## Bug Description
<describe symptoms, expected vs actual behavior>

## Steps to Reproduce
1. <step 1>
2. <step 2>
3. <step 3>
4. **Expected**: <what should happen>
5. **Actual**: <what actually happens>

## Problem Statement
<clearly define the specific problem to solve>

## Root Cause Analysis
**Location**: `<file>:<line>`
**Function**: `<function_name>()`

**Why it happens**:
<explain the root cause>

**Evidence**:
- Logs/stack traces
- Console output
- Screenshots

## Solution Statement
<describe the minimal, surgical fix approach>

## Relevant Files

### Files to Modify
- `<file1>:<line>` - <why this change is needed>
- `<file2>:<line>` - <why this change is needed>

### Files for Reference
- `<file>` - <context for understanding>

## Step by Step Tasks

**IMPORTANT**: Execute in order, top to bottom.

### Step 1: Fix Core Issue
- [ ] Modify `<file>` to <specific change>
- [ ] Add validation for <edge case>
- [ ] Update error handling

### Step 2: Add Regression Test
- [ ] Add test that reproduces the bug
- [ ] Verify test fails before fix
- [ ] Verify test passes after fix
- [ ] Add to appropriate test file

### Step 3: Validation
- [ ] Manually reproduce bug (should be fixed)
- [ ] Run full test suite
- [ ] Check for regressions
- [ ] Test edge cases

## Testing Strategy

### Regression Tests
- Test reproducing original bug
- Test edge cases: <list>

### Manual Testing
- [ ] Reproduce original bug - verify fixed
- [ ] Test happy path - verify no regression
- [ ] Test error scenarios

## Validation Commands
```bash
# Run tests
npm test
# or
uv run pytest tests/

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

## Impact Assessment

**Users affected**: <all users | specific group>
**Functionality broken**: <what doesn't work>
**Workaround**: <available workaround if any>

## Prevention

**Why this happened**:
<how bug was introduced>

**How to prevent similar bugs**:
- Add test coverage for <scenario>
- Improve validation for <input>
- Add monitoring for <metric>

## Notes
<additional context, timeline, deployment notes>
```

## After Creating Plan

```bash
# When starting to fix
/spec-move bug-[name] in-progress

# When deployed and verified
/spec-move bug-[name] fixed
```

## Bug
$ARGUMENTS
