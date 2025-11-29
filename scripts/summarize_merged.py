import argparse
import json


def is_solved_entry(obj: dict) -> bool:
    # Try common flags across our merged outputs
    if isinstance(obj, dict):
        if obj.get("is_solved") is True:
            return True
        if obj.get("passed") is True:
            return True
        status = obj.get("status") or obj.get("result")
        if isinstance(status, str) and status.lower() in {"passed", "success", "accepted"}:
            return True
    return False


def summarize(path: str, total_override: int | None = None):
    total = 0
    solved = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # Some lines may be long; best effort skip malformed ones
                continue
            if is_solved_entry(obj):
                solved += 1

    if total_override is not None:
        total = total_override

    pass_rate = (solved / total * 100.0) if total else 0.0
    return total, solved, pass_rate


def main():
    parser = argparse.ArgumentParser(description="Summarize merged JSONL by counting solved entries.")
    parser.add_argument("--file", required=True, help="Path to merged .jsonl file")
    parser.add_argument("--total", type=int, default=None, help="Override total problems if known")
    args = parser.parse_args()

    total, solved, pass_rate = summarize(args.file, args.total)
    print(f"file={args.file}")
    print(f"total={total}")
    print(f"solved={solved}")
    print(f"pass_rate={pass_rate:.2f}%")


if __name__ == "__main__":
    main()