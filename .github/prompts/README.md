# Copilot Prompt Files

These `.prompt.md` files are GitHub Copilot prompt files for the VS Code Local
agent.

VS Code Agent Host does not load prompt files. In Agent Host sessions, invoke
the corresponding custom agent directly instead of relying on these files.

Rules:
- Full-flow prompts select `stlc-orchestrator-agent`; stage prompts select their
  corresponding Copilot custom agent.
- Reusable instructions live in `.github/skills/<skill-name>/SKILL.md` and load
  through Copilot Agent Skills, not a textual `Skill:` tool call.
- `00-stlc-pipeline-contract.md` is reference documentation, not an invokable prompt.
