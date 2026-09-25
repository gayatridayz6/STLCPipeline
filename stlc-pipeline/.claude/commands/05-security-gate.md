# 05-security-gate

Run Stage 5 security and compliance review.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:05-security-gate
Args: $ARGUMENTS
```

Uses:
- Agent: `security-gate-agent`
- Skill: `claude-stlc:security-compliance-review`
- Artifact: `artifacts/security_compliance_report.md`

Expected outcome:
- Summarize SAST, SCA, and compliance evidence for the approval decision.