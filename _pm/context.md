# Shared PM workflow

The project goal is a repeatable handoff between Claude Code and Codex, with one
coordinator tracking worker results, test evidence, and CI on the current PR.

The installed command initialized a clean directory and resumed its first
milestone. A separate Claude Code worker delivered a handoff through Orca, and
the Codex coordinator resumed the worker's fixture from a fresh process. The
test and install jobs passed on the draft PR.

Start the next project in its Orca workspace and follow the
[coordinator runbook](../shared-harness/references/pm-coordinator.md). Verify its
own test and deployment entry points before closing release steps.

[Roadmap](roadmap.md) · [Checklist](checklist.md) · [Work log](work-log.md) ·
[Draft PR](https://github.com/PFCLEEAI/claude-codex-shared-harness/pull/1)
