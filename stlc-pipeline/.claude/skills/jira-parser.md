---
name: jira-parser
description: Normalize Jira story and bug payloads into structured requirement fields for Stage 1 triage.
---

# Jira Parser Skill

Purpose:
- Normalize Jira story and bug payloads into structured requirement fields.
- Break acceptance criteria into testable statements.

Inputs:
- issue key
- summary
- description
- acceptance criteria
- labels
- severity
- priority
- component

Process:
1. Extract explicit requirement statements.
2. Separate functional criteria from metadata.
3. Detect whether the Jira issue key or story traceability already maps to generated test assets.
4. Flag missing Jira fields as placeholders instead of inventing values.
5. Return a clean requirement object for Stage 1 analysis.

Output:
- normalized requirement object for Stage 1 analysis
- extracted acceptance criteria list
- existing test coverage status for the Jira story
- routing recommendation: `reuse-existing-tests` or `generate-new-tests`
- unresolved questions for human review
