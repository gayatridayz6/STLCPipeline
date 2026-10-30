# STLC workflow contract

This is reference documentation for Copilot prompt files and agents. It is not
an invokable prompt and does not call a `Skill` tool.

## Entry points and execution limits

- Full run: `.github/prompts/stlc.prompt.md` (or `00-stlc-pipeline.prompt.md`).
- Stage-specific prompt files live in `.github/prompts/*.prompt.md`.
- Each prompt selects the corresponding custom agent in `.github/agents/*.agent.md`.
- VS Code Agent Host does not load prompt files; invoke the custom agent directly
  in Agent Host sessions. Prompt-file slash commands are for the VS Code Local
  agent.
- Reusable guidance is in `.github/skills/<name>/SKILL.md`.
- The orchestration manifest and stage graph are
  `.github/config/project.json` and `stlc-pipeline/workflow/STLCWorkflowOrchestrator.java`.
- MCP templates under `.github/config/mcp/` are references only. Copilot can use
  a service only when its MCP tools are actually configured and enabled in the
  active session.
- Python guard scripts under `.github/hooks/` are not Copilot lifecycle hooks;
  invoke them explicitly when the workflow requires them. Stop on failure.
- `stlc-pipeline/workflow/token_dashboard.py` reads Claude Code transcripts only. It is not a
  Copilot telemetry collector.
- Before starting or advancing a stage, honor
  `requiresHumanApprovalBeforeStart` and all approval gates in the manifest.

## Stage flow

0. **MCP preflight** — check availability of only the services required by the
   selected stages. Missing required integrations block those stages.
1. **Requirements analysis** — `triage-agent`; write
   `stlc-pipeline/artifacts/requirement_analysis.md`. Require any configured approval before
   starting. Return exactly one route:
   `reuse-existing-tests` or `generate-new-tests`.
2. **Test planning** — `planning-agent`; write
   `stlc-pipeline/artifacts/test_planning.md`; require human approval before continuing.
3. **Test design** — `test-design-agent`; write `stlc-pipeline/artifacts/test_design.md`;
   require human approval before continuing.
4a. **Engineering** — `engineer-agent`; require approved design and write
    `stlc-pipeline/artifacts/engineering_summary.md`.
4b. **Execution** — `execution-agent`; require explicit execution approval and
    verified target; write `stlc-pipeline/artifacts/test_execution_report.md`. Mark simulations
    and review-only work accurately; do not claim application tests passed.
5. **Security and compliance** — `security-gate-agent`; use actual approved
   evidence only; write `stlc-pipeline/artifacts/security_compliance_report.md`.
6. **PR review** — `github-mcp-agent`; prepare
   `stlc-pipeline/artifacts/pr_review_summary.md`. Do not create or modify a PR without
   explicit approval and an available GitHub integration.
7. **Human decision** — `hitl-gate-agent`; record the human's explicit decision
   in `stlc-pipeline/artifacts/hitl_audit_trail.md`. Never infer or record approval for them.
8. **Closure** — `reporting-closure-agent`; require a recorded go decision and
   write `stlc-pipeline/artifacts/test_closure_metrics.md`. Jira sync requires explicit
   approval and an available integration.

## Routing and stop conditions

- If Stage 1 finds linked generated tests, skip Stages 2, 3, and 4a. Run Stage
  4b in execution-summary-only mode, then stop after its report.
- Otherwise, continue through stages 2–8 in order. Never run 4a and 4b in
  parallel.
- Stop on missing approval, missing required input or integration, failed
  validation, or blocker security/quality findings. Record the blocker; do not
  claim the blocked stage completed.
- Never fabricate remote results, test execution, security scans, approvals,
  identities, or token measurements. Keep secrets as references.

## Legacy Claude telemetry

The optional dashboard scripts and `.github/settings.json` configuration from
the previous Claude Code setup are not part of this Copilot workflow. Copilot
must not run the transcript collector or present its output as Copilot usage.
