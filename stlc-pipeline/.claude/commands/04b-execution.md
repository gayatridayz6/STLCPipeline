# 04b-execution

Run Stage 4b execution, validation, and self-healing evidence capture.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:04b-execution
Args: $ARGUMENTS
```

Uses:
- Agent: `qa-runner-agent`
- Skill: `claude-stlc:execution-evidence-writer`
- Artifact: `artifacts/test_execution_report.md`

Expected outcome:
- Record execution status, failures, retries, and self-healing notes.