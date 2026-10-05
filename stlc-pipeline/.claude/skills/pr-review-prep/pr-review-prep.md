---
name: pr-review-prep
description: Prepare PR summary content, review checkpoints, and merge-readiness notes for Stage 6.
---

# PR Review Prep Skill

Purpose:
- Prepare code review and pull request context without assuming live repository mutation.

Inputs:
- approved change summary
- execution evidence
- security findings
- outstanding risks

Process:
1. Summarize change intent and test evidence.
2. Highlight files or areas reviewers must inspect.
3. Carry forward any blocking security or quality concerns.
4. Prepare reviewer prompts and merge prerequisites.

Output:
- PR summary draft
- reviewer checklist
- merge readiness notes