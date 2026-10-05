---
name: execution-evidence-writer
description: Standardize execution findings, failures, retries, and self-healing notes into Stage 4 and Stage 8 artifacts.
---

# Execution Evidence Writer Skill

Purpose:
- Convert run results into structured evidence for reporting and audit.

Inputs:
- test run outcomes
- failures and retries
- self-healing notes
- environment details

Process:
1. Capture what ran and under which assumptions.
2. Separate pass, fail, blocked, and flaky results.
3. Record any self-healing or retry action taken.
4. Summarize residual risks for human review.

Output:
- execution summary
- issue list
- healing and retry notes
- closure-ready evidence