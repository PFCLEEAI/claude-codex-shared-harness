#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/shared-harness"
TARGET="$HOME/.codex/skills/shared-harness"
FORCE=false

if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

if [[ ! -d "$SOURCE" ]]; then
  echo "Missing source skill: $SOURCE" >&2
  exit 1
fi

mkdir -p "$HOME/.codex/skills"
if [[ -e "$TARGET" && "$FORCE" != "true" ]]; then
  echo "Target already exists: $TARGET" >&2
  echo "Re-run with --force to replace it." >&2
  exit 2
fi

rm -rf "$TARGET"
cp -R "$SOURCE" "$TARGET"

python3 "$TARGET/scripts/sync_shared_harness.py"
python3 "$TARGET/scripts/validate_shared_harness.py"

echo "Installed shared-harness"
echo "- Canonical Codex skill: $TARGET"
echo "- Claude mirror: $HOME/.claude/skills/shared-harness"
echo "- Wrapper: $HOME/.local/bin/shared-harness"
