---
name: stlc-hitl-gate
description: Record a human's explicit Stage 7 go/no-go decision.
argument-hint: Jira issue key and reviewed stage artifacts
agent: hitl-gate-agent
---

Run Stage 7 for `${input:stlcApprovalInput:Enter a Jira issue key or artifact path}`.
Follow the `hitl-audit-writer` skill and pipeline contract. Ask the human for an
explicit decision if none is present; never infer or record approval on their
behalf. Write `stlc-pipeline/artifacts/hitl_audit_trail.md`.
