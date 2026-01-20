# Spec Move Command

Move a specification to a new lifecycle state.

**Usage**: `/spec-move <spec-id-or-name> <new-state>`

**Examples**:
- `/spec-move feat-001 in-progress`
- `/spec-move bug-agent-loop fixed`
- `/spec-move composio-research completed`

## Valid States by Spec Type

### Research
- `active` → Currently researching
- `completed` → Research finished
- `archive` → Outdated or superseded

### Features
- `backlog` → Not started
- `planning` → Being planned
- `in-progress` → Actively implementing
- `completed` → Done & deployed
- `archive` → Cancelled or superseded

### Bugs
- `open` → Not fixed yet
- `in-progress` → Being fixed
- `fixed` → Fixed & deployed
- `wont-fix` → Decided not to fix

### Tools
- `active` → Currently in use
- `deprecated` → No longer recommended

## Process

### Step 1: Find Spec
- Search for spec by ID or name
- Look in current state directories
- Check frontmatter for spec ID

### Step 2: Validate Move
- Ensure new state is valid for spec type
- Check if spec file exists
- Verify state transition is logical

### Step 3: Move File
- Move file to new state directory
- Update filename if needed:
  - Completed/Fixed: Add `YYYY-MM-` prefix
  - In-progress/Open: Remove date prefix
- Preserve file contents

### Step 4: Update Metadata
- Update `status` in frontmatter
- Update `updated` date in frontmatter
- Add state change to history if exists

### Step 5: Update Index
- Update `specs/00-meta/INDEX.md`
- Reflect new state in statistics
- Update active work section

### Step 6: Commit
```bash
git add specs/
git commit -m "chore(specs): Move [spec-id] to [new-state]"
```

## Examples

### Move Feature to In Progress
```bash
/spec-move feat-chat-images in-progress
```

**Actions**:
- Move: `specs/02-features/_planning/feat-chat-images.md`
- To: `specs/02-features/_in-progress/feat-chat-images.md`
- Update frontmatter: `status: in-progress`
- Update INDEX.md

### Move Bug to Fixed
```bash
/spec-move bug-infinite-loop fixed
```

**Actions**:
- Move: `specs/03-bugs/_in-progress/bug-infinite-loop.md`
- To: `specs/03-bugs/_fixed/2025-01-11-bug-infinite-loop.md`
- Update frontmatter: `status: fixed`
- Update INDEX.md

### Move Research to Completed
```bash
/spec-move composio-research completed
```

**Actions**:
- Move: `specs/01-research/_active/composio-research.md`
- To: `specs/01-research/_completed/2025-01-composio-research.md`
- Update frontmatter: `status: completed`
- Update INDEX.md

## Error Handling

**Spec not found**:
```
❌ Spec '[spec-name]' not found.

Searched:
- specs/02-features/_planning/
- specs/02-features/_in-progress/
- specs/02-features/_backlog/

Available specs:
- feat-001: Chat Images
- feat-002: Document Management
```

**Invalid state**:
```
❌ Invalid state 'foo' for feature spec.

Valid states for features:
- backlog
- planning
- in-progress
- completed
- archive
```

**Spec already in state**:
```
ℹ️ Spec 'feat-001' is already in state 'in-progress'.
No action needed.
```

## Output

```
✅ Moved [spec-type] '[spec-id]' from '[old-state]' to '[new-state]'

File moved:
  From: specs/[type]/_[old-state]/[filename]
  To:   specs/[type]/_[new-state]/[new-filename]

Updated:
  - Frontmatter status
  - Frontmatter updated date
  - INDEX.md

Ready to commit:
  git commit -m "chore(specs): Move [spec-id] to [new-state]"
```
