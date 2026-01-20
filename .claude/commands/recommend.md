## Recommend commands, sub-agents, workflows

Analyze our entire conversation history and identify opportunities to create custom Claude Code commands, sub-agents, or hooks that would improve my workflow.

**Review for:**
- Repetitive tasks or patterns I've asked you to perform multiple times
- Multi-step workflows that follow consistent sequences
- Manual processes that could be automated
- Context-gathering operations across multiple files
- Domain-specific operations unique to my codebase
- Pain points or tedious workflows I've mentioned

**Output Format:**

For each recommendation, provide:

### 🎯 [Command/Sub-Agent Name]
**Purpose:** One-line description of what it does

**Trigger:** When/why you'd use this (the pattern you noticed)

**Suggested Implementation:**
- Command syntax: `/command-name [args]`
- Key steps it should perform
- Files/directories it should check
- Output format

**Priority:** Low/Medium/High (based on frequency and impact)

---

**Guidelines:**
- Only recommend if you found genuine patterns (minimum 2-3 instances)
- Be specific - include actual file paths, patterns, or commands if applicable
- Prioritize high-impact, frequently-used workflows
- Keep each recommendation concise and actionable
- If no patterns found, state: "No significant patterns detected - current workflow seems optimal"

Focus on practical, implementable suggestions that save time and reduce repetition.