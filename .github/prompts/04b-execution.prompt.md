---
name: stlc-execution
description: Execute approved tests and record Stage 4b evidence.
argument-hint: Jira issue key or approved execution input
agent: execution-agent
---

Run Stage 4b for `${input:stlcExecutionInput:Enter a Jira issue key or artifact path}`.
Follow the `execution-evidence-writer` skill and pipeline contract. Require
explicit execution approval and a verified target before running tests. Record
actual results in `stlc-pipeline/artifacts/test_execution_report.md`; label simulations and
review-only results accurately. Do not proceed to another stage.
