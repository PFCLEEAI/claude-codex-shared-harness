# Security Policy

## Public Package Boundary

This repository should contain only reusable shared-harness files:

- `shared-harness/SKILL.md`
- `shared-harness/agents/openai.yaml`
- `shared-harness/scripts/*.py`
- `shared-harness/references/*.md`
- install and repository metadata files

Do not commit:

- auth files
- MCP config files
- Claude/Codex settings files
- session logs
- history files
- SQLite databases
- browser profiles
- generated manifests
- `.env` files

## Reporting

Open a GitHub issue for security-sensitive bugs that do not include live credentials. Rotate any exposed credentials immediately.
