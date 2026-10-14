# 00-stlc-pipeline

Run the full enterprise STLC multi-agent pipeline from requirement intake through closure reporting.

Arguments: `$ARGUMENTS`

Before invoking the skill, initialize the run dashboard using the **Token dashboard
contract** below. Apply that contract to the skill's subagent calls and finalize
the report before returning to the user, including at approval stops.

Invoke the skill using the Skill tool:

```text
Skill: claude-stlc:00-stlc-pipeline
Args: $ARGUMENTS
```

Examples:

**Local entry points with the token dashboard contract:**
- `/00-stlc-pipeline --ticket=STL-101` - Run this local wrapper and generate the dashboard
- `/00-stlc-pipeline --ticket=STL-101 --resume` - Reuse the checkpoint's dashboard run ID
- `/stlc --ticket=STL-101` - Equivalent local wrapper

**Full pipeline (main entry point):**
- `/claude-stlc --ticket=STL-101` — Run complete STLC pipeline from triage to closure
- `/claude-stlc --ticket=STL-101 --resume` — Resume from last checkpoint if interrupted
- `/claude-stlc --text="User login with email and password"` — Run full pipeline with inline requirements
- `/claude-stlc --ticket=STL-101 --from=stage-05` — Jump to security gate stage and continue

**Individual stage commands (for targeted workflows):**
- `/claude-stlc:01-requirements-analysis --ticket=STL-101` — Triage & requirements analysis only
- `/claude-stlc:02-test-planning --ticket=STL-101` — Test planning & strategy
- `/claude-stlc:03-test-design --ticket=STL-101` — BDD scenario generation
- `/claude-stlc:04a-engineering --ticket=STL-101` — Test implementation & engineering
- `/claude-stlc:04b-execution --ticket=STL-101` — Execute tests & collect evidence
- `/claude-stlc:05-security-gate --ticket=STL-101` — Security & compliance analysis
- `/claude-stlc:06-pr-review --ticket=STL-101` — PR review & code quality check
- `/claude-stlc:07-hitl-gate --ticket=STL-101` — Human approval & audit trail
- `/claude-stlc:08-closure-sync --ticket=STL-101` — Final closure & reporting

Execution flow:

1. **Phase 0 - MCP Preflight**
   - Verify MCP connections (GitHub, Jira, Jenkins)
   - Validate configuration and authentication
   - Skill: `claude-stlc:mcp-preflight`

2. **Phase 1 - Requirements Analysis & Triage**
   - Agent: `triage-agent`
   - Skill: `claude-stlc:01-requirements-analysis`
   - Parse Jira ticket or pasted requirements
   - Check for existing test coverage
   - Output: `artifacts/requirement_analysis.md`
   - Decision: Generate new tests or reuse existing?

3. **Phase 2 - Test Planning & Strategy**
   - Agent: `qa-strategist-agent`
   - Skill: `claude-stlc:02-test-planning`
   - Create risk-based test plan
   - Define test scope and environment needs
   - Output: `artifacts/test_planning.md`
   - Gate: Human approval required

4. **Phase 3 - Test Design & BDD Scenarios**
   - Agent: `qa-sentinel-agent`
   - Skill: `claude-stlc:03-test-design`
   - Generate BDD test scenarios
   - Create acceptance criteria mappings
   - Output: `artifacts/test_design.md`
   - Gate: Human approval required

5. **Phase 4a - Engineering & Implementation**
   - Agent: `engineer-agent`
   - Skill: `claude-stlc:04a-engineering`
   - Develop test automation code
   - Configure test environments
   - Output: `artifacts/engineering_summary.md`

6. **Phase 4b - Test Execution & Evidence Collection**
   - Agent: `qa-runner-agent`
   - Skill: `claude-stlc:04b-execution`
   - Execute test suite via MCP Jenkins triggers
   - Collect test results and evidence
   - Output: `artifacts/test_execution_report.md`

7. **Phase 5 - Security & Compliance Gate**
   - Agent: `security-gate-agent`
   - Skill: `claude-stlc:05-security-gate`
   - Analyze security scan results
   - Perform RCA and QE Radar tagging
   - Output: `artifacts/security_compliance_report.md`
   - Gate: Human approval required

8. **Phase 6 - PR Review & Code Quality**
   - Agent: `github-mcp-agent`
   - Skill: `claude-stlc:06-pr-review`
   - Create PR summary via GitHub MCP
   - Prepare merge readiness checklist
   - Output: `artifacts/pr_review_summary.md`

9. **Phase 7 - Human-in-the-Loop Gate**
   - Agent: `hitl-gate-agent`
   - Skill: `claude-stlc:07-hitl-gate`
   - Record human approval decisions
   - Document audit trail
   - Output: `artifacts/hitl_audit_trail.md`
   - Gate: Final go/no-go decision

10. **Phase 8 - Closure & Reporting**
    - Agent: `reporting-closure-agent`
    - Skill: `claude-stlc:08-closure-sync`
    - Generate closure metrics and summary
    - Log defects if applicable
    - Output: `artifacts/test_closure_metrics.md`

Conditional routing:

- If Stage 1 detects **linked existing tests**, skip Stage 2, 3, 4a and jump to Stage 4b (execution-summary-only mode)
- If Stage 1 detects **no linked tests**, execute full pipeline flow with all gates

Lifecycle hooks:

- **Pre-stage-validation.py**: Runs before each stage to validate inputs and prerequisites
- **approval_gate_guard.py**: Enforces human approvals and gates progression

Configuration:

- Read: `.claude/config/project.json`
- MCP configs: `.claude/config/mcp/github_mcp_config.json`, `.claude/config/mcp/jenkins_mcp_config.json`
- Hooks: `.claude/hooks/pre_stage_validation.py`, `.claude/hooks/approval_gate_guard.py`

Orchestrator agent:

- Main coordinator: `stlc-orchestrator-agent.md`
- Loads and invokes all stage subagents in sequence
- Enforces traceability, artifact contracts, and HITL gates
- Manages resume and branching logic

Stop conditions:

- Missing human approval at any HITL gate
- Blocker security or quality findings
- MCP connectivity failures
- Configuration validation errors

## Token dashboard contract

Run Claude Code from the `stlc-pipeline` directory so `.claude/settings.json`
loads the local `Agent|Task` telemetry hooks. Python must be available.
If hooks are newly added, restart Claude Code before executing this flow.
Use `/00-stlc-pipeline` or `/stlc` to load these local instructions. Calling
the installed `/claude-stlc` plugin directly does not necessarily load this
wrapper's dashboard contract.

1. **Initialize before Phase 0.** Choose a unique run ID such as
   `STL-101-20261013T113846` (letters, digits, hyphens and underscores only).
   For inline requirements use a unique `inline-<timestamp>` ID. Do not put
   requirement text in the ID. From the project directory run:

   ```powershell
   python workflow\token_dashboard.py init --run STL-101-20261013T113846 --label STL-101
   ```

   Persist this ID with the workflow checkpoint. A new execution gets a new ID;
   `--resume` reuses the existing ID and dashboard, not `init`. Refresh a resumed
   run with `finalize --status running` before continuing.

2. **Tag every actual subagent invocation.** Prefix the Agent/Task `prompt` with
   the following exact marker, substituting the run ID and mapped agent name:

   ```text
   [STLC run=STL-101-20261013T113846 agent=triage-agent]
   ```

   Pass the run ID and this contract into a delegated orchestrator too. Tag that
   invocation with `agent=stlc-orchestrator-agent`. Use the agent names from the
   execution flow for stage calls. Run agents synchronously, in stage order;
   background agents are not supported by this collector. Do not relabel
   unrelated calls as pipeline agents.

3. **Collect measured usage, never invented counts.** The local post-tool hook
   reads the returned `agentId` and that agent's local Claude Code JSONL transcript,
   sums API counters, and refreshes both `token_usage.json` and
   `stlc_dashboard.html` under `artifacts\runs\<run-id>\`. Duplicate message
   snapshots and resumed agent transcripts are not counted twice. Input, output,
   cache-write and cache-read tokens are shown separately; total includes all four.
   A skill executed inline has no separate agent telemetry. The top-level
   coordinator is N/A unless it is itself a tagged subagent.

4. **Finalize after the last agent returns, even on early stops.** Do this in the
   calling coordinator so closure-agent usage is included. For successful full
   closure or a completed reuse-existing-tests route:

   ```powershell
   python workflow\token_dashboard.py finalize --run STL-101-20261013T113846 --status completed
   ```

   At an approval gate or blocker, use `--status blocked --reason "Awaiting Stage 2 approval"`;
   for execution errors use `--status failed` with a concise, non-sensitive reason.
   Do not advance any stage merely to generate a report. A process killed before
   finalization retains its last snapshot; refresh/finalize it when resuming.

5. **Return the HTML report path/link to the user.** It opens directly in a
   browser, with no server or external assets. Distinguish measured partial
   totals from full-run totals. Unavailable telemetry must remain N/A, not zero
   or estimated. An agent with no recorded invocation is "not recorded", not
   automatically "skipped". If dashboard generation or hooks fail, report the
   error explicitly; do not claim token measurement succeeded.
