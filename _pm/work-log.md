# Shared PM workflow log

## 2026-11-24

- Confirmed the shared PM contract and created an isolated worktree from the
  current default branch. Orca was reachable. The initial worker resource check
  deferred launch, so implementation proceeded in the coordinator session.
- The project CLI passed five tests. Coverage includes preserved existing
  notes, recovery of a partial scaffold, session resumption, and invalidation
  when a PR head moves while checks are being read.
- Installed the command and linked the coordinator instructions for both
  harnesses. A new process read the first milestone in a clean installation.
- Launched Claude Code through Orca from the Codex coordinator after the
  resource check passed. The worker returned the fixture and report, and the
  coordinator independently verified resume output. [Worker result](handoffs/M3-worker-resumption.md)
- Published the pilot in [draft PR 1](https://github.com/PFCLEEAI/claude-codex-shared-harness/pull/1).
  The installed `pm-project checks 1 --watch` reported success for the test
  and install jobs on `d9ce310`. [CI run](https://github.com/PFCLEEAI/claude-codex-shared-harness/actions/runs/45307238829)
