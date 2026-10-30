import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from token_dashboard import (
    AGENTS, COUNTERS, directory, finalize, hook, initialize, load, transcript_usage,
)


class TokenDashboardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.run = "STL-101-test"
        initialize(self.root, self.run, "STL-101")
        self.target = directory(self.root, self.run)
        self.parent = self.root / "claude-project" / "session-01.jsonl"
        self.transcript = (
            self.parent.parent / self.parent.stem / "subagents" / "agent-abc123.jsonl"
        )
        self.transcript.parent.mkdir(parents=True)

    def write_messages(self, messages):
        self.transcript.write_text(
            "".join(json.dumps(message) + "\n" for message in messages), encoding="utf-8"
        )

    def message(self, identifier="msg-1", input_tokens=20, output_tokens=10,
                cache_creation_input_tokens=3, cache_read_input_tokens=7):
        return {"type": "assistant", "message": {
            "id": identifier, "usage": {
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "cache_creation_input_tokens": cache_creation_input_tokens,
                "cache_read_input_tokens": cache_read_input_tokens,
            },
        }}

    def event(self, agent="triage-agent", tool_id="tool-1"):
        return {
            "hook_event_name": "PostToolUse", "tool_name": "Agent",
            "session_id": "session-01", "transcript_path": str(self.parent),
            "tool_use_id": tool_id,
            "tool_input": {"prompt": f"[STLC run={self.run} agent={agent}]\nAnalyze requirements"},
            "tool_response": {"agentId": "abc123"},
        }

    def test_initial_dashboard_lists_all_agents_with_unavailable_not_zero(self):
        data = load(self.target)
        self.assertEqual([row["agent"] for row in data["byAgent"]], list(AGENTS))
        self.assertTrue(all(row["totalTokens"] is None for row in data["byAgent"]))
        html = (self.target / "stlc_dashboard.html").read_text(encoding="utf-8")
        self.assertIn('class="metric">N/A', html)
        self.assertNotIn("<script", html)
        self.assertNotIn("https://", html)

    def test_actual_usage_includes_cache_and_deduplicates_stream_snapshots(self):
        self.write_messages([
            {"type": "user", "message": {"content": "PRIVATE REQUIREMENT"}},
            self.message(output_tokens=0), self.message(output_tokens=5), self.message(),
            self.message("msg-2", 5, 2, 0, 1),
        ])
        self.assertEqual(transcript_usage(self.transcript), dict(zip(COUNTERS, (25, 12, 3, 8))))
        hook(self.root, self.event())
        hook(self.root, self.event())
        data = load(self.target)
        self.assertEqual(data["measuredTotalTokens"], 48)
        self.assertEqual(data["recordedCalls"], 1)
        row = next(row for row in data["byAgent"] if row["agent"] == "triage-agent")
        self.assertEqual(row["telemetry"], "measured")
        self.assertEqual(row["totalTokens"], 48)
        self.assertNotIn("PRIVATE REQUIREMENT", (self.target / "token_usage.json").read_text())
        self.assertNotIn(str(self.transcript), (self.target / "token_usage.json").read_text())

    def test_resumed_agent_replaces_cumulative_snapshot(self):
        self.write_messages([self.message()])
        hook(self.root, self.event())
        self.write_messages([self.message(), self.message("msg-2")])
        hook(self.root, self.event(tool_id="tool-resume"))
        data = load(self.target)
        self.assertEqual(data["measuredTotalTokens"], 80)
        self.assertEqual(data["recordedCalls"], 1)

    def test_new_agent_attempt_counts_separately_and_partial_is_explicit(self):
        self.write_messages([self.message()])
        hook(self.root, self.event())
        failed = self.event(tool_id="failed-tool")
        failed["hook_event_name"] = "PostToolUseFailure"
        failed.pop("tool_response")
        with contextlib.redirect_stderr(io.StringIO()) as warning:
            hook(self.root, failed)
        self.assertIn("telemetry unavailable", warning.getvalue())
        data = load(self.target)
        self.assertEqual(data["recordedCalls"], 2)
        self.assertEqual(data["measuredCalls"], 1)
        self.assertEqual(data["measuredTotalTokens"], 40)
        row = next(row for row in data["byAgent"] if row["agent"] == "triage-agent")
        self.assertEqual(row["telemetry"], "partial")

    def test_unrelated_calls_are_ignored(self):
        unrelated = self.event()
        unrelated["tool_input"]["prompt"] = "Do some unrelated task"
        hook(self.root, unrelated)
        self.assertEqual(load(self.target)["recordedCalls"], 0)
        unrelated["tool_name"] = "Read"
        unrelated["tool_input"]["prompt"] = self.event()["tool_input"]["prompt"]
        hook(self.root, unrelated)
        self.assertEqual(load(self.target)["recordedCalls"], 0)

    def test_task_tool_and_multiple_agents(self):
        self.write_messages([self.message()])
        hook(self.root, self.event())
        second = self.event("reporting-closure-agent")
        second["tool_name"] = "Task"
        second["tool_response"]["agentId"] = "xyz456"
        path = self.transcript.with_name("agent-xyz456.jsonl")
        path.write_text(json.dumps(self.message("msg-2", 1, 2, 0, 0)) + "\n", encoding="utf-8")
        hook(self.root, second)
        finalize(self.root, self.run, "completed", "")
        data = load(self.target)
        self.assertEqual(data["measuredTotalTokens"], 43)
        self.assertEqual(data["recordedCalls"], 2)
        self.assertEqual(data["status"], "completed")

    def test_nested_orchestrator_calls_use_sibling_subagent_transcripts(self):
        self.write_messages([self.message()])
        nested = self.event()
        nested["transcript_path"] = str(self.transcript.with_name("agent-coordinator.jsonl"))
        hook(self.root, nested)
        self.assertEqual(load(self.target)["measuredTotalTokens"], 40)

    def test_cli_persists_html_with_paths_containing_spaces(self):
        project = Path(__file__).resolve().parents[1]
        copied_root = self.root / "project with spaces"
        workflow = copied_root / "workflow"
        workflow.mkdir(parents=True)
        script = workflow / "token_dashboard.py"
        shutil.copyfile(project / "workflow" / "token_dashboard.py", script)
        result = subprocess.run(
            [sys.executable, str(script), "init", "--run", self.run, "--label", "CLI test"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write_messages([self.message()])
        hook(copied_root, self.event())
        result = subprocess.run(
            [sys.executable, str(script), "finalize", "--run", self.run,
             "--status", "blocked", "--reason", "Awaiting approval"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        target = directory(copied_root, self.run)
        self.assertTrue((target / "stlc_dashboard.html").is_file())
        data = load(target)
        self.assertEqual(data["measuredTotalTokens"], 40)
        self.assertEqual(data["status"], "blocked")
        self.assertEqual(data["recordedCalls"], 1)
        self.assertIn("Awaiting approval", (target / "stlc_dashboard.html").read_text())
        result = subprocess.run(
            [sys.executable, str(script), "hook"], input="{broken",
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("STLC dashboard error", result.stderr)

    def test_missing_transcript_is_unavailable(self):
        with contextlib.redirect_stderr(io.StringIO()):
            hook(self.root, self.event())
        row = next(row for row in load(self.target)["byAgent"] if row["agent"] == "triage-agent")
        self.assertIsNone(row["totalTokens"])
        self.assertEqual(row["telemetry"], "unavailable")

    def test_incomplete_usage_is_not_presented_as_complete(self):
        for message in (
            {"type": "assistant", "message": {"id": "missing-usage"}},
            {"type": "assistant", "message": {"usage": {"input_tokens": 1, "output_tokens": 2}}},
        ):
            with self.subTest(message=message):
                self.write_messages([self.message(), message])
                self.assertIsNone(transcript_usage(self.transcript))

    def test_zero_usage_is_measured_and_optional_caches_default_to_zero(self):
        self.write_messages([{"type": "assistant", "message": {
            "id": "zero", "usage": {"input_tokens": 0, "output_tokens": 0},
        }}])
        hook(self.root, self.event())
        self.assertEqual(load(self.target)["measuredCalls"], 1)
        row = next(row for row in load(self.target)["byAgent"] if row["agent"] == "triage-agent")
        self.assertEqual(row["totalTokens"], 0)
        self.assertEqual(row["telemetry"], "measured")

    def test_invalid_counters_and_malformed_transcripts_are_explicit_errors(self):
        for value in (-1, True, "25", 1.5):
            with self.subTest(value=value):
                self.write_messages([self.message(input_tokens=value)])
                with self.assertRaisesRegex(ValueError, "nonnegative integer"):
                    hook(self.root, self.event())
        self.transcript.write_text("{invalid json\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid transcript JSON"):
            hook(self.root, self.event())

    def test_safe_run_ids_and_agent_ids(self):
        for run in ("../escape", "..", "bad run", "x" * 101):
            with self.subTest(run=run):
                with self.assertRaisesRegex(ValueError, "Run ID"):
                    initialize(self.root, run, "label")
        unsafe = self.event()
        unsafe["tool_response"]["agentId"] = "../escape"
        with self.assertRaisesRegex(ValueError, "agentId"):
            hook(self.root, unsafe)
        with self.assertRaisesRegex(ValueError, "Unknown STLC agent"):
            hook(self.root, self.event("unrelated-agent"))

    def test_agent_id_cannot_be_relabelled(self):
        self.write_messages([self.message()])
        hook(self.root, self.event())
        with self.assertRaisesRegex(ValueError, "two STLC agents"):
            hook(self.root, self.event("execution-agent"))

    def test_resume_initialization_does_not_erase_existing_data(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            initialize(self.root, self.run, "new label")
        self.assertEqual(load(self.target)["label"], "STL-101")
        with self.assertRaisesRegex(ValueError, "not initialized"):
            finalize(self.root, "not-started", "completed", "")

    def test_blocked_failed_and_resumed_statuses_and_html_escaping(self):
        reason = '<script>alert("unsafe")</script>'
        for status in ("blocked", "failed", "running"):
            with self.subTest(status=status):
                path = finalize(self.root, self.run, status, reason)
                self.assertEqual(load(self.target)["status"], status)
                html = path.read_text(encoding="utf-8")
                self.assertNotIn(reason, html)
                self.assertIn("&lt;script&gt;", html)


if __name__ == "__main__":
    unittest.main()
