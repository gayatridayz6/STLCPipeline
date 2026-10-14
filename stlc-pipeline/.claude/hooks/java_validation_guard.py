from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    workflow = project_root / "workflow" / "STLCWorkflowOrchestrator.java"
    if not workflow.is_file():
        raise SystemExit(f"Missing Java workflow definition: {workflow}")
    print("java validation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
