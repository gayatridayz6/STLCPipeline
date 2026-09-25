# 07-hitl-gate

Run Stage 7 human-in-the-loop audit and approval recording.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:07-hitl-gate
Args: $ARGUMENTS
```

Uses:
- Agent: `hitl-gate-agent`
- Skill: `claude-stlc:hitl-audit-writer`
- Artifact: `artifacts/hitl_audit_trail.md`

Expected outcome:
- Record go or no-go approval decisions and downstream gate status.