---
name: stlc-security-gate
description: Review available Stage 5 security and compliance evidence.
argument-hint: Jira issue key or security evidence artifact
agent: security-gate-agent
---

Run Stage 5 for `${input:stlcSecurityInput:Enter a Jira issue key or artifact path}`.
Follow the `security-compliance-review` skill and pipeline contract. Use actual
scanner evidence only; do not claim a scan ran without an approved, configured
scanner. Write `stlc-pipeline/artifacts/security_compliance_report.md` and stop at its approval
gate.
