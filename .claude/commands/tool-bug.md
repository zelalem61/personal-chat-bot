# Tool Bug - Plan Bug Fix for Existing Tool

Create a bug fix plan for an existing tool without implementing it.

**Usage**: `/tool-bug "tool-name - description of bug"`

Example: `/tool-bug "execute_sql_query - fix memory leak in query cache"`

## Overview

This command creates a bug fix plan for an existing tool.

**What it does**:
1. **Find the tool** - Locate spec and all integration points
2. **Reproduce the bug** - Understand the issue
3. **Root cause analysis** - Identify why it's happening
4. **Create fix plan** - Document the fix strategy
5. **Create executable plan** - Plan ready for `/implement`

**What it does NOT do**:
- Does NOT write any code
- Does NOT modify existing files
- Does NOT implement the fix

The plan is ready to be executed with `/implement specs/04-tools/[tool-name]/bugs/YYYY-MM-DD-description.md`

---

## Execution Flow

### Step 1: Parse User Input

Extract:
- **Tool name**: e.g., "execute_sql_query"
- **Bug description**: e.g., "memory leak in query cache"
- **MCP tool name**: `mcp__algorise__<tool_name>`

### Step 2: Locate Tool

Find the tool's implementation:

#### Backend (Python)
1. **Tool implementation**: `algorise/claude_tools/`
   - Search for `@tool("tool_name"`
   - Note file path and line numbers

2. **Related files**: Find all files that use this tool
   - Callback handlers
   - Capturing wrappers
   - Server registration

#### Frontend (TypeScript/React)
1. **UI renderer**: `frontend/src/components/tools/[ToolName]Renderer.tsx`
2. **Type definitions**: Check types in `frontend/src/components/ui/tool.tsx`
3. **Integration files**: streaming hooks, invocations, etc.

**Output findings**:
```
Found tool: mcp__algorise__execute_sql_query
Backend: algorise/claude_tools/sql_tools.py:25-150
Frontend: frontend/src/components/tools/SqlQueryRenderer.tsx
```

### Step 3: Reproduce and Analyze Bug

#### Reproduction
- What are the steps to reproduce?
- What input causes the bug?
- What is the expected vs actual behavior?
- Can you reproduce it consistently?

#### Root Cause Analysis
Ask:
- **Where** does the bug occur? (file, function, line number)
- **Why** does it happen? (logic error, missing validation, race condition, etc.)
- **When** does it happen? (specific conditions, edge cases)
- **What** is the impact? (severity, frequency, affected users)

**Document findings**:
```markdown
## Bug Analysis

### Reproduction Steps
1. Open chat
2. Run query: "SELECT * FROM large_table"
3. Run 10 more queries
4. Memory usage increases and doesn't drop

### Root Cause
**Location**: `algorise/claude_tools/sql_tools.py:78-85`
**Issue**: Cache dictionary never clears old entries
**Why**: No TTL check, no max size limit
**Impact**: Memory grows unbounded with heavy usage

### Evidence
- Cache size after 100 queries: 150MB
- No cache eviction logic
- Python dict grows indefinitely
```

### Step 4: Create Bug Fix Plan Document

**Location**: `specs/04-tools/[tool-name]/bugs/YYYY-MM-DD-[bug-description].md`

Use the Tool Bug Fix Template from `specs/00-meta/TEMPLATES.md`.

Create executable plan with:
- Bug metadata (type: bugfix, severity)
- Reproduction steps
- Root cause analysis
- Fix strategy
- Step-by-step implementation tasks with checkboxes
- Files to modify with exact changes
- Regression test plan
- Validation checklist

**Format for `/implement`**:
The plan should be structured so `/implement` can execute it:
- Clear sequential fix steps
- Checkboxes for tracking
- Exact file paths and line numbers
- Code to add/modify
- Test cases to prevent regression
- Validation commands

---

## Common Bug Fix Scenarios

### Scenario 1: Logic Error

**Example**: "Tool returns wrong results for empty input"

#### Fix Strategy
1. **Identify** where empty input is handled
2. **Add** validation or special case handling
3. **Test** with empty, null, and undefined inputs
4. **Add** unit test to prevent regression

#### Fix Plan Structure
```markdown
## Fix Plan

### Step 1: Add Input Validation
**File**: `algorise/claude_tools/[tool_name].py`
**Line**: 35

**Add before main logic**:
```python
# Validate input
if not param1 or param1.strip() == "":
    return {
        "content": [{"type": "text", "text": "Error: Input cannot be empty"}],
        "is_error": True
    }
```

### Step 2: Add Unit Test
**File**: `tests/unit/test_[tool_name].py`

**Add test**:
```python
def test_empty_input():
    result = await tool_name({"param1": ""})
    assert result["is_error"] == True
    assert "cannot be empty" in result["content"][0]["text"].lower()
```

### Step 3: Validation
- [ ] Test with empty string
- [ ] Test with whitespace only
- [ ] Test with null/undefined
- [ ] Verify error message is clear
- [ ] Run all existing tests
```

---

### Scenario 2: Memory Leak

**Example**: "Cache grows unbounded"

#### Fix Strategy
1. **Add TTL** (time-to-live) for cache entries
2. **Add max size** limit with LRU eviction
3. **Add cleanup** task to remove expired entries
4. **Monitor** memory usage before/after

#### Fix Plan Structure
```markdown
## Fix Plan

### Step 1: Add TTL and Max Size
**File**: `algorise/claude_tools/[tool_name].py`

**Replace cache dict with LRU cache**:
```python
from functools import lru_cache
from collections import OrderedDict
import time

class TTLCache:
    def __init__(self, max_size=100, ttl_seconds=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            timestamp, value = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = (time.time(), value)

# Replace global cache
cache = TTLCache(max_size=100, ttl_seconds=300)
```

### Step 2: Update Tool to Use New Cache
**File**: `algorise/claude_tools/[tool_name].py`

**Modify caching logic**:
```python
# Check cache
cached_result = cache.get(cache_key)
if cached_result:
    logger.info("[TOOL] Using cached result")
    return cached_result

# Execute and cache
result = execute_query(query)
cache.set(cache_key, result)
```

### Step 3: Add Memory Monitoring
**File**: `algorise/claude_tools/[tool_name].py`

**Add logging**:
```python
import sys

cache_size = sys.getsizeof(cache.cache)
logger.info(f"[TOOL] Cache size: {cache_size} bytes, entries: {len(cache.cache)}")
```

### Step 4: Test Memory Usage
- [ ] Run 100 queries
- [ ] Check memory stays under limit
- [ ] Verify old entries are evicted
- [ ] Confirm TTL works (expired entries removed)
```

---

### Scenario 3: Race Condition

**Example**: "Tool fails when called concurrently"

#### Fix Strategy
1. **Add locking** to protect shared state
2. **Make operations atomic**
3. **Test concurrent** access
4. **Add async safety** if needed

---

### Scenario 4: UI Bug

**Example**: "Renderer crashes with certain data"

#### Fix Strategy
1. **Add null/undefined checks**
2. **Add defensive rendering**
3. **Handle edge cases** (empty arrays, missing fields)
4. **Test with edge case data**

---

## Step 5: Document Testing Strategy

Include in bug fix plan:

### Regression Tests
- Tests that verify the bug is fixed
- Tests that prevent the bug from returning

### Edge Case Tests
- Test boundary conditions
- Test invalid inputs
- Test error scenarios

### Integration Tests
- Test tool in actual usage
- Test with real data
- Test in production-like conditions

**Example**:
```markdown
## Testing Strategy

### Regression Test
**Test**: Memory leak is fixed
**Method**:
1. Run 100 queries
2. Measure memory before and after
3. Verify memory returns to baseline
4. Check cache size stays under limit

**Expected**: Memory stabilizes, no unbounded growth

### Edge Cases
- Empty cache
- Cache at max capacity
- Expired entries
- Concurrent access

### Validation
- [ ] Bug no longer reproducible
- [ ] Memory usage stays stable
- [ ] Performance not degraded
- [ ] All existing tests pass
- [ ] New regression test added
```

---

## Step 6: Provide Summary

Output:
```
✅ Bug fix plan created: execute_sql_query

🐛 Bug: Memory leak in query cache

📁 Plan location: specs/04-tools/execute_sql_query/bugs/2025-10-11-fix-memory-leak.md

📋 Fix strategy:
- Replace dict with TTL-based LRU cache
- Add max size limit (100 entries)
- Add automatic cleanup of expired entries
- Add memory monitoring

📝 Files to modify:
- algorise/claude_tools/sql_tools.py (implement TTL cache)
- tests/unit/test_sql_tools.py (add regression tests)

Next step:
/implement specs/04-tools/execute_sql_query/bugs/2025-10-11-fix-memory-leak.md
```

---

## Error Handling

### Tool Not Found
```
❌ Tool 'unknown_tool' not found

Searched locations:
- algorise/claude_tools/*.py
- frontend/src/components/tools/*.tsx

Available tools: [list from server.py]
```

### Unable to Reproduce Bug
```
⚠️ Cannot reproduce the bug with provided information

Need more details:
- Exact steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Environment (dev/staging/prod)

Example: "When user sends query 'SELECT *', tool returns empty array instead of results"
```

---

## Common Pitfalls

1. **Fixing symptoms** instead of root cause
2. **Not adding regression tests** (bug will return)
3. **Breaking existing functionality** while fixing bug
4. **Not testing edge cases** thoroughly
5. **Incomplete root cause analysis**
6. **Not documenting why** bug happened
7. **Not checking performance impact** of fix

---

## Validation Commands

Before considering fix complete:

```bash
# Backend
uv run pytest tests/unit/test_[tool_name].py -v

# Frontend (if UI bug)
cd frontend
npm run test -- [ToolName]Renderer
npm run type-check

# Integration
# Test tool in actual conversation
```

---

## Reference

For bug fix examples, see:
- Existing bug fix docs in `specs/04-tools/*/bugs/`
- Tool bug fix template in `specs/00-meta/TEMPLATES.md`
- Main bug workflow in `specs/03-bugs/`

---

**Let's fix that bug!** 🐛🔧

## Bug Description
$ARGUMENTS
