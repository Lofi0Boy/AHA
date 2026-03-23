#!/bin/bash
# SessionStart hook: inject all .mpm/docs/ documents into context.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd' 2>/dev/null)
DOCS="$CWD/.mpm/docs"

[ ! -d "$DOCS" ] && exit 0

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
