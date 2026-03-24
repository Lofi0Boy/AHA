#!/bin/bash
# SessionStart hook: inject project docs + browse tool path into context.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd' 2>/dev/null)
DOCS="$CWD/.mpm/docs"

# --- 1. Project documents ---
if [ -d "$DOCS" ]; then
  output=""
  for filepath in "$DOCS"/*.md; do
    [ -f "$filepath" ] || continue
    filename=$(basename "$filepath")
    content=$(cat "$filepath")
    output+="
--- $filename ---
$content
"
  done

  if [ -n "$output" ]; then
    echo "[MPM Project Context]"
    echo "$output"
  fi
fi