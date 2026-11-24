# Verify a cross-session PM handoff

Use the worker worktree at the assigned revision. Verify the installed
`pm-project` command from a separate session and leave a project the coordinator
can resume.

1. Create a temporary fixture directory using `mktemp` and run
   `pm-project init <fixture>`.
2. Fill its `_pm/context.md` with the line `Worker handoff ready for coordinator.`
   and put two ordered steps under `## M1 Verify handoff` in its checklist.
   Mark the first step complete and leave `Verify the worker receipt.` unchecked.
3. Run `pm-project resume <fixture>` in a fresh process. Confirm that it shows
   the context line and the pending step.
4. Save a handoff to `_pm/handoffs/M3-worker-resumption.md` in the worker
   worktree and return it through Orca. Include the fixture path, tested
   revision, verification commands, and result so the coordinator can repeat
   the resume check.

Only write to the fixture and the new handoff file. The fixture needs to remain
available for the coordinator's check.

Placement: this machine (local), set up on this machine.
