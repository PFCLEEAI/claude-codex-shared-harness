# Run a project from one PM session

The PM session owns the project outcome. It receives requests, assigns work,
reviews the results, and keeps the project ready for another session to resume.

## Start or resume

1. Open the project and run `pm-project resume`. Read `_pm/memory.md`, the
   roadmap, and the linked contract and handoffs. Use Git and the current PR to
   confirm the branch, revision, and readiness of the next step.
2. For a new project, run `pm-project init` from its checkout. For a project
   inside another checkout, pass its directory explicitly. Fill in the scope,
   milestone, and acceptance checks before dispatching work.
3. The coordinator updates context, roadmap, checklist, and work log. Keep
   milestone IDs aligned. Commit the notes with the project when another
   machine or fresh checkout needs them.

## Delegate and verify

1. Write a brief in `_pm/contracts/<task>.md` with the outcome, base revision,
   files the worker may edit, and checks that demonstrate acceptance.
2. In an Orca project session, delegate through Orca orchestration. Use a
   separate worktree for edits and the configured worker agent. Run any resource
   check required on the host before starting a worker. For example:

   ```sh
   orca orchestration worker-start --environment local \
     --spec-file _pm/contracts/M1.md --worktree new-child --agent codex
   ```

   From a PM chat outside the project, resolve the target with
   `orca project setups --environment local --json`. Use
   `--worktree new-top-level --repo id:<repo-id> --base-branch <ref>` to put the
   worker in that project's checkout at the assigned revision.

3. Have the worker return a [handoff](handoff-template.md) with the tested
   commit, changed paths, commands, results, and blockers. Read the report from
   its worktree or collect it with the dispatch result. Keep the evidence in the
   coordinator's project. If feedback requires another change, use the same
   Orca dispatch or assign a follow-up with the new acceptance check.
4. Verify the integrated change against the contract. Record the revision with
   each result, including local tests and any independent review.

## Track CI and releases

1. Run `pm-project checks <pr> --watch` when the branch is on GitHub. Use
   `--required` when checking only the checks required by repository rules.
   The command reads the PR head before and after so a change during the wait
   invalidates the result. Record the head, check link, and tested revision from
   the runner when CI tests a generated merge commit.
2. Route failures back to the relevant worker with the failing job and expected
   behavior. Recheck CI after the fix lands on the PR branch.
3. For an authorized release, follow the project's deployment runbook. Record
   the deployed revision, environment, deployment link, and smoke-test result.
   If the project has no CI or deployment workflow, leave that step open and
   record the missing prerequisite.

At handoff, put the next action and any blocker in `_pm/context.md`. Link to
the relevant checklist item and evidence so a fresh session can resume.
