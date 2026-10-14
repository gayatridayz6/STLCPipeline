# EPAM STLC GitHub Copilot project

Project customizations are under `.github/`: prompt files in `prompts/`, custom
agents in `agents/`, Agent Skills in `skills/`, validation scripts in `hooks/`,
and the workflow manifest and integration references in `config/`.

Before stage work, read `.github/config/project.json` and
`stlc-pipeline/workflow/STLCWorkflowOrchestrator.java`. Follow the configured
stage order, artifact contracts, reuse-existing-tests route, and human approval
gates.

Treat external integrations as unavailable unless their tools are present and
configured in the current Copilot session. Do not invent Jira/GitHub data,
execution evidence, scan results, approvals, identities, or secrets. Stop and
report blockers explicitly.

The optional token dashboard reads Claude Code transcripts and is not Copilot
telemetry. Do not run it from Copilot or report its values as Copilot usage.
