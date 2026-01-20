# Tool Plan - Create Implementation Plan for New Tool

Create a complete plan for a new tool without implementing it.

**Usage**: `/tool-plan "tool_name - description"`

Example: `/tool-plan "execute_queries - Run SQL queries with visualization"`

## Overview

This command creates a complete implementation plan that can be executed later with `/implement`.

**What it does**:
1. Ask clarifying questions about the tool
2. Create tool directory structure
3. Create `spec.md` (complete specification)
4. Create `implementation.md` (detailed 10-phase plan)
5. Create empty `updates/` and `bugs/` directories
6. Create `tests.md` template

**What it does NOT do**:
- Does NOT write any code
- Does NOT modify existing files
- Does NOT implement the tool

The plan is ready to be executed with `/implement specs/04-tools/[tool-name]/implementation.md`

---

## Step 1: Ask Clarifying Questions

Before creating the plan, gather requirements:

### Required Information
- **What does the tool do?** (core functionality)
- **What input does it need?** (parameters, types)
- **What output does it produce?** (return format)
- **Does it need UI visualization?** (yes/no)
- **Does it stream data to frontend?** (yes/no, what data?)
- **What permissions are required?** (admin/user/public)

### Optional Information
- Expected latency/performance
- External dependencies
- Special security considerations
- Related tools or features

---

## Step 2: Create Directory Structure

**Location**: `specs/04-tools/[tool-name]/`

Create:
```
tool-name/
├── spec.md              # Complete specification (from template)
├── implementation.md    # 10-phase implementation plan (from template)
├── updates/             # Empty (for future enhancements)
├── bugs/                # Empty (for future bug fixes)
└── tests.md             # Testing template
```

---

## Step 3: Create spec.md

Use the **Tool Template** from `specs/00-meta/TEMPLATES.md`.

Fill in based on answers:

### Frontmatter
```yaml
---
id: tool-[nnn]
title: "[Tool Name]"
type: tool
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: Claude Code
tags: [backend, integration, data, ...]
---
```

### Key Sections

**Overview**:
- Purpose (one sentence)
- Category (data-access | integration | utility | generation | analysis)
- Permissions required

**Input Schema** (JSON):
```json
{
  "parameter1": {
    "type": "string",
    "description": "Clear description",
    "required": true
  },
  "parameter2": {
    "type": "number",
    "description": "Clear description",
    "required": false,
    "default": 10
  }
}
```

**Output Schema** (JSON):
```json
{
  "result": {
    "type": "object",
    "description": "Result data structure"
  },
  "metadata": {
    "type": "object",
    "description": "Additional metadata"
  }
}
```

**Error Responses**:
- List all error codes and meanings
- Examples: INVALID_INPUT, PERMISSION_DENIED, NOT_FOUND, INTERNAL_ERROR

**Implementation**:
- Backend file path: `algorise/claude_tools/[tool_name].py`
- Frontend renderer (if applicable): `frontend/src/components/tools/[ToolName]Renderer.tsx`
- Integration points (files that need modification)

**Testing**:
- Unit test scenarios
- Integration test scenarios
- Manual test cases
- Performance benchmarks

**Usage Examples**:
- How agents will use this tool
- Example conversations
- Expected results

**Performance Considerations**:
- Expected latency
- Throughput requirements
- Caching strategy

**Security Considerations**:
- Input validation requirements
- Authorization checks
- Sensitive data handling
- Audit logging

---

## Step 4: Create implementation.md

Use the **Tool Implementation Log Template** from `specs/00-meta/TEMPLATES.md`.

This is the **executable plan** for `/implement`.

### Structure

```markdown
# Implementation Plan: [Tool Name]

**Tool**: [tool-name]
**Created**: YYYY-MM-DD
**Status**: Not Started
**Last Updated**: YYYY-MM-DD HH:MM

## Overview

This implementation plan will guide the creation of [tool-name].

**What it does**: [Brief description]
**Input**: [Summary of inputs]
**Output**: [Summary of outputs]
**UI Needed**: Yes/No

---

## Implementation Steps

Follow these phases in order. Each phase must be completed before moving to the next.

### Phase 1: Backend Tool Implementation ⏸️ Pending

**Goal**: Create the Python tool function and register it.

#### Step 1.1: Create Tool Function
**File**: `algorise/claude_tools/[tool_name].py`

**Tasks**:
- [ ] Create new file `algorise/claude_tools/[tool_name].py`
- [ ] Import required dependencies
- [ ] Define tool function with @tool decorator
- [ ] Implement input validation
- [ ] Implement main tool logic
- [ ] Add comprehensive logging
- [ ] Add error handling
- [ ] Test function locally

**Expected Result**: Tool function executes successfully

#### Step 1.2: Register in MCP Server
**File**: `algorise/claude_tools/server.py`

**Tasks**:
- [ ] Import tool function
- [ ] Add to `all_tools` list

**Expected Result**: Tool registered in MCP server

#### Step 1.3: Add to Allowed Tools
**File**: `algorise/services/claude_chat_service.py`

**Tasks**:
- [ ] Add `mcp__algorise__[tool_name]` to non-streaming allowed_tools
- [ ] Add `mcp__algorise__[tool_name]` to streaming allowed_tools

**Expected Result**: Tool can be invoked by agent

---

### Phase 2: Callback Handler ⏸️ Pending
[Only if tool streams data to UI]

**Skip this phase if**: Tool only returns text to Claude

#### Step 2.1: Add Callback Protocol
**File**: `algorise/core/claude_callback.py`

**Tasks**:
- [ ] Add method to ClaudeStreamHandler protocol
- [ ] Add method to ClaudeStreamCallback class

#### Step 2.2: Implement SSE Streaming
**File**: `algorise/core/claude_callback.py`

**Tasks**:
- [ ] Add handler in ClaudeSSEStreamHandler
- [ ] Format data using Vercel protocol

#### Step 2.3: Add to Capturing Wrapper
**File**: `algorise/services/claude_chat_service.py`

**Tasks**:
- [ ] Add method to CapturingCallbackWrapper
- [ ] Capture tool data

---

### Phase 3-10: [Continue with remaining phases]

[Include all 10 phases with detailed steps]

---

## Files to Create

- `algorise/claude_tools/[tool_name].py`
- `frontend/src/components/tools/[ToolName]Renderer.tsx` (if UI needed)

## Files to Modify

- `algorise/claude_tools/server.py`
- `algorise/services/claude_chat_service.py`
- `algorise/core/claude_callback.py` (if streaming)
- `frontend/src/components/ui/tool.tsx` (if UI needed)
- `frontend/src/hooks/chat/useChatStreaming.ts` (if UI needed)
- `frontend/src/hooks/chat/useToolInvocations.ts` (if UI needed)
- `frontend/src/components/chat/v2/ChatInterfaceRefactored.tsx` (if UI needed)
- `frontend/src/components/tools/registry.tsx` (if UI needed)
- `frontend/locales/en/common.json`
- `frontend/locales/hr/common.json`

## Validation

After implementation, verify:
- [ ] Backend tool executes successfully
- [ ] Tool is registered and invokable
- [ ] Data flows correctly (backend → frontend if applicable)
- [ ] UI renders properly (if applicable)
- [ ] Translations work (EN + HR)
- [ ] All tests pass
- [ ] No type errors

## Execution

To execute this plan, run:
```bash
/implement specs/04-tools/[tool-name]/implementation.md
```
```

**Key features**:
- Each phase has clear goals and checkboxes
- Files are specified with exact paths
- Expected results are clear
- Can be executed by `/implement`
- Can be updated as implementation progresses

---

## Step 5: Create tests.md

Create initial testing template:

```markdown
# Testing Documentation: [Tool Name]

## Test Plan

### Unit Tests
[To be written during implementation]

### Integration Tests
[To be written during implementation]

### Manual Tests
[To be documented as tests are performed]

## Test Results

[Results will be added after implementation]
```

---

## Step 6: Output Summary

Provide clear next steps:

```
✅ Tool plan created: [tool-name]

📁 Directory: specs/04-tools/[tool-name]/

📝 Files Created:
- spec.md (complete specification)
- implementation.md (10-phase implementation plan)
- updates/ (empty, for future enhancements)
- bugs/ (empty, for future bug fixes)
- tests.md (testing template)

📋 Next Steps:

1. Review the specification:
   specs/04-tools/[tool-name]/spec.md

2. Review the implementation plan:
   specs/04-tools/[tool-name]/implementation.md

3. When ready to implement, run:
   /implement specs/04-tools/[tool-name]/implementation.md

The plan is complete and ready for execution!
```

---

## Example Workflow

```bash
# User runs planning command
$ /tool-plan "payment_processor - Integrate Stripe payments"

# Claude asks questions:
# - What payment methods? (cards, wallets, etc.)
# - Should it handle webhooks? (yes/no)
# - UI for payment status? (yes/no)
# - Permissions? (user can pay, admin can refund)

# User answers questions

# Claude creates:
# - specs/04-tools/payment_processor/spec.md
# - specs/04-tools/payment_processor/implementation.md
# - specs/04-tools/payment_processor/updates/ (empty)
# - specs/04-tools/payment_processor/bugs/ (empty)
# - specs/04-tools/payment_processor/tests.md

# Output:
# "✅ Plan ready. Review implementation.md then run:
#  /implement specs/04-tools/payment_processor/implementation.md"

# User reviews the plan

# User executes:
$ /implement specs/04-tools/payment_processor/implementation.md

# Claude implements all 10 phases, updating implementation.md as it goes
```

---

## Notes

- This command is **planning only** - no code is written
- The plan can be reviewed and modified before execution
- The plan serves as both input to `/implement` and a log of what was done
- Keep plans detailed but focused - avoid over-engineering
- Trust that `/implement` will handle the execution

---

**Let's plan your tool!** 📋

## Tool Description
$ARGUMENTS
