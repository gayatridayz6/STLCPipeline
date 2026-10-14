---
name: stlc-engineering
description: Prepare Stage 4a automation implementation after approval.
argument-hint: Jira issue key or approved test-design artifact
agent: engineer-agent
---

Run Stage 4a for `${input:stlcEngineeringInput:Enter a Jira issue key or artifact path}`.
Follow the `execution-evidence-writer` skill and pipeline contract. Require
approved test design, make only authorized code changes, record
`stlc-pipeline/artifacts/engineering_summary.md`, and do not start execution.
