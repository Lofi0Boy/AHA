---
name: aha-recycle
description: Scan past for rejected tasks, collect rejection context, and invoke /aha-task-write to create improved replacement tasks.
---

# Recycle Rejected Tasks

Scan past for tasks rejected by human review, collect rejection context, then delegate to `/aha-task-write` for proper task creation.

## Step 1: Find rejected tasks

```bash
python3 .aha/scripts/task.py rejected
```

If none found, inform the user and stop.

## Step 2: For each rejected task, collect context

1. Read the full task details from past:
   - `prompt` (original instruction)
   - `result` (what was actually done)
   - `agent_reviews` (what reviewer found)
   - `human_review.comment` (why human rejected)
   - `parent_goal` (which goal this serves)

2. Summarize the rejection context:
   ```
   Previous attempt: [what was done]
   Rejection reason: [human's comment]
   Reviewer findings: [relevant agent review notes]
   What went wrong: [your analysis]
   ```

## Step 3: Rewrite and recycle

Read `.claude/skills/aha-task-write/SKILL.md` for the task prompt format. Using the rejection context from Step 2, rewrite the prompt (and goal/verification if needed).

```bash
python3 .aha/scripts/task.py recycle <task_id> "<new_prompt>" [--goal "<new_goal>"] [--verification "<new_verification>"]
```

This removes the rejected task from past, injects previous attempt context into the new prompt, and adds it to future. Goal/verification are preserved from the original unless overridden.

## Step 4: Confirm

Show the user what was recycled and the new task summary.

---

Always respond in the user's language.
