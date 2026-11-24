#!/usr/bin/env python3
"""Initialize, resume, and check a shared PM project."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROADMAP = """# Project roadmap

```mermaid
flowchart TB
    M1["M1 Define the first milestone<br/>Pending"]
```

- [M1 Define the first milestone](checklist.md#m1-define-the-first-milestone)
"""

CHECKLIST = """# Project checklist

## M1 Define the first milestone

1. [ ] Record the project goal, scope, and acceptance criteria in `contracts/`.
2. [ ] Record how to run the project and verify a change.
"""


def project_root(location: str | None) -> Path:
    if location is not None:
        root = Path(location).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"Expected a project directory: {root}")
        return root

    current = Path.cwd()
    for candidate in (current, *current.parents):
        if (candidate / "_pm").is_dir() or (candidate / ".git").exists():
            return candidate
    raise ValueError("Run in a project checkout or supply its directory.")


def write_missing(path: Path, content: str) -> None:
    """Publish a complete file without replacing another session's work."""
    if path.exists() or path.is_symlink():
        return
    with tempfile.NamedTemporaryFile(
        dir=path.parent, mode="w", encoding="utf-8", delete=False
    ) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.close()
            os.link(temporary, path)
            print(f"Created {path}")
        except FileExistsError:
            pass
        finally:
            temporary.unlink(missing_ok=True)


def initialize(root: Path) -> None:
    notes = root / "_pm"
    notes.mkdir(exist_ok=True)
    write_missing(
        notes / "context.md",
        "# Project context\n\n"
        "- Goal\n- Current state and branch\n- Blockers\n- Next action\n\n"
        "[Checklist](checklist.md) · [Work log](work-log.md)\n",
    )
    write_missing(notes / "memory.md", "# Project memory\n\nRecord durable decisions and setup details here.\n")
    write_missing(notes / "work-log.md", "# Work log\n\nRecord changes, revisions, and verification evidence here.\n")

    roadmap = notes / "roadmap.md"
    checklist = notes / "checklist.md"
    has_named_roadmap = any(path != roadmap for path in notes.glob("*roadmap*.md"))
    # A starter file from an interrupted initialization can be paired safely.
    existing_plan = [
        (path, starter)
        for path, starter in ((roadmap, ROADMAP), (checklist, CHECKLIST))
        if path.exists()
    ]
    if not has_named_roadmap and all(
        path.is_file() and path.read_text(encoding="utf-8") == starter
        for path, starter in existing_plan
    ):
        write_missing(roadmap, ROADMAP)
        write_missing(checklist, CHECKLIST)
    elif not checklist.is_file() or not (roadmap.is_file() or has_named_roadmap):
        print("Kept the existing plan. Add the missing roadmap or checklist using its milestone IDs.")

    for folder in ("contracts", "handoffs"):
        directory = notes / folder
        directory.mkdir(exist_ok=True)
        if not any(directory.iterdir()):
            write_missing(directory / ".gitkeep", "")
    print(f"PM folder {notes}")


def next_step(checklist: Path) -> str:
    milestone = ""
    for line in checklist.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{1,6}\s+(.+)", line)
        if heading:
            milestone = heading[1]
        step = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\[ \]\s+(.+)", line)
        if step:
            return f"{milestone} — {step[1]}" if milestone else step[1]
    return "All recorded steps are checked."


def resume(root: Path) -> None:
    notes = root / "_pm"
    context = notes / "context.md"
    if not context.is_file():
        raise ValueError(f"Missing {context}. Run pm-project init from the project directory.")
    print(f"Project {root}")
    print(context.read_text(encoding="utf-8").rstrip())
    checklist = notes / "checklist.md"
    if checklist.is_file():
        print(f"\nFirst unchecked step\n{next_step(checklist)}")
    else:
        print(f"\nChecklist missing at {checklist}.")
    print(f"\nPlanning files and worker handoffs: {notes}")


def pull_request(root: Path, selector: str | None) -> dict[str, str]:
    command = ["gh", "pr", "view"]
    if selector:
        command.append(selector)
    command.extend(["--json", "url,headRefOid"])
    output = subprocess.check_output(command, cwd=root, text=True)
    return json.loads(output)


def check_pull_request(root: Path, selector: str | None, watch: bool, required: bool) -> int:
    original = pull_request(root, selector)
    url = original["url"]
    revision = original["headRefOid"]
    print(f"Checking {url} at {revision}", flush=True)
    command = ["gh", "pr", "checks", url]
    if watch:
        command.extend(["--watch", "--fail-fast"])
    if required:
        command.append("--required")
    result = subprocess.run(command, cwd=root, check=False)
    current = pull_request(root, url)["headRefOid"]
    if current != revision:
        print(f"PR head moved to {current}. Check that revision again.", file=sys.stderr)
        return 1
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, prog="pm-project")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="add missing PM files")
    init.add_argument("directory", nargs="?")
    resume_command = commands.add_parser("resume", help="read context and the first unchecked step")
    resume_command.add_argument("directory", nargs="?")
    checks = commands.add_parser("checks", help="read GitHub checks and recheck the PR head")
    checks.add_argument("pr", nargs="?", help="PR number, URL, or branch")
    checks.add_argument("--project", dest="directory")
    checks.add_argument("--watch", action="store_true")
    checks.add_argument("--required", action="store_true")
    args = parser.parse_args()

    try:
        root = project_root(args.directory)
        if args.command == "init":
            initialize(root)
        elif args.command == "resume":
            resume(root)
        else:
            return check_pull_request(root, args.pr, args.watch, args.required)
    except subprocess.CalledProcessError as error:
        return error.returncode
    except (OSError, ValueError) as error:
        print(f"pm-project: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
