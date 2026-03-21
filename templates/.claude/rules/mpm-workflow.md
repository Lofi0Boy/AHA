# MPM System

This project uses the MPM system for project planning and task management.

---

## PPGT Hierarchy

Projects are planned in a 4-level hierarchy. Higher levels are human-driven, lower levels are AI-autonomous.

```
Project ── Why the project exists, its purpose
  └─ Phase ── Milestone as a working system unit
       └─ Goal ── Core feature group needed to achieve a Phase
            └─ Task ── Minimum implementation unit for developer agents
```

### Autonomy gradient

| Level | Autonomy | Process |
|-------|----------|---------|
| **Project** | Human-driven | Listen to user's description, AI organizes and writes |
| **Phase** | AI-proposes | Listen to user's purpose, AI proposes, user approves/corrects |
| **Goal** | AI-driven | AI writes based on Phase, notifies user |
| **Task** | AI-autonomous | AI creates freely based on Goals |

---

## ADV Documents

Three foundation documents that must exist before Goal/Task creation.
Stored in `.mpm/docs/`.

| Document | Purpose | Creation process |
|----------|---------|------------------|
| **ARCHITECTURE.md** | Engineering consistency — tech stack, patterns, conventions | AI scans codebase, proposes architecture, user approves |
| **DESIGN.md** | UI/UX consistency — design concept, tokens, component patterns | AI asks user for design concept, organizes into rulebook |
| **VERIFICATION.md** | Self-verification methods — how to check work without asking user | AI inspects available tools (curl, pytest, chrome, etc.), asks user for additional methods |

**Layer order (never skip):**
```
Layer 1: Project + Phase       (PPGT)
Layer 2: Architecture + Design + Verification  (ADV)
Layer 3: Goal                  (PPGT)
Layer 4: Task                  (PPGT)
```

If a project has no UI, DESIGN.md can be skipped (Planner judges, user confirms).

---

## Task System

Tasks are tracked via files in `.mpm/data/`.

### File Structure

```
.mpm/data/
├── future.json             # Queued tasks (front = highest priority)
├── current/                # Active tasks (one per session)
│   └── {session_id}.json
└── past/
    └── YYMMDD.json         # Completed/postponed/discarded tasks
```

### Task Schema

All locations use the same schema. Fields are filled progressively:

```json
{
  "id": "unique_id",
  "title": "One-line summary",
  "prompt": "Detailed task instruction",
  "goal": "Verifiable acceptance criteria — WHAT must be true (fill on current entry)",
  "approach": "How to accomplish (fill on current entry)",
  "verification": "HOW will you check the goal is met (fill on current entry)",
  "result": "Actual outcome (fill on completion)",
  "memo": "Notes (fill on completion)",
  "status": "queued | active | success | postpone | modified | discard",
  "created": "YYMMDDHHmm",
  "session_id": "Claude Code session ID (fill on current entry)",
  "parent_id": "Original task ID (when re-created from postpone/modified)"
}
```

### Session ID

Get the current session ID from the hook log:
```bash
grep "session=" /tmp/mpm-hook.log | tail -1 | sed 's/.*session=//'
```

### Workflow

#### 1. Start a task

**From queue:** Pop from the front (index 0) of `future.json` and save to `current/{session_id}.json`.

**From conversation:** If there is no current task and the user requests work that involves code changes, immediately create a current task. Do this BEFORE starting the actual work.

```bash
# Get session ID, then create
SID=$(grep "session=" /tmp/mpm-hook.log | tail -1 | sed 's/.*session=//')
python3 .mpm/scripts/task.py create "$SID" "title" "prompt"
python3 .mpm/scripts/task.py update "$SID" goal "..."
python3 .mpm/scripts/task.py update "$SID" approach "..."
python3 .mpm/scripts/task.py update "$SID" verification "..."
```

**How to judge "work that involves code changes":**
- YES → create task: "Change the border color", "Add this feature", "Fix this bug"
- YES → create task: User starts with a question but then says "OK do it" — create task before first edit
- NO → no task: "How does this work?", "What's the next task?", "Why is this error happening?"

Fill `goal`, `approach`, `verification`, set `status` to `active`, set `session_id`.

**goal = WHAT** must be true (verifiable acceptance criteria, as a checklist).
**verification = HOW** you will check each goal item.

#### 2. Do the work

Work normally. No need to update the task file mid-work.

#### 3. Complete the work

When done, fill the `result` field with the actual outcome including verification results.

Also fill `memo` with a brief summary of ALL work done during the session — the task may have started as "Fix border color" but the conversation may have led to additional changes. The memo captures what actually happened, not just the original goal.

The Stop hook will then ask the user for confirmation.

#### 4. User confirmation

Map the user's natural-language response to a status:
- Agreement / "next" → `success` → move to `past/YYMMDD.json`
- Requests more changes → keep in `current`, continue working
- "Later" / defer → `postpone` → move to past + create new card in future
- "Cancel" / "drop" → `discard` → move to past

#### 5. Postpone/modified: create a new card

The original card goes to past as-is (preserving the record). Create a new card:
- Set `parent_id` to the original task's ID
- Write a `prompt` that includes context from the previous attempt (goal, approach, reason for deferral)

## Rules

- **All task JSON operations must go through `task.py`** — never read/write `.mpm/data/` JSON files directly. Available commands: `pop`, `create`, `complete`, `add`, `update`, `status`.
- Always pop from the **front** (index 0) of future.json.
- Append new tasks to the **back** of future.json.
- Move to past **immediately** when a result is confirmed — not on a date boundary.
- Only one task per session in current.
- Always respond to the user in their language.
