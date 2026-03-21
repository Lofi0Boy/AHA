---
name: mpm-task-write
description: Create well-structured tasks for developer agents with proper Outcome/Context/Verification format.
---

# Write Tasks

Create tasks that developer agents can execute autonomously.

---

## Required Task prompt structure

```
## Outcome
State that must be true on completion. WHAT, not HOW.

## Context
- File paths to read
- Existing patterns to follow
- Design tokens/components to reference (sections in DESIGN.md)
- Architecture conventions to follow (sections in ARCHITECTURE.md)

## Verification
Executable verification methods (curl, test, screenshot, etc.)

## Non-goals
What is explicitly out of scope.
```

---

## Principles

- **Outcome over process.** Describe "what"; the developer agent decides "how".
- **Be specific.** "`/health` endpoint returns `{status: 'ok'}`" > "Add health checking"
- **Check upward consistency.** Always verify the Task aligns with its Goal, Phase, and Project purpose.
- **Reference ADV documents.** Include relevant ARCHITECTURE.md conventions and DESIGN.md tokens in Context.

---

## On UI/UX Tasks

When a Task involves UI changes, `.mpm/docs/DESIGN.md` must be referenced.

**Include in Context:**
- Design tokens to apply (colors, typography, spacing, etc.)
- Existing component patterns to reuse and their code paths
- Layout principles relevant to this Task

**If DESIGN.md is missing or incomplete:**
- Do not create UI Tasks without design criteria
- Run `/mpm-init-design` skill first

**If a Task needs tokens not yet defined in DESIGN.md:**
- Create new tokens that are **aligned with existing ones** (same scale, naming convention, color palette)
- Add the new tokens to DESIGN.md before or alongside the Task
- Never introduce ad-hoc values that bypass the token system

---

## On Verification

**Always check `.mpm/docs/VERIFICATION.md` first** for project-specific verification methods.

Available verification methods:

| Method | Use case | Example |
|--------|----------|---------|
| curl + parse | API response check | `curl -s localhost:5100/api/projects \| jq .field` |
| Run tests | Logic verification | `pytest tests/test_auth.py` |
| Script execution | Output check | `python3 script.py && echo OK` |
| File inspection | Creation/modification check | Verify file contains expected content |
| Chrome | Static visual check | `google-chrome --headless --screenshot=...` |
| Browser automation | Dynamic UI check | Claude in Chrome, etc. |
| User confirmation | **Last resort** | Only when above methods cannot verify |

**Bad:** "Verify the feature works correctly"
**Good:** "`curl -s localhost:5100/api/sessions | jq length` is 1 or more, and screenshot shows the terminal panel"

---

## Command

```bash
python3 .mpm/scripts/task.py add "task title" "## Outcome
...

## Context
...

## Verification
...

## Non-goals
..."
```

---

Always respond in the user's language.
