#!/usr/bin/env python3
"""Validate the shared Claude Code / Codex harness skill."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import py_compile
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


HOME = Path.home()
CODEX_ROOT = HOME / ".codex"
CLAUDE_ROOT = HOME / ".claude"
SKILL = CODEX_ROOT / "skills" / "shared-harness"
CLAUDE_SKILL = CLAUDE_ROOT / "skills" / "shared-harness"
CLAUDE_COMMAND = CLAUDE_ROOT / "commands" / "shared-harness.md"
WRAPPER = HOME / ".local" / "bin" / "shared-harness"
CODEX_CONFIG = CODEX_ROOT / "config.toml"
CODEX_MCP = CODEX_ROOT / "mcp.json"
CLAUDE_MCP = CLAUDE_ROOT / ".mcp.json"
MANIFEST_NAME = ".shared-harness-manifest.json"

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "scripts/harness_status.py",
    "scripts/sync_shared_harness.py",
    "scripts/validate_shared_harness.py",
    "references/mcp-posture.md",
    "references/pm-memory-contract.md",
    "references/command-skill-agent-map.md",
    "references/handoff-template.md",
    "references/file-ownership.md",
    "references/bash-commands.md",
]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    files: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            files.append(str(path.relative_to(root)))
    return sorted(files)


def mirror_drift() -> dict[str, list[str]]:
    canonical_files = set(relative_files(SKILL))
    mirror_files = set(relative_files(CLAUDE_SKILL))
    shared = sorted(canonical_files & mirror_files)
    changed = [
        rel
        for rel in shared
        if file_sha256(SKILL / rel) != file_sha256(CLAUDE_SKILL / rel)
    ]
    return {
        "missing": sorted(canonical_files - mirror_files),
        "extra": sorted(mirror_files - canonical_files),
        "changed": changed,
    }


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter delimiter")
    frontmatter = text[4:end]
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_codex_config() -> dict[str, Any]:
    raw = CODEX_CONFIG.read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(raw)
    features: dict[str, Any] = {}
    section: str | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped == "[features]":
            section = "features"
            continue
        if stripped.startswith("[") and stripped != "[features]":
            section = None
            continue
        if section == "features" and "=" in stripped:
            key, value = [part.strip() for part in stripped.split("=", 1)]
            features[key] = value == "true" if value in {"true", "false"} else value
    return {"features": features}


def mcp_count(path: Path) -> int:
    data = load_json(path)
    servers = data.get("mcpServers", data.get("servers", {}))
    if not isinstance(servers, dict):
        raise ValueError(f"{path} mcpServers is not an object")
    return len(servers)


def import_script(path: Path) -> None:
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def validate() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not (SKILL / rel).exists():
            errors.append(f"missing required file: {rel}")

    try:
        frontmatter = parse_frontmatter(SKILL / "SKILL.md")
        if set(frontmatter) != {"name", "description"}:
            errors.append(f"frontmatter must contain only name and description, got {sorted(frontmatter)}")
        if frontmatter.get("name") != "shared-harness":
            errors.append("frontmatter name must be shared-harness")
        description = frontmatter.get("description", "")
        if not description:
            errors.append("frontmatter description is empty")
        if len(description) > 1024:
            errors.append("frontmatter description exceeds 1024 characters")
        if not re.fullmatch(r"[a-z0-9-]{1,63}", frontmatter.get("name", "")):
            errors.append("frontmatter name must be lowercase hyphen-case under 64 chars")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"frontmatter validation failed: {exc}")

    for script in sorted((SKILL / "scripts").glob("*.py")):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                py_compile.compile(
                    str(script),
                    cfile=str(Path(tmp) / f"{script.name}.pyc"),
                    doraise=True,
                )
            import_script(script)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"script validation failed for {script.name}: {exc}")

    for path in (CODEX_MCP, CLAUDE_MCP):
        try:
            count = mcp_count(path)
            if count:
                warnings.append(f"{path} has {count} MCP server(s); verify they are intentional and lazy")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"MCP JSON validation failed for {path}: {exc}")

    try:
        features = load_codex_config().get("features", {})
        if features.get("tool_search_always_defer_mcp_tools") is not True:
            errors.append("Codex lazy MCP flag tool_search_always_defer_mcp_tools is not true")
        if features.get("plugins") is True:
            errors.append("Codex plugins feature is enabled; expected lazy/off posture")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Codex config validation failed: {exc}")

    if not CLAUDE_SKILL.exists():
        errors.append(f"Claude mirror missing: {CLAUDE_SKILL}")
    else:
        for rel in REQUIRED_FILES:
            if not (CLAUDE_SKILL / rel).exists():
                errors.append(f"Claude mirror missing required file: {rel}")
        drift = mirror_drift()
        if drift["missing"]:
            errors.append(f"Claude mirror missing canonical files: {drift['missing']}")
        if drift["extra"]:
            errors.append(f"Claude mirror has extra files: {drift['extra']}")
        if drift["changed"]:
            errors.append(f"Claude mirror changed files: {drift['changed']}")

    if not CLAUDE_COMMAND.exists():
        errors.append(f"Claude command missing: {CLAUDE_COMMAND}")
    if not WRAPPER.exists():
        errors.append(f"wrapper missing: {WRAPPER}")
    elif not os.access(WRAPPER, os.X_OK):
        errors.append(f"wrapper is not executable: {WRAPPER}")

    for path in (SKILL / MANIFEST_NAME, CLAUDE_SKILL / MANIFEST_NAME):
        if not path.exists():
            errors.append(f"manifest missing: {path}")
        else:
            try:
                manifest = load_json(path)
                if manifest.get("mcp_configs_mutated") is not False:
                    errors.append(f"manifest does not preserve MCP config posture: {path}")
                if manifest.get("settings_mutated") is not False:
                    errors.append(f"manifest does not preserve settings posture: {path}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"manifest parse failed for {path}: {exc}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    errors, warnings = validate()
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Shared harness validation")
        print(f"- OK: {result['ok']}")
        for warning in warnings:
            print(f"- Warning: {warning}")
        for error in errors:
            print(f"- Error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
