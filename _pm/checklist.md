# Shared PM workflow checklist

## M1 Project folder and resume

1. [x] Confirm the existing PM contract and create an isolated branch from the default branch.
2. [x] Scaffold `_pm/` in a clean project and preserve authored files on repeated or partial initialization. Covered by unit tests.
3. [x] Resume from the saved context and next unchecked checklist step in a fresh process. Covered by a subprocess starting in a nested project directory.

## M2 Install the coordinator workflow

1. [x] Document scoped worker briefs, worktree ownership, acceptance, and release evidence. [Runbook](../shared-harness/references/pm-coordinator.md)
2. [x] Install the project command and connect the shared runbook to Claude Code and Codex.
3. [x] Verify the installed command in a clean directory. The command created the notes and printed the starter milestone from a fresh process.

## M3 Verify a separate worker handoff

1. [x] Confirm the local worker resource check passes before dispatch.
2. [x] Dispatch a bounded verification task through Orca and collect the returned handoff. [Worker contract](contracts/M3-worker-resumption.md) · [Result](handoffs/M3-worker-resumption.md)
3. [x] Use the handoff and checklist to verify resumption from a fresh process. The coordinator read the same context line and pending step.

## M4 Verify PR checks and install rehearsal

1. [x] Run automated tests and exercise CI status handling, including a change to the PR head. Five local tests passed.
2. [x] Publish the reviewed branch and open a [draft pull request](https://github.com/PFCLEEAI/claude-codex-shared-harness/pull/1).
3. [x] Verify CI and the install rehearsal for the PR revision. Both jobs passed on `d9ce310`. [Run](https://github.com/PFCLEEAI/claude-codex-shared-harness/actions/runs/45307238829)
