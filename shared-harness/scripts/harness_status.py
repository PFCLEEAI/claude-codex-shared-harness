#!/usr/bin/env python3
"""Read-only Claude Code / Codex shared-harness status report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - kept for older Python builds.
    tomllib = None  # type: ignore[assignment]


HOME = Path.home()
CODEX_ROOT = HOME / ".codex"
CLAUDE_ROOT = HOME / ".claude"
CANONICAL_SKILL = CODEX_ROOT / "skills" / "shared-harness"
CLAUDE_MIRROR = CLAUDE_ROOT / "skills" / "shared-harness"
CLAUDE_COMMAND = CLAUDE_ROOT / "commands" / "shared-harness.md"
WRAPPER = HOME / ".local" / "bin" / "shared-harness"
PM_BOOTSTRAP = CODEX_ROOT / "scripts" / "bootstrap-pm-brain.sh"
CLAUDE_TO_CODEX_SYNC = CODEX_ROOT / "scripts" / "sync-claude-skills-to-codex.py"
CODEX_CONFIG = CODEX_ROOT / "config.toml"
CODEX_MCP = CODEX_ROOT / "mcp.json"
CLAUDE_MCP = CLAUDE_ROOT / ".mcp.json"
MANIFEST_NAME = ".shared-harness-manifest.json"

SECRET_KEY_RE = re.compile(r"(key|token|secret|password|credential|auth)", re.I)


def redact(key: str, value: Any) -> Any:
    if SECRET_KEY_RE.search(key):
        return "<redacted>"
    if isinstance(value, dict):
        return {k: redact(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(key, item) for item in value]
    return value


def load_json(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - audit reports parse errors directly.
        return {}, f"parse_error: {exc}"
    if not isinstance(data, dict):
        return {}, "parse_error: root is not an object"
    return data, None


def parse_toml_text_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {"features": {}, "skills": {"config": []}}
    section: str | None = None
    current_skill: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[features]":
            section = "features"
            current_skill = None
            continue
        if line == "[[skills.config]]":
            section = "skills.config"
            current_skill = {}
            data["skills"]["config"].append(current_skill)
            continue
        if line.startswith("["):
            section = None
            current_skill = None
            continue
        if "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        parsed: Any
        if value in {"true", "false"}:
            parsed = value == "true"
        elif value.startswith('"') and value.endswith('"'):
            parsed = value[1:-1]
        else:
            parsed = value
        if section == "features":
            data["features"][key] = parsed
        elif section == "skills.config" and current_skill is not None:
            current_skill[key] = parsed
    return data


def load_codex_config() -> tuple[dict[str, Any], str | None]:
    if not CODEX_CONFIG.exists():
        return {}, "missing"
    try:
        raw = CODEX_CONFIG.read_text(encoding="utf-8")
        if tomllib is not None:
            return tomllib.loads(raw), None
        return parse_toml_text_fallback(raw), None
    except Exception as exc:  # noqa: BLE001
        return {}, f"parse_error: {exc}"


def mcp_servers(path: Path) -> dict[str, Any]:
    data, error = load_json(path)
    servers = data.get("mcpServers", data.get("servers", {}))
    if not isinstance(servers, dict):
        servers = {}
        error = error or "mcpServers is not an object"
    return {
        "path": str(path),
        "exists": path.exists(),
        "error": error,
        "count": len(servers),
        "names": sorted(servers.keys()),
    }


def count_files(root: Path, pattern: str, dirs_only: bool = False) -> dict[str, Any]:
    if not root.exists():
        return {"path": str(root), "exists": False, "count": 0}
    if dirs_only:
        count = sum(1 for item in root.iterdir() if item.is_dir())
    else:
        count = sum(1 for _ in root.rglob(pattern))
    return {"path": str(root), "exists": True, "count": count}


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    files: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            files.append(str(path.relative_to(root)))
    return sorted(files)


def mirror_status() -> dict[str, Any]:
    canonical_files = relative_files(CANONICAL_SKILL)
    mirror_files = relative_files(CLAUDE_MIRROR)
    shared = sorted(set(canonical_files) & set(mirror_files))
    changed = [
        name
        for name in shared
        if file_sha256(CANONICAL_SKILL / name) != file_sha256(CLAUDE_MIRROR / name)
    ]
    return {
        "canonical_exists": CANONICAL_SKILL.exists(),
        "mirror_exists": CLAUDE_MIRROR.exists(),
        "canonical_file_count": len(canonical_files),
        "mirror_file_count": len(mirror_files),
        "missing_in_mirror": sorted(set(canonical_files) - set(mirror_files)),
        "extra_in_mirror": sorted(set(mirror_files) - set(canonical_files)),
        "changed_files": changed,
        "manifest": {
            "canonical": (CANONICAL_SKILL / MANIFEST_NAME).exists(),
            "mirror": (CLAUDE_MIRROR / MANIFEST_NAME).exists(),
        },
    }


def status() -> dict[str, Any]:
    config, config_error = load_codex_config()
    features = config.get("features", {}) if isinstance(config, dict) else {}
    skills_config = (
        config.get("skills", {}).get("config", [])
        if isinstance(config.get("skills"), dict)
        else []
    )
    enabled_skills = [
        item.get("path")
        for item in skills_config
        if isinstance(item, dict) and item.get("enabled") is True and item.get("path")
    ]
    return {
        "roots": {
            "home": str(HOME),
            "codex": str(CODEX_ROOT),
            "claude": str(CLAUDE_ROOT),
            "canonical_skill": str(CANONICAL_SKILL),
            "claude_mirror": str(CLAUDE_MIRROR),
        },
        "codex": {
            "config_path": str(CODEX_CONFIG),
            "config_error": config_error,
            "feature_flags": redact("features", features),
            "enabled_skills_count": len(enabled_skills),
            "enabled_skills": enabled_skills,
            "mcp": mcp_servers(CODEX_MCP),
        },
        "claude": {
            "mcp": mcp_servers(CLAUDE_MCP),
            "skills": count_files(CLAUDE_ROOT / "skills", "SKILL.md"),
            "commands": count_files(CLAUDE_ROOT / "commands", "*.md"),
            "agents": count_files(CLAUDE_ROOT / "agents", "*.md"),
            "shared_harness_command": {
                "path": str(CLAUDE_COMMAND),
                "exists": CLAUDE_COMMAND.exists(),
            },
        },
        "shared_harness": {
            "mirror": mirror_status(),
            "wrapper": {
                "path": str(WRAPPER),
                "exists": WRAPPER.exists(),
                "executable": os.access(WRAPPER, os.X_OK),
            },
            "pm_bootstrap": {
                "path": str(PM_BOOTSTRAP),
                "exists": PM_BOOTSTRAP.exists(),
                "executable": os.access(PM_BOOTSTRAP, os.X_OK),
            },
            "claude_to_codex_sync": {
                "path": str(CLAUDE_TO_CODEX_SYNC),
                "exists": CLAUDE_TO_CODEX_SYNC.exists(),
            },
        },
    }


def print_human(report: dict[str, Any]) -> None:
    print("Shared Harness Status")
    print(f"- Codex root: {report['roots']['codex']}")
    print(f"- Claude root: {report['roots']['claude']}")
    print(f"- Canonical skill: {report['roots']['canonical_skill']}")
    print(f"- Claude mirror: {report['roots']['claude_mirror']}")
    print("")
    features = report["codex"]["feature_flags"]
    print("Codex")
    print(f"- Config: {report['codex']['config_path']} ({report['codex']['config_error'] or 'ok'})")
    for name in sorted(features):
        print(f"- Feature {name}: {features[name]}")
    print(f"- Enabled skills: {report['codex']['enabled_skills_count']}")
    for path in report["codex"]["enabled_skills"]:
        print(f"  - {path}")
    codex_mcp = report["codex"]["mcp"]
    print(f"- MCP servers: {codex_mcp['count']} {codex_mcp['names']}")
    print("")
    claude = report["claude"]
    print("Claude")
    print(f"- MCP servers: {claude['mcp']['count']} {claude['mcp']['names']}")
    print(f"- Skills: {claude['skills']['count']}")
    print(f"- Commands: {claude['commands']['count']}")
    print(f"- Agents: {claude['agents']['count']}")
    print(f"- Shared command exists: {claude['shared_harness_command']['exists']}")
    print("")
    shared = report["shared_harness"]
    mirror = shared["mirror"]
    print("Shared Harness")
    print(f"- Mirror exists: {mirror['mirror_exists']}")
    print(f"- Missing in mirror: {len(mirror['missing_in_mirror'])}")
    print(f"- Extra in mirror: {len(mirror['extra_in_mirror'])}")
    print(f"- Changed mirrored files: {len(mirror['changed_files'])}")
    print(f"- Wrapper exists/executable: {shared['wrapper']['exists']}/{shared['wrapper']['executable']}")
    print(f"- PM bootstrap exists/executable: {shared['pm_bootstrap']['exists']}/{shared['pm_bootstrap']['executable']}")
    print(f"- Claude-to-Codex sync exists: {shared['claude_to_codex_sync']['exists']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    report = status()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
