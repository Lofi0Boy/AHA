#!/bin/bash
# Usage: echo '<hook_stdin_json>' | hook-notify.sh <status>
# Reads hook stdin JSON, extracts project and session_id, sends to dashboard.
# Logs to /tmp/aha-hook.log for debugging.

STATUS="${1:-unknown}"
INPUT=$(cat)

echo "$(date) | status=$STATUS | input=$INPUT" >> /tmp/aha-hook.log

PROJECT=$(echo "$INPUT" | jq -r '.cwd | split("/") | last' 2>>/tmp/aha-hook.log)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id' 2>>/tmp/aha-hook.log)

echo "$(date) | project=$PROJECT session=$SESSION_ID" >> /tmp/aha-hook.log

# Dashboard port: AHA_PORT env var, or default 5100
PORT="${AHA_PORT:-5100}"

curl -s -X POST "http://localhost:${PORT}/api/hook/agent-status" \
  -H 'Content-Type: application/json' \
  -d "{\"project\": \"$PROJECT\", \"session_id\": \"$SESSION_ID\", \"status\": \"$STATUS\"}" \
  2>>/tmp/aha-hook.log || true

echo "$(date) | done" >> /tmp/aha-hook.log
