## Research Library Integration

You are tasked with researching a library or technology and creating a detailed integration specification for our system.

**Research Topic:** {PROMPT_ARGUMENT}

**Your Task:**

1. **Library Research Phase:**
   - Use the `mcp__context7__resolve-library-id` tool to identify the relevant library
   - Use the `mcp__context7__get-library-docs` tool to fetch comprehensive documentation
   - If the topic involves multiple libraries or components, research each one thoroughly
   - Use `mcp__linkup__search-web` for additional context about implementation patterns, best practices, and real-world usage

2. **Codebase Analysis Phase:**
   - Review our current system architecture to understand:
     - Relevant files and modules that would be affected
     - Existing patterns and conventions we follow
     - Authentication and authorization mechanisms
     - API structure and data flow
     - Database schema and models
   - Identify integration points and potential conflicts

3. **Generate Detailed Spec:**
   - Create a comprehensive specification document in `specs/research/`
   - Use a sanitized filename based on the research topic (lowercase, hyphens, no special chars)
   - Follow this structure:

```markdown
# [Library/Technology Name] Integration Research

**Research Date:** [Current Date]
**Researched By:** Claude Code
**Status:** Research Phase

## Executive Summary
- Brief overview of what was researched
- Key findings and recommendations
- Estimated complexity and effort

## Library/Technology Overview
- What it is and what problems it solves
- Key features and capabilities
- Version information and stability
- Community support and maintenance status

## Current System Analysis
- Relevant parts of our codebase
- Current implementation patterns
- Existing similar functionality or conflicts
- Technical constraints and requirements

## Integration Architecture
- Proposed integration approach
- System architecture diagrams (in text/ASCII if needed)
- Data flow and interaction patterns
- Component responsibilities

## Implementation Proposal

### Phase 1: [Initial Setup/Foundation]
- Detailed steps
- Files to create/modify
- Dependencies to add
- Configuration changes

### Phase 2: [Core Integration]
- Implementation details
- Code examples with our patterns
- API endpoints or interfaces

### Phase 3: [Testing & Refinement]
- Testing strategy
- Edge cases to handle
- Performance considerations

## Code Examples
- Show concrete examples using our codebase patterns
- Include imports, type hints (Python 3.11+ style)
- Follow our coding conventions from CLAUDE.md

## Dependencies & Requirements
- New packages/libraries needed
- Version requirements
- Environment variables
- Infrastructure changes

## Security Considerations
- Authentication/authorization impacts
- Data privacy concerns
- API key management
- Rate limiting and quotas

## Testing Strategy
- Unit tests needed
- Integration tests
- Manual testing checklist
- Performance benchmarks

## Migration Path
- Steps to migrate existing functionality (if applicable)
- Backwards compatibility considerations
- Rollback strategy

## Risks & Challenges
- Technical risks
- Integration challenges
- Maintenance concerns
- Alternative approaches

## Timeline & Effort Estimate
- Estimated development time
- Key milestones
- Dependencies on other work

## Open Questions
- Unresolved technical questions
- Decisions needed from team
- Areas needing further research

## References
- Documentation links
- Related specs
- Useful resources
- Example implementations
```

**Important Guidelines:**

- Use TodoWrite to track your research progress through these phases
- Be thorough but practical - focus on actionable insights
- Include specific file paths and code examples from our codebase
- Follow our Python coding conventions (3.11+ type hints, no Optional/Dict/List imports)
- Consider our existing architecture (FastAPI backend, React frontend, Supabase, etc.)
- Think about authentication, permissions, and multi-tenancy
- Include error handling and edge cases
- Provide concrete next steps for implementation

**Output:**
- Create the spec file in `specs/research/[sanitized-topic-name].md`
- Provide a summary of key findings and recommendations
- Highlight any critical decisions or blockers that need team input
