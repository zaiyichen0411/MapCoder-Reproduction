import json
import random
import os


def read_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def is_solved(obj: dict) -> bool:
    if not isinstance(obj, dict):
        return False
    if obj.get("is_solved") is True:
        return True
    if obj.get("passed") is True:
        return True
    status = obj.get("status") or obj.get("result")
    if isinstance(status, str) and status.lower() in {"passed", "success", "accepted"}:
        return True
    return False


def sample_compare(name: str, map_path: str, base_path: str, key_fields: list[str], sample_n: int = 50, seed: int = 42):
    random.seed(seed)
    map_rows = read_jsonl(map_path)
    base_rows = read_jsonl(base_path)

    def key_of(row: dict):
        for k in key_fields:
            v = row.get(k)
            if v:
                return v
        return None

    map_dict = {key_of(r): r for r in map_rows}
    base_dict = {key_of(r): r for r in base_rows}
    keys = [k for k in map_dict.keys() if k in base_dict and k is not None]
    if not keys:
        print(f"[{name}] 无可比对的公共样本键，跳过")
        return

    # deterministic sample
    keys.sort()
    sample_keys = keys[: sample_n] if len(keys) >= sample_n else keys
    map_solved = sum(1 for k in sample_keys if is_solved(map_dict[k]))
    base_solved = sum(1 for k in sample_keys if is_solved(base_dict[k]))
    total = len(sample_keys)
    print(f"[{name}] sample_size={total}")
    print(f"MapCoder solved: {map_solved}")
    print(f"Baseline solved: {base_solved}")
    print(f"MapCoder pass@1: {map_solved/total*100:.2f}%")
    print(f"Baseline pass@1: {base_solved/total*100:.2f}%")


def main():
    # HumanEval: GPT4-Turbo MapCoder vs CoT
    he_map = os.path.join(
        "archive",
        "final-results-backup",
        "GPT4",
        "HumanEval",
        "GPT4-Turbo-MapCoder-5-5-Human-Python3-0-1.jsonl",
    )
    he_cot = os.path.join(
        "archive",
        "final-results-backup",
        "GPT4",
        "HumanEval",
        "GPT4-Turbo-CoT-Human-Python3-0-1.jsonl",
    )
    sample_compare("HumanEval (GPT4-Turbo, MapCoder vs CoT)", he_map, he_cot, ["task_id"], sample_n=50)

    # MBPP: GPT4-Turbo MapCoder vs CoT
    mbpp_map = os.path.join(
        "archive",
        "final-results-backup",
        "GPT4",
        "MBPP",
        "GPT4-Turbo-MapCoder-3-5-MBPP-Python3-0-1.jsonl",
    )
    mbpp_cot = os.path.join(
        "archive",
        "final-results-backup",
        "GPT4",
        "MBPP",
        "GPT4-Turbo-CoT-MBPP-Python3-0-1.jsonl",
    )
    sample_compare("MBPP (GPT4-Turbo, MapCoder vs CoT)", mbpp_map, mbpp_cot, ["name", "task_id"], sample_n=50)


if __name__ == "__main__":
    main()