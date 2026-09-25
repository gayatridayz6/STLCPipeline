from pathlib import Path
import json


def main() -> int:
    config_path = Path(__file__).resolve().parents[1] / "config" / "project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("approvalMode") != "human-in-the-loop":
        raise SystemExit("approvalMode must remain human-in-the-loop")
    print("pre-stage validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
