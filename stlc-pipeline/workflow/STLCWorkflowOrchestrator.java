package workflow;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class STLCWorkflowOrchestrator {
    private final OrchestratorDefinition orchestrator = new OrchestratorDefinition(
        "stlc-orchestrator-agent",
        ".claude/agents/stlc-orchestrator-agent.md",
        List.of(
            ".claude/commands/mcp-preflight.md",
            ".claude/commands/stlc.md"
        ),
        List.of(
            ".claude/hooks/pre_stage_validation.py",
            ".claude/hooks/artifact_contract_guard.py",
            ".claude/hooks/approval_gate_guard.py"
        ),
        List.of(
            "triage-agent",
            "qa-strategist-agent",
            "qa-sentinel-agent",
            "engineer-agent",
            "qa-runner-agent",
            "security-gate-agent",
            "github-mcp-agent",
            "hitl-gate-agent",
            "reporting-closure-agent"
        )
    );

    private final List<StageNode> stages = List.of(
        new StageNode(
            "stage-01",
            "Requirements Analysis & Triage",
            "triage-agent",
            ".claude/commands/01-requirements-analysis.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/artifact_contract_guard.py"),
            List.of(".claude/skills/jira-parser.md"),
            List.of("jira"),
            Map.of(
                "reuse-existing-tests", "stage-04b-execution-only",
                "generate-new-tests", "stage-02"
            ),
            "artifacts/requirement_analysis.md",
            true,
            List.of(),
            "stage-02"
        ),
        new StageNode(
            "stage-02",
            "Test Planning & Strategy",
            "qa-strategist-agent",
            ".claude/commands/02-test-planning.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/artifact_contract_guard.py"),
            List.of(".claude/skills/test-planning-strategist.md"),
            List.of(),
            Map.of(),
            "artifacts/test_planning.md",
            true,
            List.of("stage-01"),
            "stage-03"
        ),
        new StageNode(
            "stage-03",
            "Test Case Design & Generation",
            "qa-sentinel-agent",
            ".claude/commands/03-test-design.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/artifact_contract_guard.py"),
            List.of(".claude/skills/bdd-generator.md"),
            List.of(),
            Map.of(),
            "artifacts/test_design.md",
            true,
            List.of("stage-02"),
            "stage-04"
        ),
        new StageNode(
            "stage-04",
            "Development & Self-Healing Execution",
            "engineer-agent",
            ".claude/commands/04a-engineering.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/approval_gate_guard.py"),
            List.of(".claude/skills/execution-evidence-writer.md"),
            List.of(),
            Map.of(),
            "artifacts/test_execution_report.md",
            true,
            List.of("stage-03"),
            "stage-05"
        ),
        new StageNode(
            "stage-04b-execution-only",
            "Execution Summary for Existing Story Automation",
            "qa-runner-agent",
            ".claude/commands/04b-execution.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/approval_gate_guard.py"),
            List.of(".claude/skills/execution-evidence-writer.md"),
            List.of(),
            Map.of(),
            "artifacts/test_execution_report.md",
            true,
            List.of("stage-01"),
            null
        ),
        new StageNode(
            "stage-05",
            "Security & Compliance Gate",
            "security-gate-agent",
            ".claude/commands/05-security-gate.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/approval_gate_guard.py"),
            List.of(".claude/skills/security-compliance-review.md"),
            List.of(),
            Map.of(),
            "artifacts/security_compliance_report.md",
            true,
            List.of("stage-04"),
            "stage-06"
        ),
        new StageNode(
            "stage-06",
            "GitHub PR Creation & Automated Code Review",
            "github-mcp-agent",
            ".claude/commands/06-pr-review.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/approval_gate_guard.py"),
            List.of(".claude/skills/pr-review-prep.md"),
            List.of("github"),
            Map.of(),
            "artifacts/pr_review_summary.md",
            true,
            List.of("stage-05"),
            "stage-07"
        ),
        new StageNode(
            "stage-07",
            "Human-in-the-Loop Approval Gate",
            "hitl-gate-agent",
            ".claude/commands/07-hitl-gate.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/approval_gate_guard.py"),
            List.of(".claude/skills/hitl-audit-writer.md"),
            List.of(),
            Map.of(),
            "artifacts/hitl_audit_trail.md",
            false,
            List.of("stage-06"),
            "stage-08"
        ),
        new StageNode(
            "stage-08",
            "Test Closure & Jira Sync",
            "reporting-closure-agent",
            ".claude/commands/08-closure-sync.md",
            List.of(".claude/hooks/pre_stage_validation.py", ".claude/hooks/artifact_contract_guard.py"),
            List.of(".claude/skills/execution-evidence-writer.md", ".claude/skills/hitl-audit-writer.md"),
            List.of("jira"),
            Map.of(),
            "artifacts/test_closure_metrics.md",
            true,
            List.of("stage-07"),
            null
        )
    );

    private final Map<String, StageNode> stageIndex = stages.stream()
        .collect(Collectors.toMap(StageNode::id, stage -> stage));

    public List<StageNode> stages() {
        return stages;
    }

    public OrchestratorDefinition orchestrator() {
        return orchestrator;
    }

    public Optional<StageNode> stage(String stageId) {
        return Optional.ofNullable(stageIndex.get(stageId));
    }

    public boolean requiresApproval(String stageId) {
        return stage(stageId)
            .map(StageNode::requiresHumanApprovalBeforeStart)
            .orElse(false);
    }

    public Optional<String> routeFor(String stageId, String decision) {
        return stage(stageId)
            .map(StageNode::routingDecisions)
            .map(routes -> routes.get(decision));
    }

    public record OrchestratorDefinition(
        String name,
        String agentPath,
        List<String> commands,
        List<String> preHooks,
        List<String> subAgents
    ) {
    }

    public record StageNode(
        String id,
        String name,
        String agent,
        String commandPath,
        List<String> hooks,
        List<String> skills,
        List<String> mcpDependencies,
        Map<String, String> routingDecisions,
        String artifactPath,
        boolean requiresHumanApprovalBeforeStart,
        List<String> dependsOn,
        String nextStageId
    ) {
    }
}
