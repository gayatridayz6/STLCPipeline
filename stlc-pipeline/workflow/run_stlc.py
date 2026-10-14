"""Local, approval-gated STLC workflow recorder.

Stage content is authored by an operator/agent; this runner validates handoffs
and records them. It does not claim to invoke an AI agent or remote integration.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "stage-01", "stage-02", "stage-03", "stage-04a", "stage-04b",
    "stage-05", "stage-06", "stage-07", "stage-08",
)
ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class WorkflowError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_dir(root, ticket):
    if not ISSUE_KEY.fullmatch(ticket):
        raise WorkflowError("Ticket must be a Jira-style issue key, e.g. EPMCDMETST-66524")
    return root / "artifacts" / "runs" / ticket


def load_state(directory):
    path = directory / "state.json"
    if not path.is_file():
        raise WorkflowError(f"No workflow state at {path}; run 'start' first")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(directory, state):
    path = directory / "state.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def audit(directory, event, stage, actor=None, reason=None):
    entry = {"at": now(), "event": event, "stage": stage}
    if actor:
        entry["by"] = actor
    if reason:
        entry["reason"] = reason
    with (directory / "audit.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry) + "\n")


def preflight(root, input_file):
    config_path = root / ".claude" / "config" / "project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    for hook in ("pre_stage_validation", "artifact_contract_guard", "approval_gate_guard",
                 "java_validation_guard"):
        script = root / ".claude" / "hooks" / (hook + ".py")
        result = subprocess.run(
            [sys.executable, str(script)], cwd=root, capture_output=True, text=True
        )
        if result.returncode:
            raise WorkflowError(f"{hook} failed: {result.stderr.strip() or result.stdout.strip()}")
    if not input_file.is_file() or not input_file.read_text(encoding="utf-8").strip():
        raise WorkflowError("Provide a nonempty local requirements file for offline triage")
    return config


def start(root, ticket, input_file):
    config = preflight(root, input_file)
    directory = run_dir(root, ticket)
    if (directory / "state.json").exists():
        raise WorkflowError(f"Run already exists: {directory}; use 'status' to resume")
    directory.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(input_file, directory / "requirements.txt")
    state = {
        "ticket": ticket,
        "current": "stage-01",
        "completed": [],
        "approvals": {},
        "route": None,
        "mode": "offline",
        "blocker": None,
        "execution_waiver": None,
    }
    save_state(directory, state)
    audit(directory, "started", "stage-01")
    print(f"Started {ticket} (offline input). Current: stage-01; approval required.")
    print("Live integrations:", "enabled" if config["liveIntegrationsEnabled"] else "disabled")


def approve(root, ticket, stage, actor):
    directory = run_dir(root, ticket)
    state = load_state(directory)
    if stage != state["current"] or stage == "complete":
        raise WorkflowError(f"Cannot approve {stage}; current stage: {state['current']}")
    if state.get("blocker"):
        raise WorkflowError(f"Resolve the current blocker before approving {stage}: {state['blocker']}")
    if stage in state["approvals"]:
        raise WorkflowError(f"{stage} is already approved")
    if not actor.strip():
        raise WorkflowError("An explicit human approver name is required")
    state["approvals"][stage] = {"by": actor.strip(), "at": now()}
    save_state(directory, state)
    audit(directory, "approved", stage, actor.strip())
    print(f"Approved {stage} for {ticket} by {actor.strip()}")


def artifact_key(stage):
    if stage in ("stage-04a", "stage-04b"):
        return "stage-04"
    return stage


def next_stage(stage, route):
    if stage == "stage-01" and route == "reuse-existing-tests":
        return "stage-04b"
    if stage == "stage-04b" and route == "reuse-existing-tests":
        return "complete"
    return STAGES[STAGES.index(stage) + 1] if stage != STAGES[-1] else "complete"


def complete(root, ticket, stage, source, route):
    directory = run_dir(root, ticket)
    state = load_state(directory)
    if stage != state["current"] or stage == "complete":
        raise WorkflowError(f"Cannot complete {stage}; current stage: {state['current']}")
    if state.get("blocker"):
        raise WorkflowError(f"Cannot complete blocked stage {stage}: {state['blocker']}")
    if stage not in state["approvals"]:
        raise WorkflowError(f"Human approval required before {stage}")
    config = json.loads((root / ".claude" / "config" / "project.json").read_text(encoding="utf-8"))
    if stage == "stage-01":
        routes = config["stages"][0]["routingDecisions"]
        if route not in routes:
            raise WorkflowError(f"Stage 1 requires --route: {', '.join(routes)}")
    elif route:
        raise WorkflowError("--route is valid only for stage-01")
    if not source.is_file():
        raise WorkflowError(f"Stage artifact does not exist: {source}")
    content = source.read_text(encoding="utf-8")
    if not content.strip() or re.search(r"<[a-z][a-z0-9-]*>|Phase \d+ placeholder\.", content):
        raise WorkflowError("Stage artifact is empty or contains placeholder content")
    if stage == "stage-01" and route not in content:
        raise WorkflowError("Stage 1 artifact must explicitly state its routing recommendation")
    if stage == "stage-04b" and state.get("execution_waiver"):
        if "REAL_APP_NOT_EXECUTED" not in content or "review-only" not in content.lower():
            raise WorkflowError("Waived Stage 4b evidence must state REAL_APP_NOT_EXECUTED and review-only")
    destination = directory / (stage + ".md")
    if source.resolve() != destination.resolve():
        shutil.copyfile(source, destination)
    mapped = root / config["artifacts"][artifact_key(stage)]
    shutil.copyfile(destination, mapped)
    if stage == "stage-01":
        state["route"] = route
    state["completed"].append({"stage": stage, "artifact": str(destination.relative_to(root)), "at": now()})
    state["current"] = next_stage(stage, state["route"])
    save_state(directory, state)
    audit(directory, "completed", stage)
    print(f"Completed {stage}. Next: {state['current']}")
    if state["current"] != "complete" and state["current"] != "stage-07":
        print(f"Human approval required before {state['current']}.")


def change_blocker(root, ticket, reason, unblock):
    directory = run_dir(root, ticket)
    state = load_state(directory)
    if state["current"] == "complete":
        raise WorkflowError("The workflow is already complete")
    if not reason.strip():
        raise WorkflowError("A nonempty reason is required")
    if unblock:
        if not state.get("blocker"):
            raise WorkflowError("There is no blocker to resolve")
        state["blocker"] = None
        event = "unblocked"
    else:
        state["blocker"] = reason.strip()
        state["approvals"].pop(state["current"], None)
        event = "blocked"
    save_state(directory, state)
    audit(directory, event, state["current"], reason=reason.strip())
    print(f"{event.capitalize()} {state['current']}: {reason.strip()}")


def waive_execution(root, ticket, actor, reason):
    directory = run_dir(root, ticket)
    state = load_state(directory)
    if state["current"] != "stage-04b":
        raise WorkflowError("Only Stage 4b real-app execution can be waived")
    if state.get("execution_waiver"):
        raise WorkflowError("Real-app execution has already been waived")
    if not state.get("blocker"):
        raise WorkflowError("Stage 4b must have a recorded execution blocker before waiver")
    if not actor.strip() or not reason.strip():
        raise WorkflowError("An explicit human approver and nonempty reason are required")
    state["execution_waiver"] = {"by": actor.strip(), "at": now(), "reason": reason.strip()}
    state["blocker"] = None
    state["mode"] = "review-only"
    save_state(directory, state)
    audit(directory, "real-app-execution-waived", "stage-04b", actor.strip(), reason.strip())
    print("Real-app execution waived for Stage 4b; review-only handoffs are permitted.")
    print("New Stage 4b approval is required before completing the evidence artifact.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("start", help="Preflight and start an offline issue run")
    begin.add_argument("--ticket", required=True)
    begin.add_argument("--input-file", type=Path, required=True)
    for command in ("status", "approve", "complete", "block", "unblock", "waive-execution"):
        sub = commands.add_parser(command)
        sub.add_argument("--ticket", required=True)
        if command in ("approve", "complete"):
            sub.add_argument("--stage", choices=STAGES, required=True)
        if command == "approve":
            sub.add_argument("--by", required=True, help="Human approver name")
        if command == "complete":
            sub.add_argument("--source", type=Path, required=True, help="Reviewed stage Markdown")
            sub.add_argument("--route", choices=("reuse-existing-tests", "generate-new-tests"))
        if command in ("block", "unblock"):
            sub.add_argument("--reason", required=True)
        if command == "waive-execution":
            sub.add_argument("--by", required=True, help="Human authorizing review-only continuation")
            sub.add_argument("--reason", required=True, help="Reason actual application testing is waived")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "start":
            start(root, args.ticket, args.input_file.resolve())
        elif args.command == "status":
            state = load_state(run_dir(root, args.ticket))
            print(json.dumps(state, indent=2))
        elif args.command == "approve":
            approve(root, args.ticket, args.stage, args.by)
        elif args.command in ("block", "unblock"):
            change_blocker(root, args.ticket, args.reason, args.command == "unblock")
        elif args.command == "waive-execution":
            waive_execution(root, args.ticket, args.by, args.reason)
        else:
            complete(root, args.ticket, args.stage, args.source.resolve(), args.route)
    except (WorkflowError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Workflow blocked: {exc}\n")


if __name__ == "__main__":
    main()
