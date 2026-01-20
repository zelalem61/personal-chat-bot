# Create New Tool - Complete Implementation Guide

You are tasked with implementing a new tool for the Algorise application. Follow this comprehensive checklist to ensure all components are properly integrated.

## Context Understanding

First, analyze the user's tool requirements:
- What does the tool do?
- What data does it need?
- What output does it produce?
- Does it need visualization?
- Does it stream data to the frontend?

## Implementation Checklist

### Phase 1: Backend Tool Implementation

#### 1.1 Create Tool Function (Python)
**Location**: `algorise/claude_tools/` (create new file or add to existing)

**Requirements**:
- Use `@tool()` decorator from `claude_agent_sdk`
- Include tool name, description, and input schema
- Add comprehensive logging with prefixed tags (e.g., `[TOOL NAME]`)
- Handle input validation (strings vs objects, JSON parsing)
- Return proper error responses with `is_error: True`

**Template**:
```python
from claude_agent_sdk import tool
from algorise.logs import logger
import json
from typing import Any

@tool("tool_name", "Tool description", {"param1": str, "param2": list})
async def tool_name(args: dict[str, Any]) -> dict[str, Any]:
    """
    Detailed docstring explaining:
    - What the tool does
    - Args and their types
    - Return format
    """
    try:
        # Extract and validate arguments
        param1 = args.get("param1", "")
        param2 = args.get("param2", [])

        logger.info(f"[TOOL NAME] Starting - param1: {param1}")

        if not param1:
            logger.warning("[TOOL NAME] Missing required parameter")
            return {"content": [{"type": "text", "text": "Error: param1 required"}], "is_error": True}

        # Handle JSON string inputs if needed
        if isinstance(param2, str):
            logger.info("[TOOL NAME] Parsing param2 from JSON")
            try:
                param2 = json.loads(param2)
            except json.JSONDecodeError as e:
                logger.error(f"[TOOL NAME] Invalid JSON: {e}")
                return {"content": [{"type": "text", "text": "Error: Invalid JSON"}], "is_error": True}

        # Main tool logic here
        result_data = {}  # Your actual computation

        # Stream structured data if needed (see Phase 2)
        callback = _stream_callback.get()
        if callback and result_data:
            logger.info("[TOOL NAME] Streaming data to frontend")
            await callback.handle_custom_data(result_data)

        # Format text output for Claude
        output = ["Tool Results:", f"Processed {param1}"]

        logger.info("[TOOL NAME] ✅ Complete")
        return {"content": [{"type": "text", "text": "\n".join(output)}]}

    except Exception as e:
        logger.error(f"[TOOL NAME] ❌ Error: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "is_error": True}
```

#### 1.2 Register Tool in MCP Server
**Location**: `algorise/claude_tools/server.py`

Add imports and register:
```python
from algorise.claude_tools.your_module import your_tool

all_tools = [
    # ... existing tools
    your_tool,  # Add here
]
```

#### 1.3 Add to Allowed Tools
**Location**: `algorise/services/claude_chat_service.py`

Add to both allowed_tools lists (non-streaming and streaming):
```python
allowed_tools=[
    # ... existing tools
    "mcp__algorise__your_tool",
],
```

### Phase 2: Callback Handler (if streaming structured data)

#### 2.1 Add Callback Protocol Method
**Location**: `algorise/core/claude_callback.py`

Add to `ClaudeStreamHandler` protocol:
```python
async def handle_your_data(self, data: list[dict[str, Any]]) -> None:
    """Handle your custom data for UI rendering"""
    ...
```

Add to `ClaudeStreamCallback` class:
```python
async def handle_your_data(self, data: list[dict[str, Any]]) -> None:
    """Stream your custom data"""
    await self.handler.handle_your_data(data)
```

#### 2.2 Implement SSE Streaming
**Location**: `algorise/core/claude_callback.py` in `ClaudeSSEStreamHandler`

```python
async def handle_your_data(self, data: list[dict[str, Any]]) -> None:
    """
    Handle your custom data using Vercel data part format.

    Format: 2:[{"type":"yourDataType","data":[...]}]\n
    """
    if data:
        logger.info(f"[CLAUDE SSE] Streaming {len(data)} your data items")
        your_data = {"type": "yourDataType", "data": data}
        await self.queue.put(f'2:[{json.dumps(your_data)}]\n')
```

#### 2.3 Add to CapturingCallbackWrapper
**Location**: `algorise/services/claude_chat_service.py`

In the `CapturingCallbackWrapper` class:
```python
async def handle_your_data(self, data: list[dict[str, Any]]) -> None:
    # Capture your data for the current tool
    if self.current_tool_id and self.current_tool_id not in self.capture_dict:
        self.capture_dict[self.current_tool_id] = {}
    if self.current_tool_id:
        self.capture_dict[self.current_tool_id]["yourData"] = {"data": data}
    await self.wrapped.handle_your_data(data)
```

### Phase 3: Frontend Type Definitions

#### 3.1 Add to ToolPart Type
**Location**: `frontend/src/components/ui/tool.tsx`

```typescript
export type ToolPart = {
  // ... existing fields
  yourData?: {
    data: Array<{
      field1: string
      field2: number
      // ... your data structure
    }>
  }
}
```

#### 3.2 Add Interface to Streaming Hook
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts`

Add interface at top:
```typescript
interface YourData {
  data: Array<{
    field1: string
    field2: number
  }>
}
```

Add to `UseChatStreamingReturn`:
```typescript
interface UseChatStreamingReturn {
  // ... existing fields
  messageYourData: Record<string, YourData>;
  setMessageYourData: (data: Record<string, YourData> | ((prev: Record<string, YourData>) => Record<string, YourData>)) => void;
}
```

### Phase 4: Frontend Data Flow

#### 4.1 Add State Management
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts`

Add state:
```typescript
const [messageYourData, setMessageYourData] = useState<Record<string, YourData>>(() => {
  if (typeof window !== 'undefined' && chatId) {
    const stored = localStorage.getItem(`chat_${chatId}_yourData`);
    return stored ? JSON.parse(stored) : {};
  }
  return {};
});
```

#### 4.2 Add Parsing Logic
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts` in the data parsing `useEffect`

```typescript
// Parse your custom data
if (item && typeof item === 'object' && !Array.isArray(item) && 'type' in item &&
    item.type === 'yourDataType' && 'data' in item) {
  const yourData = { data: item.data as any[] };
  if (messages.length > 0) {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role === 'assistant') {
      setMessageYourData(prev => ({...prev, [lastMessage.id]: yourData}));
    }
  }
}
```

#### 4.3 Add Initial Data Loading
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts` in the messages loading `useEffect`

```typescript
const newYourData: Record<string, YourData> = {};

// Inside the loop over messages and tool invocations:
if (invocation.toolName === 'mcp__algorise__your_tool') {
  if ((invocation as any).yourData) {
    newYourData[message.id] = (invocation as any).yourData;
  }
}

// After the loop:
if (Object.keys(newYourData).length > 0) {
  setMessageYourData(prev => ({...prev, ...newYourData}));
}
```

#### 4.4 Add LocalStorage Persistence
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts`

```typescript
useEffect(() => {
  if (typeof window !== 'undefined' && chatId && Object.keys(messageYourData).length > 0) {
    localStorage.setItem(`chat_${chatId}_yourData`, JSON.stringify(messageYourData));
  }
}, [messageYourData, chatId]);
```

#### 4.5 Add to Return Statement
**Location**: `frontend/src/hooks/chat/useChatStreaming.ts`

```typescript
return {
  // ... existing returns
  messageYourData,
  setMessageYourData,
};
```

### Phase 5: Tool Invocations Hook

#### 5.1 Add Interface
**Location**: `frontend/src/hooks/chat/useToolInvocations.ts`

```typescript
interface YourData {
  data: Array<{
    field1: string
    field2: number
  }>
}
```

#### 5.2 Add to Function Parameters
**Location**: `frontend/src/hooks/chat/useToolInvocations.ts`

```typescript
export function useToolInvocations(
  messages: Message[],
  isLoading: boolean,
  // ... existing parameters
  messageYourData: Record<string, YourData>
): Record<string, ToolPart[]> {
```

#### 5.3 Extract and Attach Data
**Location**: `frontend/src/hooks/chat/useToolInvocations.ts` inside the tool loop

```typescript
const isYourTool = toolName === 'mcp__algorise__your_tool';
const toolYourData = isYourTool ? messageYourData[message.id] : undefined;

// In hasResults check:
const hasResults = !!(result || ... || toolYourData);

// In messageTools.push:
messageTools.push({
  // ... existing fields
  yourData: toolYourData,
});
```

#### 5.4 Add to Dependencies
**Location**: `frontend/src/hooks/chat/useToolInvocations.ts`

```typescript
}, [messages, isLoading, ..., messageYourData]);
```

### Phase 6: Update Chat Interface

#### 6.1 Thread Data Through
**Location**: `frontend/src/components/chat/v2/ChatInterfaceRefactored.tsx`

Destructure from useChatStreaming:
```typescript
const {
  // ... existing
  messageYourData,
  setMessageYourData,
} = useChatStreaming(...);
```

Pass to useToolInvocations:
```typescript
const toolInvocations = useToolInvocations(
  messages,
  isLoading,
  // ... existing parameters
  messageYourData
);
```

### Phase 7: Create UI Renderer Component

#### 7.1 Create Renderer Component
**Location**: `frontend/src/components/tools/YourToolRenderer.tsx`

```typescript
"use client"

import { Icon1, Icon2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { useTranslation } from "@/lib/i18n"
import type { ToolPart } from "@/components/ui/tool"

interface YourToolRendererProps {
  toolPart: ToolPart
}

export function YourToolRenderer({ toolPart }: YourToolRendererProps) {
  const { t } = useTranslation('common')

  if (!toolPart.yourData) return null

  const { data } = toolPart.yourData

  if (!data || data.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        {t('tools.yourTool.noData')}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Icon1 className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium text-primary">
          Your Tool Results
        </span>
        <Badge variant="outline" className="text-xs px-1.5 py-0 h-5">
          {data.length} {data.length === 1 ? 'item' : 'items'}
        </Badge>
      </div>

      {/* Content - follow patterns from existing renderers */}
      <div className="rounded-lg border bg-card p-4">
        {data.map((item, index) => (
          <div key={index}>
            {/* Render your data */}
          </div>
        ))}
      </div>
    </div>
  )
}
```

#### 7.2 Register in Tool Registry
**Location**: `frontend/src/components/tools/registry.tsx`

```typescript
import { YourToolRenderer } from "./YourToolRenderer"

export const toolRegistry: Record<string, ToolRenderer> = {
  // ... existing tools
  'mcp__algorise__your_tool': YourToolRenderer,
}
```

### Phase 8: Add Translations

#### 8.1 English Translations
**Location**: `frontend/locales/en/common.json`

```json
"tools": {
  "names": {
    // ... existing
    "mcp__algorise__your_tool": "Your Tool Name"
  },
  "descriptions": {
    // ... existing
    "mcp__algorise__your_tool": "Description of what the tool does"
  },
  "yourTool": {
    "noData": "No data available",
    "field1Label": "Field 1",
    "field2Label": "Field 2"
  }
}
```

#### 8.2 Croatian Translations
**Location**: `frontend/locales/hr/common.json`

```json
"tools": {
  "names": {
    // ... existing
    "mcp__algorise__your_tool": "Naziv Alata"
  },
  "descriptions": {
    // ... existing
    "mcp__algorise__your_tool": "Opis što alat radi"
  },
  "yourTool": {
    "noData": "Nema dostupnih podataka",
    "field1Label": "Polje 1",
    "field2Label": "Polje 2"
  }
}
```

### Phase 9: Update System Prompt (Optional)

**Location**: `algorise/services/claude_chat_service.py`

If the tool needs specific guidance, add to `ALGORISE_SYSTEM_PROMPT`:
```python
YOUR TOOL USAGE:
- Use your_tool(param1="value") to perform X
- The tool returns Y format
- Best used when user asks about Z
```

### Phase 10: Testing & Validation

Run through this checklist:
- [ ] Backend tool executes successfully
- [ ] Logging shows proper flow with prefixed tags
- [ ] Data streams to frontend via callback
- [ ] Frontend parses streamed data correctly
- [ ] Data persists in localStorage
- [ ] Data reloads correctly on page refresh
- [ ] UI component renders properly
- [ ] Tool name shows translated (not raw key)
- [ ] English translations work
- [ ] Croatian translations work
- [ ] Error cases are handled gracefully
- [ ] Tool works in both new and resumed conversations

## Reference Files

For examples, refer to the chart generation implementation:
- **Backend**: `algorise/claude_tools/retail_chart_tools.py`
- **Callback**: `algorise/core/claude_callback.py:304-313`
- **Streaming Hook**: `frontend/src/hooks/chat/useChatStreaming.ts:143-149, 375-385`
- **Tool Invocations**: `frontend/src/hooks/chat/useToolInvocations.ts:112-113, 144`
- **UI Component**: `frontend/src/components/tools/ChartRenderer.tsx`
- **Registry**: `frontend/src/components/tools/registry.tsx:42`
- **Translations**: `frontend/locales/en/common.json:105-106, 117-118`

## Common Pitfalls to Avoid

1. **Forgetting to add tool to BOTH allowed_tools lists** (streaming & non-streaming)
2. **Not handling string vs object inputs** (JSON parsing)
3. **Missing callback wrapper method** (CapturingCallbackWrapper)
4. **Forgetting localStorage persistence**
5. **Not adding to dependency arrays** in hooks
6. **Missing translations** (shows raw key instead)
7. **Not using `useTranslation('common')`** in renderer
8. **Inconsistent naming** between backend and frontend type names

## Final Check

Before marking the tool as complete:
1. Test with a real user query
2. Verify data flows end-to-end
3. Check browser DevTools for errors
4. Verify backend logs show proper flow
5. Test language switching (EN ↔ HR)
6. Test conversation persistence (reload page)
7. Verify tool works in both new and existing chats

---

**Ready to implement? Let's build your tool step by step!** 🚀
