import json
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / ".github" / "config" / "project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    workflow = project_root / config["workflowDefinition"]
    if not workflow.is_file():
        raise SystemExit(f"Missing Java workflow definition: {workflow}")
    print("java validation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
