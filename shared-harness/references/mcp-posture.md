# MCP Posture

- Treat MCP as lazy and call-based. Do not start MCP servers to answer a posture question.
- It is safe to parse `~/.codex/mcp.json` and `~/.claude/.mcp.json`.
- It is safe to run listing commands such as `codex mcp list` when needed; do not use commands that connect to or launch a server unless the user explicitly asks.
- Keep Codex `features.tool_search_always_defer_mcp_tools = true` and `features.plugins = false` unless the user asks for a runtime change.
- Report configured server names and counts, not secret environment values.
- If an MCP config contains env fields, redact values for keys matching token, key, secret, password, credential, or auth.
