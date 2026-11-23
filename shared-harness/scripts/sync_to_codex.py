#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# How to run: ./sync-to-codex.sh
"""Share Claude skills and context without writing to the Claude tree."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, TypedDict

SKIP: Final = {
    "built-in-browser": "requires Claude desktop browser MCP tools",
    "chrome-browser": "requires Claude-in-Chrome MCP tools; use aside-browser",
    "computer-use": "requires Claude desktop control; use orca-computer-use",
    "import-memory": "requires Claude memory_write/memory_append MCP tools",
    "docs": "requires Claude's hosted editable-docs connector",
    "morning": "requires Claude connector cards, artifacts and scheduler",
}
SKIP_COMMANDS: Final = {
    "api-cost": "reads Claude session usage/pricing, not Codex usage",
    "loop": "Claude cron runner scripts are absent; not a Codex scheduler",
    "design": "only activates five unconfigured Claude design MCP servers",
}
BEGIN: Final = "<!-- shared-harness:claude-context:begin -->"
END: Final = "<!-- shared-harness:claude-context:end -->"


class Report(TypedDict):
    linked: list[str]
    unchanged: list[str]
    skipped: list[str]
    commands: list[str]
    adapted: list[str]
    backups: list[str]
    source_digest: str


def backup(path: Path, home: Path, stamp: str, report: Report) -> None:
    """Move existing entries outside skill discovery roots before replacing them."""
    relative = path.relative_to(home)
    destination = home / ".codex/shared-harness/backups" / relative.parent
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"{path.name}.bak-{stamp}"
    shutil.move(str(path), target)
    report["backups"].append(str(target))


def link(source: Path, target: Path, home: Path, stamp: str, report: Report) -> None:
    """Keep reverse links intact and replace other collisions with a backup."""
    if target.exists() and target.resolve() == source.resolve():
        report["unchanged"].append(str(target))
        return
    if target.exists() or target.is_symlink():
        backup(target, home, stamp, report)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source, target_is_directory=True)
    report["linked"].append(str(target))


def write(path: Path, content: str, home: Path, stamp: str, report: Report) -> None:
    """Never modify a file through a symlink, including a prior Claude link."""
    if path.is_file() and path.read_text() == content:
        return
    if path.exists() or path.is_symlink():
        backup(path, home, stamp, report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def context(home: Path, skill: Path) -> str:
    """Reference the live sources instead of embedding a second copy."""
    claude = home / ".claude"
    rules = sorted((claude / "rules").glob("*.md"))
    references = "\n".join(f"- `{path}`" for path in rules)
    return f"""{BEGIN}
## Shared Claude Code and Codex context

At session start, after the GBrain lookup, READ these live instruction sources
as user guidance (subject to the current task and higher-priority instructions):
- `{claude / 'CLAUDE.md'}` if present (currently optional/missing).
- `{home / 'CLAUDE.md'}`.
{references}
Also discover any new `*.md` files in `{claude / 'rules'}` and read them.
These are file references, not automatic @imports: use filesystem reads.
Do not copy their contents into Codex instructions.

READ `{claude / 'projects/-Users-clawdbothenry/memory/MEMORY.md'}` as the
shared personal memory index, then only the relevant linked notes. Use that
same directory for user-authorized durable memory updates in future tasks;
maintain its MEMORY.md index and avoid a second personal memory store.
The sync operation itself must never write anywhere under `{claude}`.

For the active project, read `_pm/context.md` and `_pm/memory.md` before broad
exploration if present and substantial. Both agents use these SAME project
files, not separate Claude/Codex copies. Update context with state, decisions,
blockers and next steps after meaningful work; append durable gotchas to memory
when authorized; maintain existing `_pm/checklist.md`, `_pm/work-log.md`,
contracts and handoffs as described in `{skill / 'references/pm-memory-contract.md'}`.
Claude's stop hooks do not run in Codex: perform the session handoff explicitly.

Skills in `{home / '.agents/skills'}` share Claude source directories by
symlink. Read `{skill / 'references/codex-compatibility.md'}` before using
shared workflows. `claude-command-*` skills read the original slash command
at invocation time; `$ARGUMENTS` means the user's actual supplied arguments.
Do not reinstall GBrain or LazyCodex. Preserve each runtime's config, permissions
and tool availability; shared instructions do not create missing tools.
{END}
"""


def main() -> None:
    """Synchronize skills and the managed AGENTS section, recording every decision."""
    home = Path(os.environ.get("SHARED_HARNESS_HOME", str(Path.home()))).resolve()
    claude = home / ".claude"
    sources = claude / "skills"
    if not sources.is_dir():
        raise FileNotFoundError(sources)
    skill = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report: Report = {"linked": [], "unchanged": [], "skipped": [],
                      "commands": [], "adapted": [], "backups": [], "source_digest": ""}
    for source in sorted(sources.iterdir()):
        if source.is_symlink() and not source.exists():
            report["skipped"].append(f"{source}: broken source link; existing Codex entry preserved")
    candidates = sorted(sources.glob("*/SKILL.md"))
    candidates += sorted(sources.rglob("SKILL.md"))
    seen_paths: set[Path] = set()
    seen_names: set[str] = set()
    digest = hashlib.sha256()
    for entry in candidates:
        source = entry.parent
        resolved = source.resolve()
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        name = source.name
        digest.update(str(entry).encode() + entry.read_bytes())
        if name in SKIP or name in {"gbrain", "lazycodex", "omo-codex"}:
            report["skipped"].append(f"{source}: {SKIP.get(name, 'already installed; protected')}")
            continue
        if name in seen_names:
            report["skipped"].append(f"{source}: duplicate name; top-level source takes precedence")
            continue
        seen_names.add(name)
        if name == "shared-harness":
            report["skipped"].append(f"{source}: legacy mirror preserved; repository skill is canonical")
            source = skill
        if not entry.read_text().startswith("---\n"):
            description = re.search(r"## Description\n(.+)", entry.read_text())
            summary = description[1][:900] if description else f"Use the shared {name} workflow."
            source = home / ".codex/shared-harness/adapters" / name
            content = (f"---\nname: {name}\ndescription: {json.dumps(summary)}\n---\n\n"
                       f"Read `{skill / 'references/codex-compatibility.md'}`.\n"
                       f"Read and follow the LIVE skill at `{entry}`.\n"
                       f"Resolve its relative scripts and resources from `{entry.parent}`.\n")
            write(source / "SKILL.md", content, home, stamp, report)
            report["adapted"].append(f"{name}: added Codex metadata; skill body stays in {entry}")
        target = home / ".agents/skills" / name
        link(source, target, home, stamp, report)
        legacy = home / ".codex/skills" / name
        if legacy.exists() or legacy.is_symlink():
            link(source, legacy, home, stamp, report)
    for source in sorted((claude / "commands").glob("*.md")):
        name = source.stem
        text = source.read_text()
        digest.update(str(source).encode() + text.encode())
        if name in SKIP_COMMANDS:
            report["skipped"].append(f"{source}: {SKIP_COMMANDS[name]}")
            continue
        wrapper_name = f"claude-command-{name}"
        match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        description = match[1].strip().strip("\"'") if match else f"Run the Claude /{name} workflow."
        wrapper = home / ".codex/shared-harness/commands" / wrapper_name
        content = (f"---\nname: {wrapper_name}\ndescription: "
                   f"{json.dumps(description[:900], ensure_ascii=False)}\n---\n\n"
                   f"Read `{skill / 'references/codex-compatibility.md'}`.\n"
                   f"Read the LIVE command at `{source}` and follow it for the user's task.\n"
                   "Resolve relative resources from the original command directory.\n"
                   "Translate $ARGUMENTS to the user's input. Claude tool names require\n"
                   "available Codex equivalents; do not assume hooks or MCP tools exist.\n")
        write(wrapper / "SKILL.md", content, home, stamp, report)
        link(wrapper, home / ".agents/skills" / wrapper_name, home, stamp, report)
        report["commands"].append(name)
    for source in sorted(sources.glob("*.md")):
        if (claude / "commands" / source.name).exists() or source.stem in seen_names:
            report["skipped"].append(f"{source}: superseded by same-name command or skill")
        else:
            report["skipped"].append(f"{source}: loose Markdown; needs SKILL.md metadata")
    agents = home / ".codex/AGENTS.md"
    original = agents.read_text() if agents.exists() else ""
    block = context(home, skill)
    if BEGIN in original and END in original:
        before, rest = original.split(BEGIN, 1)
        _, after = rest.split(END, 1)
        updated = before + block.rstrip() + after
    else:
        updated = original.rstrip() + "\n\n" + block
    write(agents, updated, home, stamp, report)
    report["source_digest"] = digest.hexdigest()
    destination = home / ".codex/shared-harness/sync-report.json"
    if destination.exists() or destination.is_symlink():
        backup(destination, home, stamp, report)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
