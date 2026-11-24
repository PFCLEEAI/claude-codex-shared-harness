# M3 Worker resumption handoff

- Result: passed on November 24, 2026.
- Worker: Claude Code in a separate Orca worktree.
- Tested commit: `d9ce3109b19d61332f410ff960edafb7648842f1`.
- The worker created a scratch project using `pm-project init`, filled in the
  context, and left the second checklist step unchecked.
- `pm-project resume` printed the saved context and the expected next step,
  `M1 Verify handoff — Verify the worker receipt.`
- Orca delivered the completed handoff to the Codex coordinator. The coordinator
  ran the installed command against the worker's fixture and verified the same
  output and successful exit.

[Acceptance criteria](../contracts/M3-worker-resumption.md)
