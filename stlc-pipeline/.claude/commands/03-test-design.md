# 03-test-design

Run Stage 3 test design and BDD generation.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:03-test-design
Args: $ARGUMENTS
```

Uses:
- Agent: `qa-sentinel-agent`
- Skill: `claude-stlc:bdd-generator`
- Artifact: `artifacts/test_design.md`

Expected outcome:
- Produce BDD-ready scenarios and test design outputs aligned to approved planning.