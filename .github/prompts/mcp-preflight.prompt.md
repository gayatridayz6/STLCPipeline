---
name: stlc-mcp-preflight
description: Check configured MCP availability before stages that require remote services.
argument-hint: Stage or integration set to check
---

Read `../config/project.json` and its MCP configuration references. Determine
which services the requested stages require. Check only MCP tools that are
actually available in this Copilot session; report each as connected,
unavailable, or not required. Do not infer authentication or connectivity from
configuration text, expose secrets, or run remote mutations. Stop if a required
integration is unavailable.
