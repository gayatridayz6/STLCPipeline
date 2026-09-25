# 06-pr-review

Run Stage 6 PR preparation and automated review packaging.

Arguments: `$ARGUMENTS`

```text
Skill: claude-stlc:06-pr-review
Args: $ARGUMENTS
```

Uses:
- Agent: `github-mcp-agent`
- Skill: `claude-stlc:pr-review-prep`
- Artifact: `artifacts/pr_review_summary.md`

Expected outcome:
- Prepare PR summary, reviewer checklist, and merge-readiness notes.