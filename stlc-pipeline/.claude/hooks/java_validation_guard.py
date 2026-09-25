from pathlib import Path


def main() -> int:
    required = [
        Path("src/main/java/com/enterprise/services"),
        Path("src/main/java/com/enterprise/controllers"),
        Path("workflow/STLCWorkflowOrchestrator.java"),
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing Java scaffold: " + ", ".join(missing))
    print("java validation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
