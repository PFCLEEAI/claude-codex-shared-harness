# File Ownership

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
