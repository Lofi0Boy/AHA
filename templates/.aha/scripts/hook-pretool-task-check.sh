#!/bin/bash
# PreToolUse hook (matcher: Edit|Write): BLOCK if no current task exists for this session.
# Exception: .aha/ and .claude/ paths are always allowed (system files).

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id' 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // ""' 2>/dev/null)

# No .aha directory — not an AHA project, skip
[ ! -d "$CWD/.aha" ] && exit 0

# Allow .aha/ and .claude/ paths — system files, not project code
case "$FILE_PATH" in
  */.aha/*|*/.claude/*) exit 0 ;;
esac

# Check if THIS session has a current task
TASK_FILE="$CWD/.aha/data/current/${SESSION_ID}.json"

if [ ! -f "$TASK_FILE" ]; then
  jq -n '{
    decision: "block",
    reason: "[AHA] No current task. Send to @aha-planner via SendMessage to create properly scoped tasks first, then pop one to start working. Do NOT create tasks directly — always go through @aha-planner."
  }'
  exit 0
fi

exit 0
