---
name: mpm-review-code
description: Code quality review — architecture compliance, DRY, security, error handling, complexity.
---

# Code Review

> **Review context (injected by reviewer):**
> - **Task fields** — `goal` (acceptance criteria), `prompt` (context + non-goals), `verification` (how to check). These define what was requested. Judge against them exactly.
> - **`.mpm/docs/ARCHITECTURE.md`** — primary criteria for code structure, patterns, conventions.
> - **`.mpm/docs/PROJECT.md`** — product vision. Code that works but doesn't serve the product direction should be flagged.
> - **`.mpm/docs/VERIFICATION.md`** — check if the dev used the correct verification methods.

## 1. Architecture compliance

Check against the injected ARCHITECTURE.md:
- Does the code follow the stated patterns? (naming, module structure, data flow)
- Are new files in the right directories?
- Does the code respect component boundaries?

## 2. Error handling

- Are exceptions named and specific? (not catch-all `except Exception`)
- Does every error path produce a meaningful message?
- Are errors logged with context? (what was attempted, with what input)
- No "swallow and continue" — every caught error must retry, degrade gracefully, or re-raise

## 3. DRY violations

```bash
# Check for duplicated logic in changed files
git diff --name-only | head -20
```
Read each changed file. Flag:
- Copy-pasted blocks that should be a function
- Logic that already exists elsewhere in the codebase (grep for similar patterns)

## 4. Security

- **Injection**: SQL, command, template, XSS — check user input handling
- **Secrets**: no hardcoded credentials, API keys, passwords
  ```bash
  git diff | grep -iE 'password|secret|api_key|token.*=.*["\x27]' | head -10
  ```
- **Auth**: new endpoints have proper authorization checks
- **Dependencies**: new packages have known vulnerabilities?

## 5. Complexity

- Methods with >5 branches → suggest refactor
- New abstractions solving problems that don't exist yet → flag over-engineering
- Missing defensive checks on external input → flag under-engineering

## Return format

```
CODE REVIEW: PASS/FAIL
Issues:
- [issue 1: what's wrong + file:line + how to fix]
- [issue 2: ...]
```
