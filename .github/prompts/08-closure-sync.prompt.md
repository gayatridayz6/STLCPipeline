---
name: stlc-closure
description: Prepare Stage 8 closure metrics and sync-ready reporting.
argument-hint: Jira issue key or completed workflow artifacts
agent: reporting-closure-agent
---

Run Stage 8 for `${input:stlcClosureInput:Enter a Jira issue key or artifact path}`.
Follow the `execution-evidence-writer` and `hitl-audit-writer` skills and pipeline
contract. Require the recorded Stage 7 go decision. Write
`stlc-pipeline/artifacts/test_closure_metrics.md`; do not sync Jira without explicit approval
and an available configured integration.
