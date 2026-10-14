---
name: stlc-requirements-analysis
description: Analyze and triage requirements for Stage 1.
argument-hint: Jira issue key or pasted requirement
agent: triage-agent
---

Run Stage 1 for `${input:stlcRequirement:Enter a Jira issue key or requirement}`.
Follow the `jira-parser` skill and the Stage 1 contract in
`00-stlc-pipeline-contract.md`. Preserve traceability, inspect current test
coverage, and route to `reuse-existing-tests` or `generate-new-tests`.
Honor any configured approval before starting. Write
`stlc-pipeline/artifacts/requirement_analysis.md`. Do not proceed to another stage.
