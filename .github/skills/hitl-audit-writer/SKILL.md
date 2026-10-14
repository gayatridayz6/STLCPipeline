---
name: hitl-audit-writer
description: Record human approvals, blockers, and decisions in a traceable Stage 7 audit format.
---

# HITL Audit Writer Skill

Purpose:
- Capture approval decisions and reasons with traceability.

Inputs:
- stage identifier
- requested action
- decision status
- approver name
- timestamp
- rationale and notes

Process:
1. Record the exact gate being requested.
2. Distinguish design approval from execution approval.
3. Preserve rejection or deferment reasons.
4. Produce a clear downstream go or no-go status.

Output:
- audit entry
- approval matrix update
- pending action list