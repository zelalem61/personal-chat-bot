# Update Existing Tool - Automated Tracking & Implementation

You are tasked with updating an existing tool in the Algorise application. This command will automatically track down all integration points for the specified tool and make the requested changes.

## User Input Format

The user will provide a tool name and update description:
```
/update-tool "<tool_name> - <description of what to update>"
```

Example:
```
/update-tool "execute_sql_query tool - show the SQL query on the UI in its tool result component"
```

## Phase 1: Tool Discovery & Analysis

### 1.1 Extract Tool Information
- Parse tool name from user input (e.g., "execute_sql_query")
- Parse update description (e.g., "show the SQL query on the UI")
- Determine the MCP tool name format: `mcp__algorise__<tool_name>`

### 1.2 Locate All Tool Integration Points

Search for the tool across these locations:

**Backend (Python)**:
1. Tool implementation: `algorise/claude_tools/` (search for `@tool("<tool_name>"` or `@tool('mcp__algorise__<tool_name>'`)
2. Server registration: `algorise/claude_tools/server.py` (check `all_tools` list)
3. Allowed tools: `algorise/services/claude_chat_service.py` (check `allowed_tools` lists)
4. Callback handlers: `algorise/core/claude_callback.py` (search for custom data handlers)
5. Capturing wrapper: `algorise/services/claude_chat_service.py` in `CapturingCallbackWrapper`

**Frontend (TypeScript/React)**:
1. Type definitions: `frontend/src/components/ui/tool.tsx` in `ToolPart` type
2. Streaming interfaces: `frontend/src/hooks/chat/useChatStreaming.ts`
3. Tool invocations: `frontend/src/hooks/chat/useToolInvocations.ts`
4. Chat interface: `frontend/src/components/chat/v2/ChatInterfaceRefactored.tsx`
5. UI renderer: `frontend/src/components/tools/` (search for tool-specific renderer)
6. Tool registry: `frontend/src/components/tools/registry.tsx`
7. Translations: `frontend/locales/en/common.json` and `frontend/locales/hr/common.json`

### 1.3 Document Current State
Log findings:
```
Found tool: mcp__algorise__<tool_name>
Backend implementation: algorise/claude_tools/<file>.py:<line>
Frontend renderer: frontend/src/components/tools/<ToolRenderer>.tsx
Current data structure: <describe what data is currently being passed>
```

## Phase 2: Analyze Update Requirements

Based on the update description, determine:
- **What needs to change?** (UI component, data structure, backend logic, etc.)
- **Does it require new data from backend?** If yes, need to update:
  - Tool function to include new data
  - Callback handlers to stream new data
  - Frontend types to receive new data
- **Is it UI-only?** If yes, only need to update renderer component
- **Does it need new translations?** If yes, update both EN and HR locales

Create a plan with specific files and changes needed.

## Phase 3: Implement Changes

### 3.1 Backend Changes (if needed)

If new data needs to be captured/streamed:

1. **Update tool function** (`algorise/claude_tools/<file>.py`):
   - Modify return data structure to include new fields
   - Update logging to reflect new data
   - Example:
   ```python
   # Before
   result_data = {"results": rows}

   # After
   result_data = {"results": rows, "sql_query": sql_query}
   ```

2. **Update callback handler** (`algorise/core/claude_callback.py`):
   - If using custom data streaming, ensure new fields are included
   - Update TypeScript-like interfaces in docstrings

3. **Update capturing wrapper** (`algorise/services/claude_chat_service.py`):
   - Ensure new data is captured in `CapturingCallbackWrapper`

### 3.2 Frontend Type Updates

1. **Update ToolPart type** (`frontend/src/components/ui/tool.tsx`):
   ```typescript
   export type ToolPart = {
     // ... existing fields
     sqlData?: {
       results: any[]
       sql_query?: string  // Add new field
     }
   }
   ```

2. **Update streaming interfaces** (`frontend/src/hooks/chat/useChatStreaming.ts`):
   - Add new fields to data interfaces
   - Update parsing logic if data structure changed

3. **Update tool invocations** (`frontend/src/hooks/chat/useToolInvocations.ts`):
   - Ensure new data is extracted and passed through

### 3.3 UI Renderer Updates

1. **Modify renderer component** (`frontend/src/components/tools/<ToolRenderer>.tsx`):
   - Add new UI elements to display additional data
   - Follow existing design patterns (use Card, Badge, etc.)
   - Use proper icons from lucide-react
   - Example:
   ```typescript
   // Add SQL query display
   {toolPart.sqlData?.sql_query && (
     <div className="rounded-lg border bg-muted/50 p-3">
       <div className="flex items-center gap-2 mb-2">
         <Code2 className="h-4 w-4 text-muted-foreground" />
         <span className="text-xs font-medium text-muted-foreground">
           {t('tools.sqlTool.query')}
         </span>
       </div>
       <pre className="text-xs font-mono">{toolPart.sqlData.sql_query}</pre>
     </div>
   )}
   ```

### 3.4 Translation Updates

1. **Update English** (`frontend/locales/en/common.json`):
   ```json
   "tools": {
     "sqlTool": {
       "query": "SQL Query",
       "newField": "New Field Label"
     }
   }
   ```

2. **Update Croatian** (`frontend/locales/hr/common.json`):
   ```json
   "tools": {
     "sqlTool": {
       "query": "SQL Upit",
       "newField": "Nova Oznaka Polja"
     }
   }
   ```

## Phase 4: Create Update Specification Document

Create a detailed spec document at `/specs/updates/update-<tool-name>-<timestamp>.md`:

```markdown
# Tool Update: <Tool Name> - <Brief Description>

**Date**: <Current Date>
**Tool**: mcp__algorise__<tool_name>
**Update Type**: [UI Enhancement | Data Structure Change | Backend Logic | Full Stack]

## Update Description

<User's original request>

## Changes Made

### Backend Changes

#### File: algorise/claude_tools/<file>.py
- **Lines Modified**: <line numbers>
- **Changes**:
  - Added `<field>` to return data structure
  - Updated logging to include `<field>`
- **Before**:
  ```python
  <original code>
  ```
- **After**:
  ```python
  <updated code>
  ```

### Frontend Changes

#### File: frontend/src/components/ui/tool.tsx
- **Lines Modified**: <line numbers>
- **Changes**: Added `<field>` to ToolPart type

#### File: frontend/src/components/tools/<ToolRenderer>.tsx
- **Lines Modified**: <line numbers>
- **Changes**:
  - Added new UI section to display `<field>`
  - Used `<icons>` for visual consistency
  - Wrapped in Card component with proper styling

### Translation Changes

#### File: frontend/locales/en/common.json
- **Added Keys**:
  - `tools.<toolName>.<key>`

#### File: frontend/locales/hr/common.json
- **Added Keys**:
  - `tools.<toolName>.<key>`

## Data Flow

```
Backend Tool Function
  └─> Returns: { existing_fields..., new_field: value }
      └─> Callback Handler (if streaming)
          └─> Frontend Type (ToolPart)
              └─> Tool Invocations Hook
                  └─> Renderer Component
                      └─> UI Display
```

## Testing Checklist

- [ ] Backend returns new data field correctly
- [ ] Frontend receives and parses new data
- [ ] UI component displays new field properly
- [ ] English translations show correctly
- [ ] Croatian translations show correctly
- [ ] Existing functionality still works
- [ ] Data persists on page reload (if applicable)
- [ ] Works in both new and existing conversations

## Files Modified

1. `algorise/claude_tools/<file>.py`
2. `frontend/src/components/ui/tool.tsx`
3. `frontend/src/components/tools/<ToolRenderer>.tsx`
4. `frontend/locales/en/common.json`
5. `frontend/locales/hr/common.json`

## Screenshots / Examples

<Describe what the updated UI looks like>

## Additional Notes

<Any special considerations, edge cases handled, or future improvements>
```

## Phase 5: Validation

### 5.1 Verify Changes
- Run grep/search to confirm all changes were made
- Check for syntax errors in modified files
- Ensure no broken imports or references

### 5.2 Test Flow
```bash
# Backend: Check tool is still registered
grep -r "mcp__algorise__<tool_name>" algorise/

# Frontend: Check types compile
cd frontend && npm run type-check

# Check translations exist
grep -r "tools.<toolName>" frontend/locales/
```

### 5.3 Summary Report

Provide a concise summary:
```
✅ Updated <tool_name> tool

Changes:
- Backend: Added <field> to data structure
- Frontend: Updated UI to display <field>
- Translations: Added EN/HR labels for <field>

Modified Files: <count> files
Spec Document: /specs/updates/update-<tool-name>-<timestamp>.md

Ready to test!
```

## Common Update Scenarios

### Scenario 1: Add New Field to UI
- Update backend to include field in return data
- Add field to frontend types
- Update renderer to display field
- Add translations

### Scenario 2: Change UI Layout/Styling
- Only modify renderer component
- No backend or type changes needed
- May need new translation keys

### Scenario 3: Add New Data Source
- Update backend tool to fetch new data
- Add callback handler if streaming
- Update all frontend types
- Create new UI section in renderer
- Add translations

### Scenario 4: Performance Optimization
- Modify backend query/logic
- May need to update data structure
- Frontend may need loading states
- Update spec with performance metrics

## Error Handling

If tool is not found:
```
❌ Tool '<tool_name>' not found in codebase.

Searched:
- algorise/claude_tools/*.py
- frontend/src/components/tools/*.tsx

Available tools:
<list available tools from server.py>

Did you mean: <suggest similar tool names>
```

## Final Checklist

Before completing:
- [ ] All integration points located
- [ ] Changes implemented across stack
- [ ] Translations added (EN + HR)
- [ ] Spec document created in /specs/updates/
- [ ] Files saved and validated
- [ ] Summary provided to user

---

**Let's track down and update your tool!** 🔍
