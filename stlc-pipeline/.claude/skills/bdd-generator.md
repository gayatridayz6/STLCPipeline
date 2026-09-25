---
name: bdd-generator
description: Convert approved acceptance criteria and planning decisions into BDD-ready scenarios for Stage 3.
---

# BDD Generator Skill

Purpose:
- Convert approved acceptance criteria into BDD-ready scenarios for Stage 3.
- Preserve traceability from requirement to scenario to execution evidence.

Inputs:
- approved acceptance criteria
- Stage 2 planning notes
- risk and priority guidance

Process:
1. Create scenario titles aligned to business outcomes.
2. Split happy path, negative path, and boundary coverage.
3. Keep steps reusable and implementation-agnostic.
4. Mark assumptions and open questions for human review.

Output:
- feature-level scenario inventory
- Given/When/Then drafts
- traceability notes for Stage 4 execution
