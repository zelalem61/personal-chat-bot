# Spec Report Command

Generate a report of spec activity for a time period.

**Usage**: `/spec-report <period>`

**Periods**:
- `week` - Last 7 days
- `month` - Last 30 days
- `quarter` - Last 90 days
- `YYYY-MM-DD` - Specific date range

**Examples**:
- `/spec-report week`
- `/spec-report month`
- `/spec-report 2025-01-01 2025-01-31`

## Report Contents

### Overview Statistics
- Total specs by type
- Active specs
- Completed this period
- Velocity metrics

### Completed Work
- Features completed
- Bugs fixed
- Research finished
- Tools created/updated

### Active Work
- Features in progress
- Bugs being fixed
- Research ongoing

### Highlights
- Major accomplishments
- Key decisions made
- Important changes

### Metrics
- Spec completion rate
- Average time to complete
- Bug fix rate
- Feature delivery rate

## Process

### Step 1: Scan Specs
- Read all spec files
- Extract frontmatter metadata
- Filter by date range
- Group by type and status

### Step 2: Calculate Metrics
- Count specs by state
- Calculate completion rates
- Measure time to complete
- Identify trends

### Step 3: Generate Report
- Create markdown report
- Include statistics
- List key accomplishments
- Add visualizations (ASCII charts)

### Step 4: Save Report
- Save to `specs/00-meta/reports/YYYY-MM-[period].md`
- Update latest report link
- Optionally generate summary

## Report Format

```markdown
---
title: "Spec Activity Report - [Period]"
date: YYYY-MM-DD
period: [week|month|quarter|custom]
generated_by: claude-code
---

# Spec Activity Report
**Period**: [Date Range]
**Generated**: [Date Time]

## Executive Summary

[High-level overview of the period's activity]

### Key Highlights
- 🎉 Completed X features
- 🐛 Fixed Y bugs
- 📚 Finished Z research documents
- ⚡ Average completion time: N days

## Statistics

### Overall
- **Total Specs**: X
- **Active**: Y
- **Completed**: Z
- **Archived**: N

### By Type
- **Features**: X total (Y active, Z completed)
- **Bugs**: X total (Y open, Z fixed)
- **Research**: X total (Y active, Z completed)
- **Tools**: X total (Y active, Z deprecated)

### Velocity
- **Features Completed**: X (↑/↓ compared to last period)
- **Bugs Fixed**: Y (↑/↓ compared to last period)
- **Research Completed**: Z
- **Tools Created**: N

## Completed Work

### Features ✅
1. **[feat-001] Chat Image Upload** - Completed YYYY-MM-DD
   - Duration: X days
   - Complexity: High
   - Impact: Users can now upload images in chat

2. **[feat-002] Document Management** - Completed YYYY-MM-DD
   - Duration: Y days
   - Complexity: Medium
   - Impact: Improved document organization

### Bugs Fixed 🐛
1. **[bug-001] Agent Mode Infinite Loop** - Fixed YYYY-MM-DD
   - Severity: High
   - Time to Fix: 2 days
   - Root Cause: Incorrect maxSteps configuration

2. **[bug-002] LocalStorage Performance** - Fixed YYYY-MM-DD
   - Severity: Medium
   - Time to Fix: 1 day
   - Root Cause: Excessive data storage

### Research Completed 📚
1. **Composio MCP Integration** - Completed YYYY-MM-DD
   - Led to: feat-003 (Planned)
   - Key Findings: [Summary]

## Active Work

### Features In Progress 🚧
1. **[feat-003] Advanced Analytics** - 60% complete
   - Started: YYYY-MM-DD
   - Expected: YYYY-MM-DD
   - Blockers: None

2. **[feat-004] Export Functionality** - 30% complete
   - Started: YYYY-MM-DD
   - Expected: YYYY-MM-DD
   - Blockers: Waiting on feat-003

### Bugs In Progress 🔧
1. **[bug-003] API Timeout Issues** - In Progress
   - Severity: Medium
   - Started: YYYY-MM-DD
   - Status: Root cause identified, implementing fix

## Planning & Backlog

### Features Planned
1. **[feat-005] Mobile App** - In Planning
   - Research: Completed
   - Estimated: 8 weeks
   - Priority: High

2. **[feat-006] Advanced Search** - In Backlog
   - Estimated: 4 weeks
   - Priority: Medium

### Open Bugs
1. **[bug-004] UI Flickering** - Open
   - Severity: Low
   - Reported: YYYY-MM-DD
   - Assigned: Unassigned

## Time Analysis

### Average Time to Complete
- **Features**: X days (median)
- **Bugs**: Y days (median)
- **Research**: Z days (median)

### Longest Running
- **Feature**: [feat-XXX] - N days in progress
- **Bug**: [bug-XXX] - M days open

## Trends

### Completion Rate
```
Week 1: ████████░░ 80%
Week 2: ███████░░░ 70%
Week 3: █████████░ 90%
Week 4: ████████░░ 80%
```

### Bug Arrival vs Fix Rate
```
Opened:  ██████ 6
Fixed:   ████████ 8
Net:     -2 (good!)
```

## Quality Metrics

### Test Coverage
- Unit Tests: 85% coverage
- Integration Tests: 70% coverage
- E2E Tests: 60% coverage

### Bug Severity Distribution
- Critical: 0 (0%)
- High: 2 (20%)
- Medium: 5 (50%)
- Low: 3 (30%)

## Architecture Decisions

### ADRs Created
1. **ADR-001**: Use Composio for MCP integration
   - Date: YYYY-MM-DD
   - Impact: High

2. **ADR-002**: Migrate to new state management
   - Date: YYYY-MM-DD
   - Impact: Medium

## Tooling Updates

### Tools Created
1. **execute_sql_query** - Created YYYY-MM-DD
2. **generate_chart** - Created YYYY-MM-DD

### Tools Updated
1. **get_user_collections** - Updated to show collection stats
2. **vector_search** - Performance improvements

## Recommendations

### For Next Period
1. Focus on completing in-progress features before starting new ones
2. Allocate time to reduce bug backlog
3. Consider additional testing for high-severity bugs
4. Update documentation for recently completed features

### Process Improvements
1. Improve spec templates based on usage
2. Add more granular status tracking
3. Implement automated status updates

## Appendix

### All Specs Modified This Period
- [Full list with links]

### Contributors
- [List of people who worked on specs]
```

## Output Location

Report saved to:
```
specs/00-meta/reports/YYYY-MM-[period].md
```

Update link in INDEX.md:
```
Latest Report: [2025-01 Monthly](reports/2025-01-monthly.md)
```

## Usage Example

```bash
$ /spec-report week

Generating spec report for last 7 days...
Scanning specs...
Calculating metrics...
Creating report...

✅ Report generated: specs/00-meta/reports/2025-01-week-2.md

Summary:
- Completed: 3 features, 5 bugs
- Active: 4 features, 2 bugs
- Velocity: +20% vs last week
```
