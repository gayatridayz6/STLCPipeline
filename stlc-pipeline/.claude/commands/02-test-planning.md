# 02-test-planning

Run Stage 2 test planning and strategy generation.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:02-test-planning
Args: $ARGUMENTS
```

Uses:
- Agent: `qa-strategist-agent`
- Skill: `claude-stlc:test-planning-strategist`
- Artifact: `artifacts/test_planning.md`

Expected outcome:
- Build a risk-based plan.
- Define scope, environments, dependencies, and exit criteria.