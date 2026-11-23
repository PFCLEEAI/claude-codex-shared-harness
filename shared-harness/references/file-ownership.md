# File Ownership

The opt-in `sync-to-codex.sh` workflow additionally owns `~/.agents/skills/`
links, matching pre-existing `~/.codex/skills/` collisions, the managed
shared-harness section of `~/.codex/AGENTS.md`, and generated adapters/reports
under `~/.codex/shared-harness/`. Back up existing entries before replacement.
Claude source files are read-only in this mode; do not run the legacy mirror.
Explicit user requests to compare or add MCP entries are separate from sync.

Allowed bridge-owned surfaces:

- `~/.codex/skills/shared-harness/**`
- `~/.claude/skills/shared-harness/**`
- `~/.claude/commands/shared-harness.md`
- `~/.local/bin/shared-harness`
- PM status files for the active lane.

Config exception:

- `~/.codex/config.toml` may receive one `[[skills.config]]` entry for `~/.codex/skills/shared-harness/SKILL.md` when missing.

Do not edit:

- MCP configs, Claude settings, Claude global instructions, unrelated skills, unrelated commands, unrelated agents, auth files, caches, sessions, or project repositories.
