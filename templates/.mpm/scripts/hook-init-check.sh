#!/bin/bash
# SessionStart hook: check if MPM is initialized in this project.
# If PROJECT.md doesn't exist, prompt to spawn the planner agent.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd' 2>/dev/null)

# Check if .mpm directory exists but PROJECT.md is missing
if [ -d "$CWD/.mpm" ] && [ ! -f "$CWD/.mpm/docs/PROJECT.md" ]; then
  cat <<'EOF'
[MPM] This project hasn't been initialized yet.
Spawn the planner agent to initialize: use Agent tool with subagent_type "planner", or suggest the user run `claude --agent planner`.
EOF
  exit 0
fi

# PROJECT.md exists — normal session
exit 0
