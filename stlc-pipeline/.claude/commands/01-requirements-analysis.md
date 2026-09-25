# 01-requirements-analysis

Run Stage 1 requirements analysis and triage.

Arguments: `$ARGUMENTS`

Invoke through the orchestrator or directly as a stage command.

```text
Skill: claude-stlc:01-requirements-analysis
Args: $ARGUMENTS
```

Uses:
- Agent: `triage-agent`
- Skill: `claude-stlc:jira-parser`
- Artifact: `artifacts/requirement_analysis.md`

Expected outcome:
- Normalize Jira or pasted requirement input.
- Map existing automation coverage.
- Detect whether this Jira story already has generated tests linked to it.
- If linked tests already exist, recommend execution-summary-only routing.
- If linked tests do not exist, identify gaps and recommend Stage 2 scope.