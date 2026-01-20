# Extract Design System

Extract a comprehensive design system guide from the frontend application for use with external tools like Lovable, Bolt, or v0.

**Usage**: `/extract-design`

## What This Does

This command launches the **design-system-extractor** subagent which will:

1. Analyze your entire frontend codebase
2. Extract all design patterns, colors, typography, components, spacing, animations, and responsive behavior
3. Generate a complete, copy-paste-ready design guide
4. Save the guide to `specs/design-system/design-system-guide.md`

The resulting guide can be pasted directly into prompts for external AI tools to ensure they match your platform's look and feel.

## Output

You'll receive a comprehensive Markdown document covering:

- Complete color system (light/dark mode)
- Typography scale and font configuration
- All component variants (buttons, inputs, cards, etc.)
- Spacing and layout patterns
- Icon usage guidelines
- Animation and transition patterns
- Responsive design breakpoints
- Tailwind configuration reference
- CSS custom properties
- Real component composition examples
- Usage guide for external tools

## Instructions

Launch the design-system-extractor subagent to perform the analysis:

$INVOKE_AGENT design-system-extractor

Once complete, save the generated guide to `specs/design-system/design-system-guide.md` and provide a summary of key findings.
