---
description: Review conversation history and commit recent changes
---

Review our conversation history to understand what features or changes we've been working on. Then:

1. Run `git status` and `git diff` to see all changes
2. Analyze the changes in context of our conversation
3. Stage all relevant files with `git add`
4. Create a concise, informative commit message that describes WHAT was changed and WHY
5. The commit message should:
   - Be clear and descriptive
   - Focus on the user-facing changes or technical improvements
   - NOT include any signatures, credits, or "Generated with" footers
   - Follow conventional commit format if appropriate (feat:, fix:, refactor:, etc.)
6. Commit the changes with `git commit -m "your message"`
7. Show the commit summary with `git log -1 --stat`

IMPORTANT: Do NOT include any AI assistant signatures, credits, or "Co-Authored-By" lines in the commit message.

IMPORTANT: Never do git add -A or take all the files. check just what is relevant to the feature/bug or whatever we were doing. Whats not relevant to that can remain uncommited.
For example, I sometimes have some local docker changes, or docker ocmpose changes so leave thouse out of it if they were not specifically changed to support this feature/bug.
