"""Collect Claude Code subagent usage and render an offline STLC dashboard."""

import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AGENTS = {
    "delivery-orchestrator-agent": "Coordinator",
    "triage-agent": "Stage 1",
    "planning-agent": "Stage 2",
    "test-design-agent": "Stage 3",
    "engineer-agent": "Stage 4a",
    "execution-agent": "Stage 4b",
    "security-gate-agent": "Stage 5",
    "github-mcp-agent": "Stage 6",
    "hitl-gate-agent": "Stage 7",
    "reporting-closure-agent": "Stage 8",
}
COUNTERS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
MARKER = re.compile(r"\[STLC run=([A-Za-z0-9_-]{1,100}) agent=([a-z0-9-]+)\]")


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def directory(root, run):
    if not SAFE_ID.fullmatch(run):
        raise ValueError("Run ID must contain 1-100 letters, digits, underscores or hyphens")
    return root / "artifacts" / "runs" / run


def load(directory):
    path = directory / "token_usage.json"
    if not path.is_file():
        raise ValueError(f"Dashboard run not initialized: {directory}")
    return json.loads(path.read_text(encoding="utf-8"))


def count(value, field):
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def transcript_usage(path):
    """Streaming snapshots of one message ID are not separate API calls."""
    messages = {}
    incomplete = False
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid transcript JSON at line {number}: {path}") from exc
            if entry.get("type") != "assistant":
                continue
            message = entry.get("message", {})
            usage = message.get("usage")
            message_id = message.get("id")
            if not message_id or not isinstance(usage, dict):
                incomplete = True
                continue
            if not all(field in usage for field in COUNTERS[:2]):
                incomplete = True
                continue
            counters = {field: count(usage.get(field, 0), field) for field in COUNTERS}
            previous = messages.setdefault(message_id, dict.fromkeys(COUNTERS, 0))
            for field in COUNTERS:
                previous[field] = max(previous[field], counters[field])
    if incomplete or not messages:
        return None
    return {field: sum(usage[field] for usage in messages.values()) for field in COUNTERS}


def collect(event):
    response = event.get("tool_response") or {}
    agent_id = response.get("agentId") if isinstance(response, dict) else None
    if not agent_id:
        return None, None, "Runtime did not expose a subagent transcript ID"
    if not SAFE_ID.fullmatch(agent_id):
        raise ValueError("Invalid runtime agentId")
    parent = Path(event["transcript_path"])
    subagents = parent.parent if parent.parent.name == "subagents" else (
        parent.parent / parent.stem / "subagents"
    )
    path = subagents / f"agent-{agent_id}.jsonl"
    if not path.is_file():
        return agent_id, None, "Subagent transcript unavailable (or agent still running)"
    usage = transcript_usage(path)
    return agent_id, usage, None if usage is not None else "Transcript has incomplete or missing usage counters"


def aggregate(data):
    rows = []
    for agent, stage in AGENTS.items():
        calls = [item for item in data["invocations"].values() if item["agent"] == agent]
        measured = [item["usage"] for item in calls if item["usage"] is not None]
        counters = {
            field: sum(usage[field] for usage in measured) if measured else None
            for field in COUNTERS
        }
        total = sum(counters.values()) if measured else None
        rows.append({
            "agent": agent, "stage": stage, "calls": len(calls),
            "measuredCalls": len(measured), **counters, "totalTokens": total,
            "telemetry": "not recorded" if not calls else (
                "measured" if len(calls) == len(measured) else (
                    "partial" if measured else "unavailable"
                )
            ),
        })
    data["byAgent"] = rows
    data["measuredTotalTokens"] = sum(row["totalTokens"] or 0 for row in rows)
    data["measuredCalls"] = sum(row["measuredCalls"] for row in rows)
    data["recordedCalls"] = sum(row["calls"] for row in rows)


def render(data):
    maximum = max((row["totalTokens"] or 0 for row in data["byAgent"]), default=0)

    def number(value):
        return f"{value:,}" if value is not None else "N/A"

    rows = []
    for row in data["byAgent"]:
        width = 100 * (row["totalTokens"] or 0) / maximum if maximum else 0
        cells = "".join(f"<td>{number(row[field])}</td>" for field in COUNTERS)
        rows.append(
            f'<tr><th scope="row">{escape(row["agent"])}<small>{escape(row["stage"])}</small></th>'
            f'<td>{row["calls"]}</td>{cells}<td><strong>{number(row["totalTokens"])}</strong>'
            f'<div class="bar" style="width:{width:.2f}%"></div></td>'
            f'<td>{escape(row["telemetry"])}</td></tr>'
        )
    warnings = "".join(
        f'<li>{escape(item["agent"])}: {escape(item["warning"])}</li>'
        for item in data["invocations"].values() if item.get("warning")
    )
    total = number(data["measuredTotalTokens"]) if data["measuredCalls"] else "N/A"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STLC Token Dashboard - {escape(data["label"])}</title>
<style>
:root {{color-scheme:light; font-family:system-ui,sans-serif; color:#172b4d; background:#f3f6fb}}
body {{margin:0; padding:32px}} main {{max-width:1300px; margin:auto}}
h1 {{margin-bottom:8px}} p,small {{color:#52657e}} small {{display:block; font-weight:normal}}
.cards {{display:flex; flex-wrap:wrap; gap:16px; margin:24px 0}}
.card {{flex:1; min-width:180px; padding:20px; background:white; border-radius:12px; border:1px solid #dce4ef}}
.metric {{font-size:28px; font-weight:700; margin-top:8px; overflow-wrap:anywhere}}
.table {{overflow-x:auto; background:white; border-radius:12px; border:1px solid #dce4ef}}
table {{width:100%; border-collapse:collapse}} th,td {{padding:14px; border-bottom:1px solid #edf1f7; text-align:left}}
thead {{background:#e8eef8}} .bar {{height:5px; background:#167d8d; margin-top:6px; border-radius:4px}}
.note {{padding:16px; background:#e8eef8; border-radius:12px; margin-top:20px}}
@media(max-width:600px) {{body {{padding:16px}} th,td {{padding:10px}}}}
</style></head><body><main>
<h1>STLC Token Dashboard</h1>
<p>{escape(data["label"])} | Run: {escape(data["run"])} | Updated: {escape(data["updatedAt"])}</p>
<section class="cards" aria-label="Run summary">
<div class="card">Workflow status<div class="metric">{escape(data["status"])}</div></div>
<div class="card">Measured total tokens<div class="metric">{total}</div></div>
<div class="card">Calls with telemetry<div class="metric">{data["measuredCalls"]} / {data["recordedCalls"]}</div></div>
<div class="card">Agents with telemetry<div class="metric">{sum(row["measuredCalls"] > 0 for row in data["byAgent"])} / {len(AGENTS)}</div></div>
</section><div class="table"><table>
<caption>Per-agent token consumption (measured calls only)</caption>
<thead><tr><th scope="col">Agent / stage</th><th scope="col">Calls</th><th scope="col">Input</th>
<th scope="col">Output</th><th scope="col">Cache write</th><th scope="col">Cache read</th>
<th scope="col">Total tokens</th><th scope="col">Telemetry</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<div class="note"><strong>Measurement scope</strong>
<p>Total = uncached input + output + cache-write input + cache-read input.
Counters come from local Claude Code subagent transcripts, not text estimates.
Partial totals exclude calls without counters. N/A is not zero.
Not recorded does not mean skipped: a stage may have run inline or outside the instrumented calls.
The parent coordinator's usage is unavailable unless it is itself a tagged subagent;
whole-session usage is not added because it may include unrelated work.
No transcript content or credentials are embedded in this report.</p>
<p>{escape(data.get("reason", ""))}</p>
{"<ul>" + warnings + "</ul>" if warnings else ""}</div>
</main></body></html>
"""


def save(directory, data):
    data["updatedAt"] = timestamp()
    aggregate(data)
    for name, text in (
        ("token_usage.json", json.dumps(data, indent=2) + "\n"),
        ("stlc_dashboard.html", render(data)),
    ):
        path = directory / name
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)


def initialize(root, run, label):
    target = directory(root, run)
    if (target / "token_usage.json").exists():
        raise ValueError("Dashboard already exists; use the same run ID to resume, or choose a new ID")
    target.mkdir(parents=True, exist_ok=True)
    save(target, {
        "run": run, "label": label, "status": "running", "startedAt": timestamp(),
        "invocations": {},
    })
    return target / "stlc_dashboard.html"


def hook(root, event):
    if event.get("tool_name") not in ("Agent", "Task"):
        return
    prompt = event.get("tool_input", {}).get("prompt", "")
    match = MARKER.match(prompt)
    if not match:
        return
    run, agent = match.groups()
    if agent not in AGENTS:
        raise ValueError(f"Unknown STLC agent: {agent}")
    target = directory(root, run)
    data = load(target)
    agent_id, usage, warning = collect(event)
    session = event["session_id"]
    # A resumed subagent transcript is cumulative; replace its earlier snapshot.
    key = f"{session}:{agent_id or event['tool_use_id']}"
    previous = data["invocations"].get(key)
    if previous and previous["agent"] != agent:
        raise ValueError("Runtime agent ID was mapped to two STLC agents")
    data["invocations"][key] = {"agent": agent, "usage": usage, "warning": warning}
    save(target, data)
    if warning:
        print(f"STLC token telemetry unavailable for {agent}: {warning}", file=sys.stderr)


def finalize(root, run, status, reason):
    target = directory(root, run)
    data = load(target)
    data["status"] = status
    data["reason"] = reason
    save(target, data)
    return target / "stlc_dashboard.html"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("init")
    begin.add_argument("--run", required=True)
    begin.add_argument("--label", required=True)
    commands.add_parser("hook")
    finish = commands.add_parser("finalize")
    finish.add_argument("--run", required=True)
    finish.add_argument("--status", choices=("running", "completed", "blocked", "failed"), required=True)
    finish.add_argument("--reason", default="")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            print(initialize(ROOT, args.run, args.label))
        elif args.command == "hook":
            hook(ROOT, json.load(sys.stdin))
        else:
            print(finalize(ROOT, args.run, args.status, args.reason))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"STLC dashboard error: {exc}\n")


if __name__ == "__main__":
    main()
