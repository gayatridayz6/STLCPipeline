---
name: stlc-test-design
description: Generate Stage 3 BDD test design from approved planning.
argument-hint: Jira issue key or test-planning artifact
agent: qa-sentinel-agent
---

Run Stage 3 for `${input:stlcDesignInput:Enter a Jira issue key or artifact path}`.
Follow the `bdd-generator` skill and pipeline contract. Require approved Stage 2
input, write `stlc-pipeline/artifacts/test_design.md`, and stop for required human review.
Do not advance the workflow.
