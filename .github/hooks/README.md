# Validation scripts

These Python scripts are explicit workflow guards, not Copilot lifecycle hooks.
The orchestrator runs them with Python at the stages specified by the manifest
and stops if a guard fails.

Do not register the Claude Code transcript collector as a Copilot hook. Its
event payload and transcript source are Claude-specific.
