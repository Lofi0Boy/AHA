#!/bin/bash
# SessionStart hook: check if AHA is initialized in this project.
# If PROJECT.md doesn't exist, prompt the user to run /aha-init.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd' 2>/dev/null)

# Check if .aha directory exists but PROJECT.md is missing
if [ -d "$CWD/.aha" ] && [ ! -f "$CWD/.aha/docs/PROJECT.md" ]; then
  cat <<'INITEOF'
[AHA] This project hasn't been initialized yet.
Send to @aha-planner via SendMessage to run /aha-init and set up your project.
INITEOF
  exit 0
fi

# PROJECT.md exists — normal session
exit 0
