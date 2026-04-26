# Command, Skill, Agent Map

- Skill: reusable Codex/Claude procedural knowledge loaded by trigger or explicit request.
- Command: Claude-facing slash-command markdown that points to the skill and wrapper.
- Wrapper: shell entry point for deterministic status checks from either harness.
- Agent: a lane or role used by PM orchestration; it should receive a scoped write set and handoff target.
- MCP: external tool/server integration. Inventory it by config file, but do not launch it for status audits.
- Canonical direction for this harness is Codex skill to Claude mirror.
- Existing Claude-to-Codex sync scripts are separate and should be audited, not replaced, unless explicitly requested.
