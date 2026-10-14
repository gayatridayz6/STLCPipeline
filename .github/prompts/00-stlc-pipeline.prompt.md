---
name: stlc-pipeline
description: Run the existing STLC pipeline from requirements through closure.
argument-hint: Jira key, requirement text, or supported resume/stage options
agent: stlc-orchestrator-agent
---

Run the existing STLC pipeline for: `${input:stlcRequest:Enter a Jira key or requirement text}`

Follow [the pipeline contract](./00-stlc-pipeline-contract.md), the project
manifest at `.github/config/project.json`, and `stlc-pipeline/workflow/STLCWorkflowOrchestrator.java`.
Preserve stage order, reuse-existing-tests routing, artifact names, approvals, and
external-mutation safeguards.

If the required custom-agent, subagent, MCP, or runtime capability is unavailable,
stop at that point and report the blocker. Do not treat a textual `Skill:` block
as a tool invocation, substitute a different workflow, or claim unavailable work
was completed.

The optional token dashboard reads Claude Code transcripts only. Do not run it
from Copilot or report its values as Copilot telemetry.
