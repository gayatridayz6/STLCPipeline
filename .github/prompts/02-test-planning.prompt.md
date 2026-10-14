---
name: stlc-test-planning
description: Create the approved-input risk-based Stage 2 test plan.
argument-hint: Jira issue key or requirement-analysis artifact
agent: qa-strategist-agent
---

Run Stage 2 for `${input:stlcPlanningInput:Enter a Jira issue key or artifact path}`.
Follow the `test-planning-strategist` skill and pipeline contract. Require
approved Stage 1 input, write `stlc-pipeline/artifacts/test_planning.md`, and stop for required
human review. Do not advance the workflow.
