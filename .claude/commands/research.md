# Research Command

Create a detailed research specification for a library, technology, or integration.

**Usage**: `/research "topic or library name"`

## Instructions

You will create a comprehensive research document in `specs/01-research/_active/[topic]-research.md`.

When the research is complete:
1. Move to `specs/01-research/_completed/YYYY-MM-[topic].md`
2. If research leads to a feature, create feature spec in `specs/02-features/_planning/`
3. Link the two specs together using frontmatter

## Research Process

### Phase 1: Library Research
- Use `mcp__context7__resolve-library-id` to identify the relevant library
- Use `mcp__context7__get-library-docs` to fetch comprehensive documentation
- Use `mcp__linkup__search-web` for additional context, best practices, and real-world usage
- Research multiple libraries if the topic involves several components

### Phase 2: Codebase Analysis
Review the current system architecture to understand:
- Relevant files and modules that would be affected
- Existing patterns and conventions
- Authentication and authorization mechanisms
- API structure and data flow
- Database schema and models
- Identify integration points and potential conflicts

### Phase 3: Generate Detailed Spec

Create the research document at `specs/01-research/_active/[sanitized-topic-name].md`:

## Research Document Format

```markdown
---
id: research-[nnn]
title: "[Library/Technology Name] Integration Research"
type: research
status: active
created: YYYY-MM-DD
author: [Your Name]
tags: [library, integration, backend/frontend]
---

# [Library/Technology Name] Integration Research

**Research Date**: [Current Date]
**Researched By**: Claude Code
**Status**: Research Phase

## Executive Summary
- Brief overview of what was researched
- Key findings and recommendations
- Estimated complexity and effort
- Go/No-Go recommendation

## Library/Technology Overview
- What it is and what problems it solves
- Key features and capabilities
- Version information and stability
- Community support and maintenance status
- License considerations

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
- Code examples with project patterns
- API endpoints or interfaces

### Phase 3: [Testing & Refinement]
- Testing strategy
- Edge cases to handle
- Performance considerations

## Code Examples
- Show concrete examples using your codebase patterns
- Include imports and type hints
- Follow your coding conventions

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

## Recommendation
[Clear recommendation: Proceed/Don't Proceed/Needs More Investigation]

## Next Steps
1. [Concrete action items]
2. [Who needs to be involved]
3. [What needs approval]

## References
- Documentation links
- Related specs
- Useful resources
- Example implementations
```

## Important Guidelines

- Use TodoWrite to track your research progress
- Be thorough but practical - focus on actionable insights
- Include specific file paths and code examples
- Follow project coding conventions
- Consider existing architecture
- Think about authentication, permissions, and multi-tenancy
- Include error handling and edge cases
- Provide concrete next steps for implementation

## Output

When complete:
1. Research document created in `specs/01-research/_active/[topic].md`
2. Summary of key findings and recommendations
3. Highlight any critical decisions or blockers that need team input

## Topic
$ARGUMENTS
