---
name: security-compliance-review
description: Summarize security scanner outputs and compliance exceptions for Stage 5 decisions.
---

# Security Compliance Review Skill

Purpose:
- Normalize SAST, SCA, and compliance findings into a decision-ready summary.

Inputs:
- static analysis findings
- dependency findings
- policy exceptions
- severity thresholds

Process:
1. Group findings by severity and exploitability.
2. Distinguish blocking issues from accepted risks.
3. Note missing scans or missing evidence.
4. Prepare human review questions when policy interpretation is needed.

Output:
- consolidated finding summary
- blocker list
- approved exception list
- remediation recommendations