# Config Package

This package contains the STLC manifest and integration reference files.

- `project.json` is the orchestration manifest.
- `mcp/` contains integration templates/references, not proof that a Copilot MCP
  server is installed, connected, or authenticated.

Configure MCP servers through the active Copilot host's supported MCP settings.
Do not copy secrets into this repository. Custom agents must check actual tool
availability before relying on remote services.