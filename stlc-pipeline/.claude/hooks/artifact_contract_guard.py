from pathlib import Path
import json


def main() -> int:
    config_path = Path(__file__).resolve().parents[1] / "config" / "project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    artifacts = config.get("artifacts", {})
    missing = [path for path in artifacts.values() if not (config_path.parent.parent / path).exists()]
    if missing:
        raise SystemExit("Missing artifact placeholders: " + ", ".join(missing))
    print("artifact contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())