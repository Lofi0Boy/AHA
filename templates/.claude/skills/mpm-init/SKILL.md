---
name: mpm-init
description: Initialize a new MPM project — Create foundation documents, set up Phase, Goals and Tasks.
---

# Initialize MPM Project

Before starting, briefly explain to the user what will happen:

> "To help agents work more consistently on your project, I'll walk through an initial setup.

Then proceed through the following steps **in order**. Each step must be completed before moving to the next.

At the start of each step, briefly tell the user **what this step is and why it matters** in one sentence. Do not use internal terms like "Layer" or "PPGT" — just explain in plain language.

---

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

## Step 3: Project Documentation

> Tell the user: "Now we'll define your project clearly so all agents share the same understanding. This goes through a structured process — product definition, strategic review, then engineering review."

Run the following skills **in order**. Each skill is a conversation — complete it fully before moving to the next.

### 3a. `/mpm-office-hour`

Product definition. Understands the problem, challenges assumptions, generates a design document.

After completion, a design doc is saved to `.mpm/gstack/design-{datetime}.md`.

### 3b. `/mpm-plan-ceo-review`

Strategic review. Challenges scope, maps the 12-month ideal, validates premises.

After completion, a CEO plan may be saved to `.mpm/gstack/ceo-plans/`.

### 3c. `/mpm-plan-eng-review`

Engineering review. Locks in architecture, data flow, test strategy, edge cases.

### 3d. Write foundation documents

After the three reviews are complete, synthesize the accumulated insights into foundation documents:

1. **`.mpm/docs/PROJECT.md`** — Problem, users, demand evidence, vision, scope, success criteria (from office-hour + CEO review)
2. **`.mpm/docs/ARCHITECTURE.md`** — System design, component boundaries, data flow, tech decisions, deployment strategy (from eng review)

Present both documents to the user for approval before writing.

## Step 4: Design Documentation

> Tell the user: "If your project has a user interface, we'll set up a design system now. If it's backend-only, we can skip this."

Ask the user: "Does this project have a user-facing interface (web, mobile, dashboard, etc.)?"

- **If yes:** Run `/mpm-init-design`. This creates `.mpm/docs/DESIGN.md` and `.mpm/docs/tokens/`.
- **If no:** Skip this step.

## Step 5: VERIFICATION.md

> Tell the user: "This document defines how agents can verify their own work without asking you — so they can self-check before reporting done."

1. Inspect available verification tools in the project:
   - Test frameworks (pytest, jest, etc.)
   - API endpoints (curl targets)
   - Build commands
   - Browser tools (ex-headless chrome, Claude in Chrome, etc)
2. Ask the user: "Are there additional ways you can self-verify without asking anyone?"
3. Write to `.mpm/docs/VERIFICATION.md`


## Step 6: Define Phase 1

> Tell the user: "A Phase is a milestone — a concrete, verifiable goal you want to reach. Let's define the first one."

Ask the user what they want to achieve first. Based on their answer:
1. Propose a Phase name and verifiable completion state
2. User approves or corrects

Only Phase 1 is required at init. More phases can be added later.


Then create the Phase using `phase.py`:

```bash
python3 .mpm/scripts/phase.py add "Phase Name" "Verifiable completion state description"
```

This stores the Phase in `.mpm/data/phases.json` as structured data.

## Step 7: Define Goals and Tasks for Phase 1

> Tell the user: "Now I'll break down the Phase into Goals (what users get) and Tasks (what agents build). I'll show you the full plan for review before creating anything."

### 7a. Draft Goals

Based on the Phase definition and foundation documents:
1. Draft Goal items from the user's perspective
2. Present the full Goal list to the user for review
3. User approves, corrects, or requests changes
4. **Do not create Goals until user approves**

### 7b. Draft Tasks per Goal

For each approved Goal:
1. Break down into Tasks following `/mpm-task-write` skill guidelines (single function, 1–2 evidence items)
2. Present all Tasks grouped by Goal to the user:
   - Show: title, goal (acceptance criteria), verification method
   - Show dependency order if any
3. User approves, corrects, or requests changes
4. **Do not create Tasks until user approves the full plan**

### 7c. Create Goals and Tasks

Only after user approval of both Goals and Tasks:

```bash
# Create Goals
python3 .mpm/scripts/phase.py goal-add <phase_id> "Goal description from user perspective"

# Create Tasks (per Goal)
python3 .mpm/scripts/task.py add "task title" "prompt" --goal "criteria" --verification "method" --goal-id <goal_id>
```

Show the final created list to the user.

---

Always respond in the user's language.
