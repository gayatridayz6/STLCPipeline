# Config Package

This package contains the active project configuration for the STLC system.

- `project.json` is the main orchestration manifest.
- `mcp/jira_mcp_config.json` is the Jira MCP placeholder.
- `mcp/github_mcp_config.json` is the GitHub MCP placeholder.

All hooks, commands, and agents should read config from this package.