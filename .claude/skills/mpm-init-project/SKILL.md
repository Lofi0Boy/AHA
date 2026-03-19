---
name: mpm-init-project
description: Analyze the project and write PROJECT.md through automatic scanning and user interview.
disable-model-invocation: true
---

# Initialize PROJECT.md

## Step 1: Automatic project scan

Scan the following to understand the project before asking anything:

- `README.md` — project description
- `package.json` / `pyproject.toml` / `Cargo.toml` etc. — tech stack, dependencies
- Directory structure (1-2 levels deep) — project scale and layout
- `docs/` and all `.md` files in the project — existing documentation
- `CLAUDE.md`, `.claude/rules/` — existing development rules
- Recent git log (last 10 commits) — recent work direction

## Step 2: Share your understanding

Present what you've learned to the user:
- "This project appears to be ... Is that correct?"
- Share your understanding of the tech stack, modules, and current state.

## Step 3: Targeted interview

Only ask about what the scan didn't reveal:
- Core purpose (why does this project exist?)
- Current progress (what's done so far?)
- Future direction (what's planned next?)
- Do NOT re-ask things already clear from the scan.

## Step 4: Write PROJECT.md

Write to `.mpm/docs/PROJECT.md`.

**Required structure:**
```markdown
# Project Name (MUST be in English)

First paragraph is the project description (displayed on the dashboard header).

## ... (optional sections — content can be any language)
```

**IMPORTANT:** The `# heading` (project name) MUST be written in English — MPM uses it as a machine-readable identifier. The description and body content can be in any language.

The dashboard parses:
- **`# heading`** → project display name (English required)
- **First non-empty line after `#`** (before any `##`) → description

Everything after is free-form — cover identity, current state, and direction as needed.

Show the result to the user and save after confirmation.
Always respond in the user's language.
