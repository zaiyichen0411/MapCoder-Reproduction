import argparse
import json
import os
import re
from typing import List, Dict, Any


def ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def build_run_name(model: str, strategy: str, dataset: str, language: str, temperature: str, pass_at_k: int) -> str:
    try:
        t_float = float(temperature)
        temperature_str_pref = f"{t_float:.1f}"
    except Exception:
        temperature_str_pref = str(temperature)
    return f"{model}-{strategy}-{dataset}-{language}-{temperature_str_pref}-{pass_at_k}"


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_code_from_responses(responses: List[str]) -> str | None:
    if not responses:
        return None
    # Try to extract from fenced code blocks
    code_block_re = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL | re.IGNORECASE)
    for r in responses:
        m = code_block_re.search(r)
        if m:
            return m.group(1).strip()
    # Fallback: return raw response
    return responses[0].strip()


def choose_solution(row: Dict[str, Any]) -> str | None:
    # Prefer structured source_codes
    srcs = row.get("source_codes")
    if isinstance(srcs, list) and srcs:
        # First non-empty entry
        for s in srcs:
            if isinstance(s, str) and s.strip():
                return s.strip()
    # Fallback to responses
    resps = row.get("responses")
    if isinstance(resps, list) and resps:
        return extract_code_from_responses(resps)
    return None


def main():
    parser = argparse.ArgumentParser(description="Generate HumanEvalPlus samples.jsonl from HumanEval merged results")
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--strategy", type=str, required=True)
    parser.add_argument("--language", type=str, default="Python3")
    parser.add_argument("--temperature", type=str, default="0.0")
    parser.add_argument("--pass_at_k", type=int, default=1)
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument("--out_dir", type=str, default=os.path.join("results", "HumanEvalPlus"))
    args = parser.parse_args()

    run_name = build_run_name(args.model, args.strategy, "HumanEval", args.language, args.temperature, args.pass_at_k)
    merged_path = os.path.join(args.results_dir, f"{run_name}-merged.jsonl")
    if not os.path.exists(merged_path):
        raise FileNotFoundError(f"Merged HumanEval results not found: {merged_path}. Ensure you have merged shards before generating samples.")

    rows = read_jsonl(merged_path)
    print(f"Loaded {len(rows)} merged rows from: {merged_path}")

    out_path = os.path.join(args.out_dir, f"{args.model}-{args.strategy}-HumanEvalPlus-samples.jsonl")
    ensure_dir(out_path)

    written = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for r in rows:
            task_id = r.get("task_id")
            sol = choose_solution(r)
            if not task_id or not sol:
                continue
            # Normalize solution: optionally prepend typing import to match existing samples style
            if not sol.lstrip().startswith("from typing"):
                sol = "from typing import *\n\n" + sol
            out.write(json.dumps({"task_id": task_id, "solution": sol}, ensure_ascii=False) + "\n")
            written += 1

    print(f"Samples written: {out_path} ({written} items)")


if __name__ == "__main__":
    main()