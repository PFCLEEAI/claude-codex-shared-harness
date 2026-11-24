"""Exercise the shared PM command through project and PR handoffs."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "shared-harness" / "scripts" / "pm_project.py"
sys.path.insert(0, str(SCRIPT.parent))
import pm_project


class ProjectTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.notes = self.root / "_pm"

    def command(self, *args, cwd=None):
        return subprocess.check_output(
            [sys.executable, str(SCRIPT), *args], cwd=cwd or self.root, text=True
        )

    def test_second_init_preserves_authored_context_and_checklist(self):
        self.command("init", str(self.root))
        for name in ("context.md", "memory.md", "work-log.md", "roadmap.md", "checklist.md"):
            self.assertTrue((self.notes / name).is_file())
        for name in ("contracts", "handoffs"):
            self.assertTrue((self.notes / name / ".gitkeep").is_file())
        self.assertIn("checklist.md#m1-define-the-first-milestone",
                      (self.notes / "roadmap.md").read_text())
        context = "# Project handoff\n\nCurrent branch and blocker."
        (self.notes / "context.md").write_text(context)
        plan = "# Checklist\n\n## M3 Verify\n1. [x] Build\n2. [ ] Smoke test."
        (self.notes / "checklist.md").write_text(plan)

        self.command("init")
        self.assertEqual((self.notes / "context.md").read_text(), context)
        self.assertEqual((self.notes / "checklist.md").read_text(), plan)
        output = self.command("resume", cwd=self.notes / "contracts")
        self.assertIn("Current branch and blocker.", output)
        self.assertIn("M3 Verify — Smoke test.", output)

    def test_keeps_existing_named_roadmap_and_authored_plan(self):
        self.notes.mkdir()
        (self.notes / "deployment-roadmap.md").write_text("# M7 Deployment\n")
        (self.notes / "checklist.md").write_text("# Deploy checklist\n- [ ] Review release.\n")

        self.command("init")
        self.assertFalse((self.notes / "roadmap.md").exists())
        self.assertIn("Review release.", self.command("resume"))
        self.assertEqual((self.notes / "deployment-roadmap.md").read_text(), "# M7 Deployment\n")

    def test_repairs_a_partial_starter(self):
        self.notes.mkdir()
        (self.notes / "roadmap.md").write_text(pm_project.ROADMAP)
        self.command("init")
        self.assertEqual((self.notes / "checklist.md").read_text(), pm_project.CHECKLIST)


class PullRequestTest(unittest.TestCase):
    url = "https://github.com/example/project/pull/4"

    def revision(self, revision):
        return json.dumps({"url": self.url, "headRefOid": revision})

    def test_forwards_ci_status_for_the_same_pr_head(self):
        root = Path(".")
        with (
            patch.object(subprocess, "check_output", side_effect=[self.revision("a")] * 2),
            patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 8)) as run,
        ):
            status = pm_project.check_pull_request(root, "4", watch=True, required=True)

        self.assertEqual(status, 8)
        run.assert_called_once_with(
            ["gh", "pr", "checks", self.url, "--watch", "--fail-fast", "--required"],
            cwd=root,
            check=False,
        )

    def test_rejects_success_after_the_pr_head_moves(self):
        with (
            patch.object(subprocess, "check_output",
                         side_effect=[self.revision("a"), self.revision("b")]),
            patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)),
        ):
            status = pm_project.check_pull_request(Path("."), "4", watch=False, required=False)

        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
