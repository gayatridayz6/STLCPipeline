import json
from pathlib import Path
import shutil
import tempfile
import unittest

from run_stlc import WorkflowError, approve, change_blocker, complete, load_state, preflight, run_dir, start, waive_execution


PROJECT = Path(__file__).resolve().parents[2]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        config_dir = self.root / ".github" / "config"
        config_dir.mkdir(parents=True)
        config = json.loads((PROJECT / ".github/config/project.json").read_text(encoding="utf-8"))
        self.config = config
        (config_dir / "project.json").write_text(json.dumps(config), encoding="utf-8")
        hooks = self.root / ".github" / "hooks"
        hooks.mkdir()
        for name in ("pre_stage_validation", "artifact_contract_guard", "approval_gate_guard",
                     "java_validation_guard"):
            shutil.copyfile(PROJECT / ".github/hooks" / (name + ".py"), hooks / (name + ".py"))
        workflow = self.root / config["workflowDefinition"]
        workflow.parent.mkdir(parents=True)
        workflow.write_text("class STLCWorkflowOrchestrator {}", encoding="utf-8")
        for artifact in config["artifacts"].values():
            path = self.root / artifact
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Template", encoding="utf-8")
        self.input_file = self.root / "input.txt"
        self.input_file.write_text("AC1: Search returns an existing book\n", encoding="utf-8")
        self.ticket = "EPMCDMETST-66524"

    def artifact(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_start_needs_real_input_and_all_artifact_contracts(self):
        self.assertIsNotNone(preflight(self.root, self.input_file))
        self.input_file.write_text("", encoding="utf-8")
        with self.assertRaisesRegex(WorkflowError, "nonempty"):
            start(self.root, self.ticket, self.input_file)
        self.input_file.write_text("Requirement", encoding="utf-8")
        (self.root / self.config["artifacts"]["stage-03"]).unlink()
        with self.assertRaisesRegex(WorkflowError, "artifact_contract_guard"):
            start(self.root, self.ticket, self.input_file)

    def test_approval_route_and_resume(self):
        start(self.root, self.ticket, self.input_file)
        artifact = self.artifact("triage.md", "# Analysis\ngenerate-new-tests\n")
        with self.assertRaisesRegex(WorkflowError, "Human approval"):
            complete(self.root, self.ticket, "stage-01", artifact, "generate-new-tests")
        approve(self.root, self.ticket, "stage-01", "Reviewer")
        with self.assertRaisesRegex(WorkflowError, "routing recommendation"):
            complete(self.root, self.ticket, "stage-01", self.artifact("wrong.md", "Analysis"), "generate-new-tests")
        complete(self.root, self.ticket, "stage-01", artifact, "generate-new-tests")
        state = load_state(run_dir(self.root, self.ticket))
        self.assertEqual(state["current"], "stage-02")
        self.assertEqual(state["route"], "generate-new-tests")
        mapped_artifact = self.root / self.config["artifacts"]["stage-01"]
        self.assertEqual(mapped_artifact.read_text(), artifact.read_text())
        self.assertEqual(len((run_dir(self.root, self.ticket) / "audit.jsonl").read_text().splitlines()), 3)
        with self.assertRaisesRegex(WorkflowError, "already exists"):
            start(self.root, self.ticket, self.input_file)
        with self.assertRaisesRegex(WorkflowError, "current stage"):
            approve(self.root, self.ticket, "stage-03", "Reviewer")

    def test_reuse_existing_tests_skips_design_and_engineering(self):
        start(self.root, self.ticket, self.input_file)
        approve(self.root, self.ticket, "stage-01", "Reviewer")
        complete(
            self.root, self.ticket, "stage-01",
            self.artifact("triage.md", "reuse-existing-tests: test matched to story"), "reuse-existing-tests",
        )
        self.assertEqual(load_state(run_dir(self.root, self.ticket))["current"], "stage-04b")
        approve(self.root, self.ticket, "stage-04b", "Reviewer")
        complete(self.root, self.ticket, "stage-04b", self.artifact("execution.md", "Executed: 2 passed"), None)
        self.assertEqual(load_state(run_dir(self.root, self.ticket))["current"], "complete")

    def test_every_stage_including_hitl_needs_explicit_approval(self):
        start(self.root, self.ticket, self.input_file)
        for stage in ("stage-01", "stage-02", "stage-03", "stage-04a", "stage-04b",
                      "stage-05", "stage-06", "stage-07", "stage-08"):
            artifact = self.artifact("output.md", f"# {stage}\n" + (
                "generate-new-tests\n" if stage == "stage-01" else "Reviewed evidence\n"
            ))
            with self.assertRaisesRegex(WorkflowError, "Human approval"):
                complete(self.root, self.ticket, stage, artifact,
                         "generate-new-tests" if stage == "stage-01" else None)
            approve(self.root, self.ticket, stage, "Reviewer")
            complete(self.root, self.ticket, stage, artifact,
                     "generate-new-tests" if stage == "stage-01" else None)
        self.assertEqual(load_state(run_dir(self.root, self.ticket))["current"], "complete")

    def test_invalid_ticket_and_placeholder_rejected(self):
        with self.assertRaisesRegex(WorkflowError, "Jira-style"):
            start(self.root, "../escape", self.input_file)
        start(self.root, self.ticket, self.input_file)
        approve(self.root, self.ticket, "stage-01", "Reviewer")
        with self.assertRaisesRegex(WorkflowError, "placeholder"):
            complete(self.root, self.ticket, "stage-01",
                     self.artifact("template.md", "generate-new-tests <criterion>"), "generate-new-tests")

    def test_blocked_stage_revokes_approval_until_resolved_and_reapproved(self):
        start(self.root, self.ticket, self.input_file)
        approve(self.root, self.ticket, "stage-01", "Reviewer")
        change_blocker(self.root, self.ticket, "Missing target", False)
        with self.assertRaisesRegex(WorkflowError, "Resolve the current blocker"):
            approve(self.root, self.ticket, "stage-01", "Reviewer")
        with self.assertRaisesRegex(WorkflowError, "blocked stage"):
            complete(self.root, self.ticket, "stage-01",
                     self.artifact("triage.md", "generate-new-tests"), "generate-new-tests")
        change_blocker(self.root, self.ticket, "Target supplied", True)
        with self.assertRaisesRegex(WorkflowError, "Human approval"):
            complete(self.root, self.ticket, "stage-01",
                     self.artifact("triage.md", "generate-new-tests"), "generate-new-tests")
        approve(self.root, self.ticket, "stage-01", "Reviewer")
        complete(self.root, self.ticket, "stage-01",
                 self.artifact("triage.md", "generate-new-tests"), "generate-new-tests")

    def test_execution_waiver_requires_blocker_and_new_approval_and_explicit_evidence(self):
        start(self.root, self.ticket, self.input_file)
        with self.assertRaisesRegex(WorkflowError, "Stage 4b"):
            waive_execution(self.root, self.ticket, "Reviewer", "No target")
        state = load_state(run_dir(self.root, self.ticket))
        state["current"] = "stage-04b"
        (run_dir(self.root, self.ticket) / "state.json").write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(WorkflowError, "recorded execution blocker"):
            waive_execution(self.root, self.ticket, "Reviewer", "No target")
        approve(self.root, self.ticket, "stage-04b", "Reviewer")
        change_blocker(self.root, self.ticket, "No target", False)
        with self.assertRaisesRegex(WorkflowError, "human approver"):
            waive_execution(self.root, self.ticket, "", "No target")
        waive_execution(self.root, self.ticket, "Reviewer", "No target; review-only")
        with self.assertRaisesRegex(WorkflowError, "already been waived"):
            waive_execution(self.root, self.ticket, "Reviewer", "No target")
        with self.assertRaisesRegex(WorkflowError, "Human approval"):
            complete(self.root, self.ticket, "stage-04b", self.artifact("report.md", "Results"), None)
        approve(self.root, self.ticket, "stage-04b", "Reviewer")
        with self.assertRaisesRegex(WorkflowError, "REAL_APP_NOT_EXECUTED"):
            complete(self.root, self.ticket, "stage-04b", self.artifact("report.md", "2 passed"), None)
        complete(self.root, self.ticket, "stage-04b",
                 self.artifact("report.md", "REAL_APP_NOT_EXECUTED; review-only"), None)
        state = load_state(run_dir(self.root, self.ticket))
        self.assertEqual(state["mode"], "review-only")
        self.assertEqual(state["current"], "stage-05")
        self.assertEqual(state["execution_waiver"]["by"], "Reviewer")


if __name__ == "__main__":
    unittest.main()
