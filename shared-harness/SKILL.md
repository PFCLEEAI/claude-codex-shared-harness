---
name: shared-harness
description: Shared Claude Code and Codex interoperability harness for keeping workflow rules, PM handoffs, skill/MCP/bash sync, wrapper commands, and lazy setup posture aligned. Use when working on Claude Code/Codex bridge workflows, shared harness audits, mirrored skills, MCP parity checks, shell command wrappers, PM memory conventions, or avoiding duplicate manual setup across both agents.
---

# Shared Harness

Use this skill when Claude Code and Codex need to share a workflow without merging their runtime configs. Choose the requested sync direction below and preserve each runtime's configuration.

## Claude sources shared with Codex

For a Claude-to-Codex setup, run `sync-to-codex.sh` from this repository's root.
This is a separate, read-only-on-Claude workflow: link compatible Claude skills
into `~/.agents/skills`, expose slash commands as live-source wrappers, and add
absolute instruction and memory references outside the GBrain block in Codex's
global AGENTS.md. The repository is the shared-harness skill's source in this
mode. Backups live outside skill discovery roots and use `.bak-<timestamp>` names.

Read [codex-compatibility.md](references/codex-compatibility.md) for tool mapping
and skipped Claude-only workflows. Rerun the script after adding Claude skills
or commands. It does not touch MCP config; compare `claude mcp list` with
`codex mcp list` separately and add only missing user-scope stdio entries.
Never run the legacy mirror script when the task forbids writes under `.claude`.
Fresh Codex verification sessions are permitted when explicitly requested.

## Legacy Codex-to-Claude workflow

1. Read the local `_pm/context.md` and `_pm/memory.md` before broad exploration when a project has `_pm/`.
2. Run `scripts/harness_status.py` for a read-only inventory of Codex and Claude posture.
3. Run `scripts/sync_shared_harness.py` only when the canonical Codex skill should be mirrored to Claude and the `shared-harness` wrapper/command should be refreshed.
4. Run `scripts/validate_shared_harness.py` after edits or syncs.
5. Do not start MCP servers, plugins, browsers, Claude sessions, or Codex sub-sessions just to inspect posture.

## Legacy mirror source of truth

- Canonical skill: `~/.codex/skills/shared-harness/`
- Claude mirror: `~/.claude/skills/shared-harness/`
- Claude command: `~/.claude/commands/shared-harness.md`
- Shell wrapper: `~/.local/bin/shared-harness`
- Generated manifest: `.shared-harness-manifest.json` in both canonical and mirrored skill folders

## Scripts

- `scripts/harness_status.py`: read-only audit of roots, feature flags, enabled skills, MCP config inventory, Claude skill/command/agent counts, mirror status, wrapper status, PM bootstrap status, and existing Claude-to-Codex sync status.
- `scripts/sync_shared_harness.py`: copy canonical shared-harness files to Claude, create the Claude command, create the shell wrapper, and write manifests. It must not edit MCP configs, settings, global instructions, or unrelated skills.
- `scripts/validate_shared_harness.py`: validate frontmatter, required files, Python syntax/importability, MCP JSON parseability, mirror presence, wrapper presence, manifest presence, and lazy MCP posture.

## References

Load only the reference needed for the task:

- `references/mcp-posture.md`: lazy MCP rules and audit boundaries.
- `references/pm-memory-contract.md`: `_pm` files, lane handoffs, and status updates.
- `references/command-skill-agent-map.md`: how commands, skills, agents, wrappers, and MCP relate.
- `references/handoff-template.md`: standard implementation/review/test handoff shape.
- `references/file-ownership.md`: allowed and forbidden write surfaces.
- `references/bash-commands.md`: supported shell wrapper and script commands.
