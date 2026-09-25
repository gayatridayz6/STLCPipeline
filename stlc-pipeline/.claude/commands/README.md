# Command Package

This package defines the command entry points for the enterprise STLC pipeline.

Rules:
- Commands are the public entry points for pipeline execution.
- Commands should invoke skills by name through the Skill tool.
- Commands should not read skill files directly.
- Commands should route into the orchestrator or the appropriate stage subagent.