# mcp-preflight

Verify that every remote MCP server required by the STLC pipeline is connected and authenticated before execution begins.

Arguments: `$ARGUMENTS`

Important:
- Do not attempt to read or locate skill files directly.
- Use the Skill tool to invoke reusable capabilities by skill name.

To run the preflight check, invoke the skill using the Skill tool:

```text
Skill: claude-stlc:mcp-preflight
Args: $ARGUMENTS
```

Expected behavior:
- Read `.claude/config/project.json` and the MCP bindings under `.claude/config/mcp/`.
- Derive the required MCP set for the requested run.
- Verify Jira and GitHub MCP connectivity and authentication in parallel.
- Print a status table.
- Halt with reconnect guidance if a required MCP is not connected.
- Warn, but do not block, on optional MCPs.

Use this as Phase 0 before the full pipeline or before manually invoking any phase that depends on remote MCP services.