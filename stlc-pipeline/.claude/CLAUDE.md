# EPAM STLC Claude Project

This repository uses Claude assets rooted in `.claude/`.

## Structure

- Global config: `.claude/config/project.json`
- Agent prompts: `.claude/agents/`
- Hooks: `.claude/hooks/`
- Skills: `.claude/skills/`
- MCP bindings: `.claude/config/mcp/`
- Phase artifacts: `artifacts/`

## Operating Rules

- Read `.claude/config/project.json` before stage-specific work.
- Treat human approval as mandatory before advancing a stage from design to execution.
- Keep live integrations disabled until the user provides real Jira, GitHub, and security configuration.
- Use placeholders instead of inventing external IDs, URLs, secrets, or environment-specific values.

## Current Boundary

- Stage 1 is initialized for reviewable requirement analysis output.
- Stages 2 through 8 remain scaffolds pending explicit approval.
- No legacy package layout should be used going forward.
