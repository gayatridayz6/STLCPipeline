---
name: stlc-pr-review
description: Prepare a Stage 6 PR review from available repository evidence.
argument-hint: Pull request URL/number or review context
agent: github-mcp-agent
---

Run Stage 6 for `${input:stlcPRInput:Enter a PR reference or review context}`.
Follow the `pr-review-prep` skill and pipeline contract. Use GitHub tools only if
they are available and configured. Do not create or modify a PR without explicit
approval. Write `stlc-pipeline/artifacts/pr_review_summary.md`.
