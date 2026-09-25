# 08-closure-sync

Run Stage 8 closure reporting and Jira sync preparation.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:08-closure-sync
Args: $ARGUMENTS
```

Uses:
- Agent: `reporting-closure-agent`
- Skills: `claude-stlc:execution-evidence-writer`, `claude-stlc:hitl-audit-writer`
- Artifact: `artifacts/test_closure_metrics.md`

Expected outcome:
- Produce closure metrics, evidence summaries, and Jira sync-ready status updates.