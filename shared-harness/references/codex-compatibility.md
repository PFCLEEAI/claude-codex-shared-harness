# Shared workflows in Codex

The source skill and command bodies stay in Claude's directories. Treat tool
spelling and runtime hooks as implementation details to translate, not capabilities
that become available by sharing a file.

- `Read`, `Write`, `Edit`, `Bash`, `Grep`, and `Glob`: use Codex filesystem,
  patch, command, and search tools. `AskUserQuestion`: use the available user
  question tool or ask in conversation. `$ARGUMENTS` is the user's supplied input.
- `Agent` / `Task` and `.claude/agents/*.md`: read the agent instructions as role
  guidance. Use native Codex delegation only when available and authorized; if
  unavailable, execute the applicable steps sequentially. Claude model IDs,
  task IDs, orchestration plugins, and hook events do not transfer.
- MCP tools: discover the current Codex tool surface and map by capability,
  never by assumed `mcp__...` spelling. A configured but disabled server is
  unavailable until enabled. Report a missing required integration honestly.
- Source-relative scripts, references and assets resolve from the original
  skill directory (symlinks preserve it). Replace obsolete `/mnt/skills`,
  `/mnt/data`, `/home/claude`, and missing `~/.codex/skills/<name>` examples with
  the actual source skill path and current workspace/output directory.
- Use native Codex artifact, browser and connector skills when the task needs
  their tools. Google Workspace API guidance can be shared, but connector names
  and response schemas require the actual available integration. Local document
  scripts may need their documented dependencies installed separately.
- Claude's stop hooks, usage cache, cron runner, skill telemetry and automatic
  memory capture do not run in Codex. Maintain `_pm/context.md` explicitly.
  Auto-improvement workflows must not rewrite a shared skill without the user's
  authorization. Resource limits in shared memory apply to spawned sessions.
- This bridge never installs GBrain or LazyCodex, changes Claude settings, or
  copies authentication, chat transcripts or session logs. Shared notes and PM
  handoffs provide continuity; a running session's hidden state is not shared.

Skipped Claude-only skills: `built-in-browser`, `chrome-browser`, `computer-use`,
`import-memory`, `docs`, and `morning`. Use the configured Codex browser/control,
document, memory and scheduling tools for equivalent tasks. Skipped commands:
`api-cost` (Claude usage), `loop` (missing Claude scheduler scripts), and `design`
(unconfigured design MCP activation). The generated sync report lists every skip,
including duplicate names and superseded loose Markdown skills.
