---
name: stlc
description: Run or resume the enterprise STLC pipeline.
argument-hint: Jira key, requirement text, or supported resume/stage options
agent: stlc-orchestrator-agent
---

Run the STLC workflow for `${input:stlcRequest:Enter a Jira key or requirement text}`.
Use [the pipeline contract](./00-stlc-pipeline-contract.md) as source of truth.
Follow the configured stage graph, reuse-existing-tests route, approvals, and
artifact contracts. If an integration or tool needed for a step is unavailable,
report a blocker and stop; never invent execution results or approval.
