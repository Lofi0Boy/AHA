# MPM Task System

This project uses the MPM task system. Tasks are tracked via files in `.mpm/data/`.

---

## File Structure

```
.mpm/data/
├── future.json             # Queued tasks (front = highest priority)
├── current/                # Active tasks (one per session)
│   └── {session_id}.json
└── past/
    └── YYMMDD.json         # Completed/postponed/discarded tasks
```

## Task Schema

All locations use the same schema. Fields are filled progressively:

```json
{
  "id": "unique_id",
  "title": "One-line summary",
  "prompt": "Detailed task instruction",
  "goal": "Refined goal (fill on current entry)",
  "approach": "How to accomplish (fill on current entry)",
  "verification": "Concrete steps to verify success — HOW will you check? (fill on current entry)",
  "result": "Actual outcome (fill on completion)",
  "memo": "Notes (fill on completion)",
  "status": "queued | active | success | postpone | modified | discard",
  "created": "YYMMDDHHmm",
  "session_id": "Claude Code session ID (fill on current entry)",
  "parent_id": "Original task ID (when re-created from postpone/modified)"
}
```

## Workflow

### 1. Start a task

Pop from the front (index 0) of `future.json` and save to `current/{session_id}.json`.
Fill `goal`, `approach`, `verification`, set `status` to `active`, set `session_id`.

**verification must describe HOW you will verify**, not just WHAT should be true.
- Bad: "Tests pass"
- Good: "Run `pytest tests/` and confirm all tests pass. Take a headless Chrome screenshot of the dashboard and visually confirm the card renders correctly."

### 2. Do the work

Work normally. No need to update the task file mid-work.

### 3. Complete the work

When done, fill the `result` field with the outcome including verification results.
The Stop hook will then ask the user for confirmation.

### 4. User confirmation

Map the user's natural-language response to a status:
- Agreement / "next" → `success` → move to `past/YYMMDD.json`
- Requests more changes → keep in `current`, continue working
- "Later" / defer → `postpone` → move to past + create new card in future
- "Cancel" / "drop" → `discard` → move to past

### 5. Postpone/modified: create a new card

The original card goes to past as-is (preserving the record). Create a new card:
- Set `parent_id` to the original task's ID
- Write a `prompt` that includes context from the previous attempt (goal, approach, reason for deferral)

## Rules

- Always pop from the **front** (index 0) of future.json.
- Append new tasks to the **back** of future.json.
- Move to past **immediately** when a result is confirmed — not on a date boundary.
- Only one task per session in current.
- Always respond to the user in their language.
