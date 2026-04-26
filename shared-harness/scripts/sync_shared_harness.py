#!/usr/bin/env python3
"""Mirror the canonical Codex shared-harness skill into Claude Code."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


HOME = Path.home()
CODEX_SKILL = HOME / ".codex" / "skills" / "shared-harness"
CLAUDE_SKILL = HOME / ".claude" / "skills" / "shared-harness"
CLAUDE_COMMAND = HOME / ".claude" / "commands" / "shared-harness.md"
WRAPPER = HOME / ".local" / "bin" / "shared-harness"
MANIFEST_NAME = ".shared-harness-manifest.json"


IGNORED_NAMES = {MANIFEST_NAME, "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def should_copy(path: Path) -> bool:
    return not any(part in IGNORED_NAMES for part in path.parts) and path.suffix not in IGNORED_SUFFIXES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_skill() -> list[dict[str, str]]:
    if not CODEX_SKILL.exists():
        raise FileNotFoundError(f"canonical skill missing: {CODEX_SKILL}")
    copied: list[dict[str, str]] = []
    for source in sorted(CODEX_SKILL.rglob("*")):
        if not source.is_file() or not should_copy(source.relative_to(CODEX_SKILL)):
            continue
        rel = source.relative_to(CODEX_SKILL)
        target = CLAUDE_SKILL / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(rel), "sha256": sha256(source)})
    return copied


def write_claude_command() -> None:
    CLAUDE_COMMAND.parent.mkdir(parents=True, exist_ok=True)
    CLAUDE_COMMAND.write_text(
        """# shared-harness

Use the mirrored `shared-harness` skill to inspect or refresh Claude Code / Codex interoperability posture.

Default audit:

```bash
shared-harness
```

Useful commands:

```bash
shared-harness --json
python3 ~/.codex/skills/shared-harness/scripts/sync_shared_harness.py
python3 ~/.codex/skills/shared-harness/scripts/validate_shared_harness.py
```

Rules:

- Do not start MCP servers, plugins, browsers, or agent sessions for a status audit.
- Treat `~/.codex/skills/shared-harness` as canonical.
- Keep PM task state in the active `_pm/` files and write handoffs for lane results.
- Do not edit MCP configs or settings from this command.
""",
        encoding="utf-8",
    )


def write_wrapper() -> None:
    WRAPPER.parent.mkdir(parents=True, exist_ok=True)
    WRAPPER.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
exec python3 "$HOME/.codex/skills/shared-harness/scripts/harness_status.py" "$@"
""",
        encoding="utf-8",
    )
    WRAPPER.chmod(0o755)


def write_manifest(files: list[dict[str, str]]) -> dict[str, object]:
    manifest = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_skill": str(CODEX_SKILL),
        "claude_skill": str(CLAUDE_SKILL),
        "claude_command": str(CLAUDE_COMMAND),
        "wrapper": str(WRAPPER),
        "managed_by": "shared-harness",
        "mcp_configs_mutated": False,
        "settings_mutated": False,
        "files": files,
    }
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (CODEX_SKILL / MANIFEST_NAME).write_text(text, encoding="utf-8")
    (CLAUDE_SKILL / MANIFEST_NAME).write_text(text, encoding="utf-8")
    return manifest


def sync() -> dict[str, object]:
    files = copy_skill()
    write_claude_command()
    write_wrapper()
    manifest = write_manifest(files)
    return {
        "copied_files": len(files),
        "claude_skill": str(CLAUDE_SKILL),
        "claude_command": str(CLAUDE_COMMAND),
        "wrapper": str(WRAPPER),
        "manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    result = sync()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Shared harness synced")
        print(f"- Copied files: {result['copied_files']}")
        print(f"- Claude skill: {result['claude_skill']}")
        print(f"- Claude command: {result['claude_command']}")
        print(f"- Wrapper: {result['wrapper']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
