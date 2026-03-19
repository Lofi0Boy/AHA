#!/bin/bash
# MPM Auto-Next Stop Hook
# When autonext is active, blocks session exit and feeds next task prompt.
# Uses a queue of task IDs — only processes tasks in the queue.

set -euo pipefail

HOOK_INPUT=$(cat)
STATE_FILE=".mpm/data/autonext-state.json"

# No active autonext → allow exit
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Session isolation
STATE_SESSION=$(jq -r '.session_id // ""' "$STATE_FILE")
HOOK_SESSION=$(echo "$HOOK_INPUT" | jq -r '.session_id // ""')
if [[ -n "$STATE_SESSION" ]] && [[ "$STATE_SESSION" != "$HOOK_SESSION" ]]; then
  exit 0
fi

MAX_ITER=$(jq -r '.max_iterations // 3' "$STATE_FILE")
TASK_ITER=$(jq -r '.task_iteration // 0' "$STATE_FILE")
TASKS_DONE=$(jq -r '.tasks_completed // 0' "$STATE_FILE")
QUEUE_LEN=$(jq '.queue | length' "$STATE_FILE")

SID="$HOOK_SESSION"
CURRENT_FILE=".mpm/data/current/${SID}.json"
HAS_CURRENT="false"
CURRENT_RESULT=""
if [[ -f "$CURRENT_FILE" ]]; then
  HAS_CURRENT="true"
  CURRENT_RESULT=$(jq -r '.result // ""' "$CURRENT_FILE")
fi

# --- Current task still in progress (no result yet) ---
if [[ "$HAS_CURRENT" == "true" ]] && [[ -z "$CURRENT_RESULT" ]]; then
  NEW_TASK_ITER=$((TASK_ITER + 1))

  if [[ $NEW_TASK_ITER -ge $MAX_ITER ]]; then
    # Max iterations — force fail
    python3 .mpm/scripts/task.py update "$SID" result "(auto-failed: max iterations reached)" 2>/dev/null || true
    python3 .mpm/scripts/task.py update "$SID" memo "Max $MAX_ITER iterations reached without completing verification." 2>/dev/null || true
    python3 .mpm/scripts/task.py complete "$SID" fail 2>/dev/null || true
    TASKS_DONE=$((TASKS_DONE + 1))

    # Remove completed task from queue
    COMPLETED_ID=$(jq -r '.id // ""' "$CURRENT_FILE" 2>/dev/null || echo "")
    TMPF="${STATE_FILE}.tmp.$$"
    jq --argjson ti 0 --argjson td "$TASKS_DONE" --arg cid "$COMPLETED_ID" \
      '.task_iteration = $ti | .tasks_completed = $td | .queue = [.queue[] | select(. != $cid)]' "$STATE_FILE" > "$TMPF"
    mv "$TMPF" "$STATE_FILE"
    QUEUE_LEN=$(jq '.queue | length' "$STATE_FILE")

    if [[ "$QUEUE_LEN" -eq 0 ]]; then
      echo "✅ MPM Auto-Next complete ($TASKS_DONE tasks processed). Queue empty."
      rm "$STATE_FILE"
      exit 0
    fi

    PROMPT="Previous task failed after $MAX_ITER iterations. Moving on.
Pop the next task: python3 .mpm/scripts/task.py pop $SID
Then fill goal/approach/verification, do the work, self-verify, and fill result+memo.
Use available verification methods (headless Chrome, curl, tests, file inspection).
If verification passes, complete with success. If not, retry up to $MAX_ITER times."

    jq -n --arg p "$PROMPT" --argjson td "$TASKS_DONE" --argjson ql "$QUEUE_LEN" \
      '{decision:"block", reason:$p, systemMessage:("🔄 Auto-Next | Done: " + ($td|tostring) + " | Queue: " + ($ql|tostring) + " | Task failed → next")}'
    exit 0
  fi

  # Not at max — continue working
  TMPF="${STATE_FILE}.tmp.$$"
  jq --argjson ti "$NEW_TASK_ITER" '.task_iteration = $ti' "$STATE_FILE" > "$TMPF"
  mv "$TMPF" "$STATE_FILE"

  PROMPT="Continue working on the current task. Iteration $NEW_TASK_ITER/$MAX_ITER.
Self-verify your work using the verification method specified in the task.
If verification passes: fill result and memo, then run: python3 .mpm/scripts/task.py complete $SID success
If verification fails: fix the issues and try again."

  jq -n --arg p "$PROMPT" --argjson ti "$NEW_TASK_ITER" --argjson mi "$MAX_ITER" \
    '{decision:"block", reason:$p, systemMessage:("🔄 Auto-Next | Task iteration " + ($ti|tostring) + "/" + ($mi|tostring))}'
  exit 0
fi

# --- Current task completed (has result) or no current task ---
if [[ "$HAS_CURRENT" == "true" ]] && [[ -n "$CURRENT_RESULT" ]]; then
  STATUS=$(jq -r '.status // ""' "$CURRENT_FILE")
  if [[ "$STATUS" == "active" ]]; then
    python3 .mpm/scripts/task.py complete "$SID" success 2>/dev/null || true
  fi
  TASKS_DONE=$((TASKS_DONE + 1))

  # Remove completed task from queue
  COMPLETED_ID=$(jq -r '.id // ""' "$CURRENT_FILE" 2>/dev/null || echo "")
  TMPF="${STATE_FILE}.tmp.$$"
  jq --argjson ti 0 --argjson td "$TASKS_DONE" --arg cid "$COMPLETED_ID" \
    '.task_iteration = $ti | .tasks_completed = $td | .queue = [.queue[] | select(. != $cid)]' "$STATE_FILE" > "$TMPF"
  mv "$TMPF" "$STATE_FILE"
  QUEUE_LEN=$(jq '.queue | length' "$STATE_FILE")
fi

# Check queue — if empty, re-check future for new tasks (default mode only)
if [[ "$QUEUE_LEN" -eq 0 ]]; then
  MODE=$(jq -r '.mode // "--all"' "$STATE_FILE")
  if [[ "$MODE" == "--all" ]] || [[ "$MODE" == "" ]]; then
    # Re-check future.json for newly added tasks
    NEW_QUEUE=$(python3 -c "
import json
tasks = json.load(open('.mpm/data/future.json'))
ids = [t['id'] for t in tasks]
print(json.dumps(ids))
" 2>/dev/null || echo "[]")
    NEW_LEN=$(echo "$NEW_QUEUE" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
    if [[ "$NEW_LEN" -gt 0 ]]; then
      TMPF="${STATE_FILE}.tmp.$$"
      jq --argjson q "$NEW_QUEUE" '.queue = $q' "$STATE_FILE" > "$TMPF"
      mv "$TMPF" "$STATE_FILE"
      QUEUE_LEN="$NEW_LEN"
    else
      # Future is empty — done
      echo "✅ MPM Auto-Next complete ($TASKS_DONE tasks processed). No more tasks."
      rm "$STATE_FILE"
      exit 0
    fi
  else
    # Non-default mode — queue exhausted, done
    echo "✅ MPM Auto-Next complete ($TASKS_DONE tasks processed). Queue empty."
    rm "$STATE_FILE"
    exit 0
  fi
fi

if [[ "$QUEUE_LEN" -eq 0 ]]; then
  echo "✅ MPM Auto-Next complete ($TASKS_DONE tasks processed). No more tasks."
  rm "$STATE_FILE"
  exit 0
fi

# Feed next task
PROMPT="Pop the next task: python3 .mpm/scripts/task.py pop $SID
Then fill goal/approach/verification, do the work, self-verify, and fill result+memo.
Use available verification methods (headless Chrome screenshots, curl, tests, file inspection).
Only ask the user when self-verification is genuinely impossible.
If verification passes: complete with success.
Max $MAX_ITER iterations per task."

jq -n --arg p "$PROMPT" --argjson td "$TASKS_DONE" --argjson ql "$QUEUE_LEN" \
  '{decision:"block", reason:$p, systemMessage:("🔄 Auto-Next | Done: " + ($td|tostring) + " | Queue: " + ($ql|tostring))}'
exit 0
