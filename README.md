# Claude Codex Shared Harness

SEO keywords: Claude Code, OpenAI Codex, Codex CLI, Claude Code skills, Codex skills, MCP audit, lazy MCP, AI agent workflow, multi-agent PM handoffs, developer automation.

`claude-codex-shared-harness` is a lightweight interoperability bridge for developers who use both Claude Code and OpenAI Codex. It keeps shared workflow rules, skills, shell commands, MCP posture checks, and PM handoff conventions aligned without merging each tool's runtime config.

## What It Does

- Mirrors a canonical Codex skill into Claude Code.
- Adds a `shared-harness` shell command for read-only status audits.
- Checks Claude and Codex MCP config posture without starting MCP servers.
- Validates skill frontmatter, mirror drift, wrapper install state, and lazy MCP behavior.
- Documents `_pm/` memory, PM lanes, handoffs, file ownership, and sync rules.

## What It Does Not Do

- It does not copy secrets, auth files, chat history, browser profiles, or session logs.
- It does not start MCP servers, plugins, browsers, Claude sessions, or Codex sessions.
- It does not try to make Claude Code and Codex use identical runtime settings.

## Install

From a clone of this repository:

```bash
./install.sh
```

Manual install:

```bash
mkdir -p ~/.codex/skills
cp -R shared-harness ~/.codex/skills/shared-harness
python3 ~/.codex/skills/shared-harness/scripts/sync_shared_harness.py
python3 ~/.codex/skills/shared-harness/scripts/validate_shared_harness.py
```

## Usage

Run a read-only status audit:

```bash
shared-harness
```

Machine-readable audit:

```bash
shared-harness --json
```

Refresh the Claude Code mirror from the canonical Codex skill:

```bash
python3 ~/.codex/skills/shared-harness/scripts/sync_shared_harness.py
```

Validate the bridge:

```bash
python3 ~/.codex/skills/shared-harness/scripts/validate_shared_harness.py
```

## Recommended Workflow

1. Keep `~/.codex/skills/shared-harness` as the canonical source.
2. Run sync only after changing the canonical skill.
3. Run validation after sync.
4. Use `shared-harness` anytime you want to audit Claude/Codex parity.
5. Keep MCP lazy: configure servers only when needed, and do not start them for audits.

## Public Safety Model

This repository is designed to be safe to publish:

- No personal machine path is required.
- No credentials or environment values are included.
- MCP config files are inspected by name/count only.
- Environment-like values are redacted when keys match token, key, secret, password, credential, or auth.
- Generated manifests and Python bytecode are ignored.

## Repository Layout

```text
shared-harness/
  SKILL.md
  agents/openai.yaml
  scripts/
    harness_status.py
    sync_shared_harness.py
    validate_shared_harness.py
  references/
    bash-commands.md
    command-skill-agent-map.md
    file-ownership.md
    handoff-template.md
    mcp-posture.md
    pm-memory-contract.md
install.sh
```

## License

MIT
