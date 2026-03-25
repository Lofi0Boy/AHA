---
name: aha-human-review
description: Process the human review queue — show tasks one by one, discuss with user, approve/reject/discard.
---

# Human Review

Process tasks in the review queue one at a time. You drive the flow — the user only confirms.

## Step 1: Show queue

```bash
python3 .aha/scripts/human-review.py
```

If queue is empty, inform the user and stop. If there are rejected tasks in past, suggest running `/aha-recycle` in a planner session.

## Step 2: Show first task

```bash
python3 .aha/scripts/human-review.py 1
```

The script outputs a structured card and the `task_id`. After showing the card:

- **If `[UI]` task**: provide the app URL from the injected VERIFICATION.md and list the screenshot paths so the user can open them.
- **If `needs-input`**: explain what the agent couldn't verify and ask the user how to proceed.
- Otherwise, briefly summarize and ask for the user's take.

Do NOT attempt to open or interpret screenshots. Just provide paths.

## Step 3: Discuss with user

Multi-turn conversation. Let the user ask questions, raise concerns, or confirm. Read source files if the user asks about implementation details.

## Step 4: Conclude

When the conversation reaches a conclusion, draft the verdict yourself:

- **approve** → `python3 .aha/scripts/task.py complete <task_id> success`
- **reject** → `python3 .aha/scripts/task.py complete <task_id> rejected --comment "..."` (you write the comment)
- **discard** → `python3 .aha/scripts/task.py complete <task_id> discard`

Present your draft to the user naturally. Example:
> "Looks good — I'll approve. OK?"
> "The empty state is missing — I'll reject: 'Empty state not implemented, blank screen on zero data.' OK?"

After user confirms, execute the command.

### On reject: recycle immediately

When a task is rejected, rewrite and re-queue it right away — don't wait for a separate `/aha-recycle` step. The discussion already established what went wrong.

1. Read `.claude/skills/aha-task-write/SKILL.md` for the task prompt format
2. Rewrite the prompt (and goal/verification if needed) based on the rejection discussion
3. Recycle:
   ```bash
   python3 .aha/scripts/task.py recycle <task_id> "<new_prompt>" [--goal "<new_goal>"] [--verification "<new_verification>"]
   ```
   This removes the rejected task from past, injects previous attempt context into the new prompt, and adds it to future. Goal/verification are preserved from the original unless overridden with `--goal`/`--verification`.
4. Brief one-line confirmation (e.g., "Recycled → new task added to queue"), then move on

Do NOT show the full rewritten prompt to the user for approval — the rejection discussion already covered what needs to change.

## Step 5: Next

Move to the next task — run `python3 .aha/scripts/human-review.py 1` again (always index 1, since the previous task was removed from the queue). Keep going until the queue is empty.

Always respond in the user's language.
