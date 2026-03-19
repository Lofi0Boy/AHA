---
name: mpm-autonext
description: Automatically work through selected future tasks — work, self-verify, complete, and move to next.
disable-model-invocation: true
allowed-tools: Bash(python3 *), Bash(google-chrome *), Bash(curl *)
---

# MPM Auto-Next

Automatically process tasks from the future queue. Each task: pop → work → self-verify → complete → next.

## Arguments

- **(no args)**: Queue ALL current future tasks. After exhausting the queue, re-check future for newly added tasks and continue.
- `--top N`: Queue only the top N tasks (highest priority = front of queue).
- `0,2,4` or `1,3,5`: Queue only tasks at these indices (0-based).

## Setup

```bash
SID=$(grep "session=" /tmp/mpm-hook.log | tail -1 | sed 's/.*session=//')

# Parse arguments and build initial queue
QUEUE=$(python3 -c "
import json, sys
tasks = json.load(open('.mpm/data/future.json'))
args = sys.argv[1:]

if not args:
    # Default: all tasks
    ids = [t['id'] for t in tasks]
elif args[0] == '--top' and len(args) > 1:
    n = int(args[1])
    ids = [t['id'] for t in tasks[:n]]
elif ',' in args[0] or args[0].isdigit():
    indices = [int(i) for i in args[0].split(',')]
    ids = [tasks[i]['id'] for i in indices if i < len(tasks)]
else:
    ids = [t['id'] for t in tasks]

print(json.dumps(ids))
" -- ${ARGS:-})

MODE=${1:---all}

cat > .mpm/data/autonext-state.json << EOF
{
  "session_id": "$SID",
  "max_iterations": 3,
  "task_iteration": 0,
  "tasks_completed": 0,
  "queue": $QUEUE,
  "mode": "$MODE",
  "started_at": "$(date -Iseconds)"
}
EOF
echo "🚀 MPM Auto-Next activated ($(echo $QUEUE | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))') tasks)"
```

## Workflow

1. Pop the next task:
   ```bash
   python3 .mpm/scripts/task.py pop ${CLAUDE_SESSION_ID}
   ```

2. Read the task and fill `goal`, `approach`, `verification`.
   - **goal**: verifiable acceptance criteria (checklist)
   - **verification**: HOW to check — prefer self-verification:
     - `/chrome` — interact with live pages (click, type, scroll, read console). Best for UI verification
     - `google-chrome --headless --screenshot=...` — quick static visual checks
     - `curl -s URL | grep/jq ...` — API responses, HTML content
     - Run tests, check files, execute scripts
     - Ask user ONLY when genuinely impossible

3. Do the work.

4. Self-verify using the method you specified.
   - If verification **passes**: fill `result` and `memo`, then complete with `success`.
   - If verification **fails**: fix and retry. The Stop hook will track iterations.

5. After completing a task, the Stop hook will pop the next task from the queue.

6. **When the queue is exhausted** (default mode only): re-check `future.json` for newly added tasks. If new tasks exist, add them to the queue and continue. If no new tasks, the loop ends.

## Rules

- **NEVER manually delete `autonext-state.json`** — the Stop hook manages the lifecycle. Manual deletion breaks the queue re-check loop.
- After completing a task, just end your response normally. The Stop hook will handle queue progression and future re-check.
- Only the user should cancel autonext (by deleting the state file or saying "stop").

## Cancellation

The **user** can stop the auto-next loop at any time by deleting the state file:
```bash
rm .mpm/data/autonext-state.json
```

Always respond in the user's language.
