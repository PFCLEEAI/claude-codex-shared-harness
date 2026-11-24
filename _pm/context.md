# Shared PM workflow

The project goal is a repeatable handoff between Claude Code and Codex, with one
coordinator tracking worker results, test evidence, and CI on the current PR.

The initializer, resume command, and PR-head check passed five local tests.
The installed command initialized a clean directory and resumed its first
milestone. The next actions are the independent Orca worker pilot and
verification of a draft PR's checks.

[Roadmap](roadmap.md) · [Checklist](checklist.md) · [Work log](work-log.md)
