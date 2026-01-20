# Tool Update - Plan Enhancement for Existing Tool

Create an enhancement plan for an existing tool without implementing it.

**Usage**: `/tool-update "tool-name - description of enhancement"`

Example: `/tool-update "execute_sql_query - add query execution time display"`

## Overview

This command creates an enhancement plan for an existing tool.

**What it does**:
1. **Find the tool** - Locate spec and all integration points
2. **Analyze the enhancement** - Determine what needs to change
3. **Create update plan** - Document all required changes in `updates/`
4. **Create executable plan** - Plan ready for `/implement`

**What it does NOT do**:
- Does NOT write any code
- Does NOT modify existing files
- Does NOT implement the enhancement

The plan is ready to be executed with `/implement specs/04-tools/[tool-name]/updates/YYYY-MM-DD-description.md`

## Execution Flow

### Step 1: Parse User Input

Extract:
- **Tool name**: e.g., "execute_sql_query"
- **Update description**: e.g., "show SQL query in the UI"
- **MCP tool name**: `mcp__algorise__<tool_name>`

### Step 2: Locate Tool and Integration Points

Search for the tool across the codebase:

#### Backend (Python)
1. **Tool implementation**: `algorise/claude_tools/`
   - Search for `@tool("tool_name"` or `@tool('tool_name'`
   - Note file path and line numbers

2. **Server registration**: `algorise/claude_tools/server.py`
   - Check if tool is in `all_tools` list

3. **Allowed tools**: `algorise/services/claude_chat_service.py`
   - Check both streaming and non-streaming `allowed_tools`

4. **Callback handlers**: `algorise/core/claude_callback.py`
   - Search for custom data handler methods
   - Check if tool streams custom data

5. **Capturing wrapper**: `algorise/services/claude_chat_service.py`
   - Check `CapturingCallbackWrapper` for tool-specific handling

#### Frontend (TypeScript/React)
1. **Type definitions**: `frontend/src/components/ui/tool.tsx`
   - Check `ToolPart` type for tool-specific data

2. **Streaming interfaces**: `frontend/src/hooks/chat/useChatStreaming.ts`
   - Check for tool-specific interfaces and state

3. **Tool invocations**: `frontend/src/hooks/chat/useToolInvocations.ts`
   - Check how tool data is extracted and passed

4. **Chat interface**: `frontend/src/components/chat/v2/ChatInterfaceRefactored.tsx`
   - Check data threading

5. **UI renderer**: `frontend/src/components/tools/`
   - Search for `[ToolName]Renderer.tsx`

6. **Tool registry**: `frontend/src/components/tools/registry.tsx`
   - Check tool registration

7. **Translations**:
   - `frontend/locales/en/common.json`
   - `frontend/locales/hr/common.json`

**Output findings**:
```
Found tool: mcp__algorise__execute_sql_query
Backend implementation: algorise/claude_tools/sql_tools.py:25-120
Frontend renderer: frontend/src/components/tools/SqlQueryRenderer.tsx
Current data structure: {results: [], query_info: {...}}
```

### Step 3: Analyze Update Requirements

Based on the update description, determine:

**What needs to change?**
- UI only? → Only modify renderer component
- New data from backend? → Update tool function + callback + frontend types
- Data structure change? → Update backend + all frontend integration points
- New translations? → Update locale files

**Create update plan**:
```markdown
## Update Plan

### Scope: Frontend UI Enhancement

### Changes Needed:
1. Backend: Add `sql_query` to return data (if not already present)
2. Frontend Types: Add `sql_query?: string` to SqlData type
3. UI Renderer: Add UI section to display SQL query
4. Translations: Add labels for SQL query display

### Files to Modify:
- algorise/claude_tools/sql_tools.py
- frontend/src/components/ui/tool.tsx
- frontend/src/components/tools/SqlQueryRenderer.tsx
- frontend/locales/en/common.json
- frontend/locales/hr/common.json

### Breaking Changes: No
```

### Step 4: Create Update Plan Document

**Location**: `specs/04-tools/[tool-name]/updates/YYYY-MM-DD-[enhancement-description].md`

Use the Tool Update Template from `specs/00-meta/TEMPLATES.md`.

Create executable plan with:
- Update metadata (type: enhancement)
- User's original request
- Analysis of what needs to change
- Step-by-step implementation tasks with checkboxes
- Files to modify with exact changes
- Testing checklist
- Expected results

**Format for `/implement`**:
The plan should be structured so `/implement` can execute it:
- Clear sequential steps
- Checkboxes for tracking
- Exact file paths and line numbers where possible
- Code templates to insert
- Validation commands

---

## Common Update Scenarios

### Scenario 1: Add New Field to UI

**Example**: "Show the SQL query in the UI"

#### Backend Changes

**File**: `algorise/claude_tools/[tool_name].py`

**Add field to return data**:
```python
# Before
result_data = {
    "results": rows,
    "query_info": {...}
}

# After
result_data = {
    "results": rows,
    "query_info": {...},
    "sql_query": sql_query  # Add the SQL query
}
```

**After modifying**:
- Update update document with change
- Note file path and line numbers

#### Type Definition Changes

**File**: `frontend/src/components/ui/tool.tsx`

**Update ToolPart type**:
```typescript
export type ToolPart = {
  // ... existing fields
  sqlData?: {
    results: any[]
    query_info: object
    sql_query?: string  // Add this
  }
}
```

**After modifying**:
- Update update document

#### UI Renderer Changes

**File**: `frontend/src/components/tools/[ToolName]Renderer.tsx`

**Add new UI section**:
```typescript
{/* Add SQL Query Display */}
{toolPart.sqlData?.sql_query && (
  <div className="rounded-lg border bg-muted/50 p-3 mb-3">
    <div className="flex items-center gap-2 mb-2">
      <Code2 className="h-4 w-4 text-muted-foreground" />
      <span className="text-xs font-medium text-muted-foreground">
        {t('tools.sqlTool.query')}
      </span>
    </div>
    <pre className="text-xs font-mono bg-background p-2 rounded overflow-x-auto">
      {toolPart.sqlData.sql_query}
    </pre>
  </div>
)}
```

**After modifying**:
- Update update document
- Note exact line numbers

#### Translation Changes

**File**: `frontend/locales/en/common.json`

**Add keys**:
```json
"tools": {
  "sqlTool": {
    "query": "SQL Query",
    // ... existing keys
  }
}
```

**File**: `frontend/locales/hr/common.json`

**Add keys**:
```json
"tools": {
  "sqlTool": {
    "query": "SQL Upit",
    // ... existing keys
  }
}
```

**After modifying**:
- Update update document

---

### Scenario 2: Change UI Layout/Styling

**Example**: "Make the results table more compact"

**Changes needed**: Only UI renderer

**File**: `frontend/src/components/tools/[ToolName]Renderer.tsx`

Modify styling:
- Adjust padding, spacing
- Change table layout
- Update responsive behavior

**No backend or type changes needed**

---

### Scenario 3: Add New Data Source

**Example**: "Include query execution time"

**Full stack changes needed**:

1. **Backend**: Capture execution time
2. **Backend**: Add to return data
3. **Callback**: Stream if real-time
4. **Frontend types**: Add to interface
5. **State management**: Handle new data
6. **UI**: Display execution time
7. **Translations**: Add labels

Follow same pattern as Scenario 1 for each layer.

---

### Scenario 4: Performance Optimization

**Example**: "Cache query results for 5 minutes"

**Backend changes only**:

**File**: `algorise/claude_tools/[tool_name].py`

```python
# Add caching logic
from functools import lru_cache
import time

cache = {}

async def tool_name(args: dict[str, Any]) -> dict[str, Any]:
    query = args.get("query")
    cache_key = f"{query}:{user_id}"

    # Check cache
    if cache_key in cache:
        cached_time, cached_data = cache[cache_key]
        if time.time() - cached_time < 300:  # 5 minutes
            logger.info("[TOOL] Using cached data")
            return cached_data

    # Execute query
    result_data = execute_query(query)

    # Cache result
    cache[cache_key] = (time.time(), result_data)

    return result_data
```

**Document performance impact** in update doc.

---

## Step 6: Test Changes

### Testing Checklist

**Backend Tests**:
- [ ] Tool still executes successfully
- [ ] New data field is present in response
- [ ] Existing functionality not broken
- [ ] Error handling still works

**Frontend Tests** (if UI changes):
- [ ] New field displays correctly
- [ ] UI renders properly on all screen sizes
- [ ] Data persists on page refresh
- [ ] Translations show correctly (EN + HR)
- [ ] Existing data still displays

**Integration Tests**:
- [ ] Works in new conversations
- [ ] Works in existing conversations
- [ ] No console errors
- [ ] No type errors (run `npm run type-check`)

### Document Test Results

Update the update document with:
```markdown
## Testing Results

### Manual Testing
**Date**: YYYY-MM-DD

**Test 1: New field displays**
- Status: ✅ Pass
- Notes: SQL query shows correctly in UI

**Test 2: Existing functionality**
- Status: ✅ Pass
- Notes: Results table still works

**Test 3: Translations**
- Status: ✅ Pass
- Notes: Both EN and HR labels display

### Issues Found
None
```

---

## Step 7: Finalize Documentation

### Update the Update Document

Complete all sections:
- ✅ All changes documented
- ✅ Files modified list complete
- ✅ Before/after code samples
- ✅ Testing results added
- ✅ Screenshots/examples if helpful

### Update Main spec.md

**File**: `specs/04-tools/[tool-name]/spec.md`

Update relevant sections:
- **Output Schema**: If data structure changed
- **Implementation**: If code paths changed
- **Change History**: Add entry for this update

```markdown
## Change History

- **2025-10-11**: Added SQL query display to UI (see updates/2025-10-11-show-query.md)
- **2025-01-15**: Initial creation
```

Update frontmatter:
```markdown
---
updated: 2025-10-11
---
```

### Update implementation.md (if significant)

If the update was substantial, add a note to implementation.md:
```markdown
## Updates

### 2025-10-11: Added SQL Query Display
See: `updates/2025-10-11-show-query.md`

**Changes**:
- Added `sql_query` field to backend response
- Updated UI to display SQL query
- Added translations
```

---

## Step 8: Provide Summary

Output:
```
✅ Tool Updated: execute_sql_query

📝 Update: Show SQL query in the UI

Files Modified (5):
- algorise/claude_tools/sql_tools.py (added sql_query field)
- frontend/src/components/ui/tool.tsx (added type)
- frontend/src/components/tools/SqlQueryRenderer.tsx (added UI section)
- frontend/locales/en/common.json (added translations)
- frontend/locales/hr/common.json (added translations)

✅ All tests passing
✅ Documentation updated

Update document: specs/04-tools/execute_sql_query/updates/2025-10-11-show-query.md
```

---

## Error Handling

### Tool Not Found

If tool cannot be located:
```
❌ Tool 'unknown_tool' not found in codebase.

Searched locations:
- algorise/claude_tools/*.py
- frontend/src/components/tools/*.tsx

Available tools:
- execute_sql_query
- vector_search
- generate_chart
[... list from server.py ...]

Did you mean: execute_sql_query?
```

### Ambiguous Update

If update description is unclear, ask:
```
🤔 Need clarification on update:

The description "improve the tool" is too vague.

Please specify:
- What specific aspect to improve?
- What should the new behavior be?
- Is this a UI change, backend change, or both?

Example: "show execution time in the UI"
```

---

## Common Pitfalls

1. **Forgetting to update both type definitions** (backend and frontend)
2. **Not testing in existing conversations** (only testing new chats)
3. **Missing translations** (only adding English)
4. **Not updating main spec.md** (only creating update doc)
5. **Breaking existing functionality** (not testing old features)
6. **Incomplete update document** (not documenting all changes)
7. **Not checking type errors** (run `npm run type-check`)

---

## Validation Commands

Before considering update complete:

### Backend
```bash
# Check tool still registered
grep -r "your_tool" algorise/claude_tools/server.py

# Check allowed tools
grep -r "mcp__algorise__your_tool" algorise/services/
```

### Frontend
```bash
cd frontend

# Type check
npm run type-check

# Lint check
npm run lint

# Build check
npm run build
```

---

## Reference

For update examples, see:
- Existing update docs in `specs/04-tools/*/updates/`
- Tool update template in `specs/00-meta/TEMPLATES.md`

---

**Let's track down and update your tool!** 🔍

## Tool Update
$ARGUMENTS
