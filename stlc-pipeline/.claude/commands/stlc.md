# stlc

Run the full enterprise STLC multi-agent pipeline from requirement intake through closure reporting.

Arguments: `$ARGUMENTS`

To run the pipeline, invoke the skill using the Skill tool:

```text
Skill: claude-stlc:00-stlc-pipeline
Args: $ARGUMENTS
```

Examples:
- `/claude-stlc --ticket={{JIRA_PREFIX}}-1234`
- `/claude-stlc --ticket={{JIRA_PREFIX}}-1234 --resume`
- `/claude-stlc --ticket={{JIRA_PREFIX}}-1234 --from=stage-03`
- `/claude-stlc --text="As a user I want..."`

Execution model:
1. Run `mcp-preflight`.
2. Load `stlc-orchestrator-agent`.
3. Run Stage 1 triage and determine whether the story already has linked generated tests.
4. If linked generated tests already exist, skip Stage 2, Stage 3, and Stage 4a and run Stage 4b execution-summary-only mode.
5. If linked generated tests do not exist, execute the normal phase flow in order with HITL gates enforced.
6. Update artifacts after each completed phase.
7. Stop on blocker conditions or missing approval.