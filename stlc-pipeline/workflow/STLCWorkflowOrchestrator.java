package workflow;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class STLCWorkflowOrchestrator {
    private final OrchestratorDefinition orchestrator = new OrchestratorDefinition(
        "delivery-orchestrator-agent",
        ".github/agents/00-delivery-orchestrator-agent.agent.md",
        List.of(
            ".github/prompts/mcp-preflight.prompt.md",
            ".github/prompts/stlc.prompt.md"
        ),
        List.of(
            ".github/hooks/pre_stage_validation.py",
            ".github/hooks/artifact_contract_guard.py",
            ".github/hooks/approval_gate_guard.py"
        ),
        List.of(
            "triage-agent",
            "planning-agent",
            "test-design-agent",
            "engineer-agent",
            "execution-agent",
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
            ".github/prompts/01-requirements-analysis.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/artifact_contract_guard.py"),
            List.of(".github/skills/jira-parser/SKILL.md"),
            List.of("jira"),
            Map.of(
                "reuse-existing-tests", "stage-04b-execution-only",
                "generate-new-tests", "stage-02"
            ),
            "stlc-pipeline/artifacts/requirement_analysis.md",
            true,
            List.of(),
            "stage-02"
        ),
        new StageNode(
            "stage-02",
            "Test Planning & Strategy",
            "planning-agent",
            ".github/prompts/02-test-planning.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/artifact_contract_guard.py"),
            List.of(".github/skills/test-planning-strategist/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/test_planning.md",
            true,
            List.of("stage-01"),
            "stage-03"
        ),
        new StageNode(
            "stage-03",
            "Test Case Design & Generation",
            "test-design-agent",
            ".github/prompts/03-test-design.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/artifact_contract_guard.py"),
            List.of(".github/skills/bdd-generator/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/test_design.md",
            true,
            List.of("stage-02"),
            "stage-04a"
        ),
        new StageNode(
            "stage-04a",
            "Test Automation Engineering",
            "engineer-agent",
            ".github/prompts/04a-engineering.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/execution-evidence-writer/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/engineering_summary.md",
            true,
            List.of("stage-03"),
            "stage-04b"
        ),
        new StageNode(
            "stage-04b",
            "Test Execution & Evidence Collection",
            "execution-agent",
            ".github/prompts/04b-execution.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/execution-evidence-writer/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/test_execution_report.md",
            true,
            List.of("stage-04a"),
            "stage-05"
        ),
        new StageNode(
            "stage-04b-execution-only",
            "Execution Summary for Existing Story Automation",
            "execution-agent",
            ".github/prompts/04b-execution.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/execution-evidence-writer/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/test_execution_report.md",
            true,
            List.of("stage-01"),
            null
        ),
        new StageNode(
            "stage-05",
            "Security & Compliance Gate",
            "security-gate-agent",
            ".github/prompts/05-security-gate.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/security-compliance-review/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/security_compliance_report.md",
            true,
            List.of("stage-04b"),
            "stage-06"
        ),
        new StageNode(
            "stage-06",
            "GitHub PR Creation & Automated Code Review",
            "github-mcp-agent",
            ".github/prompts/06-pr-review.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/pr-review-prep/SKILL.md"),
            List.of("github"),
            Map.of(),
            "stlc-pipeline/artifacts/pr_review_summary.md",
            true,
            List.of("stage-05"),
            "stage-07"
        ),
        new StageNode(
            "stage-07",
            "Human-in-the-Loop Approval Gate",
            "hitl-gate-agent",
            ".github/prompts/07-hitl-gate.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/approval_gate_guard.py"),
            List.of(".github/skills/hitl-audit-writer/SKILL.md"),
            List.of(),
            Map.of(),
            "stlc-pipeline/artifacts/hitl_audit_trail.md",
            false,
            List.of("stage-06"),
            "stage-08"
        ),
        new StageNode(
            "stage-08",
            "Test Closure & Jira Sync",
            "reporting-closure-agent",
            ".github/prompts/08-closure-sync.prompt.md",
            List.of(".github/hooks/pre_stage_validation.py", ".github/hooks/artifact_contract_guard.py"),
            List.of(".github/skills/execution-evidence-writer/SKILL.md", ".github/skills/hitl-audit-writer/SKILL.md"),
            List.of("jira"),
            Map.of(),
            "stlc-pipeline/artifacts/test_closure_metrics.md",
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
