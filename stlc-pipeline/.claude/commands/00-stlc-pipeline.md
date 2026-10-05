# 00-stlc-pipeline

Run the full enterprise STLC multi-agent pipeline from requirement intake through closure reporting.

Arguments: `$ARGUMENTS`

Invoke the skill using the Skill tool:

```text
Skill: claude-stlc:00-stlc-pipeline
Args: $ARGUMENTS
```

Examples:
- `/claude-stlc --ticket=TICKET-1234`
- `/claude-stlc --ticket=TICKET-1234 --resume`
- `/claude-stlc --ticket=TICKET-1234 --from=stage-03`
- `/claude-stlc --text="As a user I want..."`

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
