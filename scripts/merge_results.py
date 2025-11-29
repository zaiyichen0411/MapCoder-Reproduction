import os
import json
import argparse
from typing import List
import sys
from os.path import abspath, dirname, join

repo_root = abspath(join(dirname(__file__), ".."))
sys.path.insert(0, join(repo_root, "src"))


def ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def build_run_name(model: str, strategy: str, dataset: str, language: str, temperature: str, pass_at_k: int) -> str:
    """
    Build RUN_NAME consistent with src/main.py, but temperature is handled as a string
    to avoid mismatches like 0 vs 0.0.
    """
    # Normalize temperature formatting: keep as-is, but also provide a float format fallback
    try:
        t_float = float(temperature)
        # prefer one decimal to match typical naming like `0.0`
        temperature_str_pref = f"{t_float:.1f}"
    except Exception:
        temperature_str_pref = str(temperature)
    return f"{model}-{strategy}-{dataset}-{language}-{temperature_str_pref}-{pass_at_k}"


def candidate_shard_paths(results_dir: str, base_run_name: str, part_idx: int) -> List[str]:
    """
    Generate candidate shard paths to tolerate minor formatting differences.
    e.g., 0 vs 0.0 in the temperature segment.
    """
    # First try exact
    paths = [os.path.join(results_dir, f"{base_run_name}p{part_idx}.jsonl")]
    # Try alternative forms: temperature 0 or 0.00
    tokens = base_run_name.split("-")
    if len(tokens) >= 6:
        # tokens: [model, strategy, dataset, language, temperature, pass_at_k]
        temp = tokens[-2]
        try:
            tf = float(temp)
            variants = {f"{tf}", f"{tf:.1f}", f"{tf:.2f}", str(int(tf))}
            for v in variants:
                alt = tokens[:-2] + [v, tokens[-1]]
                alt_name = "-".join(alt)
                p = os.path.join(results_dir, f"{alt_name}p{part_idx}.jsonl")
                if p not in paths:
                    paths.append(p)
        except Exception:
            pass
    return paths


def read_jsonl(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: str, rows: List[dict]):
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def summarize(rows: List[dict]) -> dict:
    total = len(rows)
    solved = sum(1 for r in rows if r.get("is_solved", False))
    rate = (solved / total * 100.0) if total else 0.0
    return {"total": total, "solved": solved, "pass_rate": rate}


def write_summary_md(path: str, dataset: str, run_name: str, summary: dict, parts: int, merged_path: str):
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {dataset} Summary\n\n")
        f.write(f"- Run: `{run_name}`\n")
        f.write(f"- Parts merged: `{parts}`\n")
        f.write(f"- Merged file: `{merged_path}`\n")
        f.write(f"- Total problems: `{summary['total']}`\n")
        f.write(f"- Solved: `{summary['solved']}`\n")
        f.write(f"- Pass rate: `{summary['pass_rate']:.2f}%`\n")


def main():
    parser = argparse.ArgumentParser(description="Merge shards and summarize HumanEval results")
    parser.add_argument("--dataset", type=str, default="HumanEval")
    parser.add_argument("--strategy", type=str, default="MapCoder")
    parser.add_argument("--model", type=str, default="QwenCoderTurbo")
    parser.add_argument("--language", type=str, default="Python3")
    parser.add_argument("--temperature", type=str, default="0.0")
    parser.add_argument("--pass_at_k", type=int, default=1)
    parser.add_argument("--parts", type=int, default=8)
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument("--merged_out", type=str, default=None)
    parser.add_argument("--summary_out", type=str, default=None)
    parser.add_argument("--single_path", type=str, default=None, help="Summarize a single results file instead of merging shards")
    parser.add_argument("--dedup", action="store_true")
    parser.add_argument("--compute_missing", action="store_true")

    args = parser.parse_args()

    run_name = build_run_name(args.model, args.strategy, args.dataset, args.language, args.temperature, args.pass_at_k)
    merged_out = args.merged_out or os.path.join(args.results_dir, f"{run_name}-merged.jsonl")
    summary_out = args.summary_out or os.path.join("final-results", args.model, args.dataset, "summary.md")

    if args.single_path:
        # Single-file summarize mode
        src_path = args.single_path
        if not os.path.isabs(src_path):
            src_path = os.path.join(args.results_dir, src_path)
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Single results file not found: {src_path}")
        rows = read_jsonl(src_path)
        print(f"Summarizing single file: {src_path} ({len(rows)} rows)")
        merged_out = src_path
        parts_used = 1
    else:
        print(f"Merging shards for {run_name} (parts={args.parts})")

        rows: List[dict] = []
        missing: List[int] = []
        for idx in range(1, args.parts + 1):
            found_path = None
            for p in candidate_shard_paths(args.results_dir, run_name, idx):
                if os.path.exists(p):
                    found_path = p
                    break
            if not found_path:
                missing.append(idx)
                continue
            part_rows = read_jsonl(found_path)
            rows.extend(part_rows)
            print(f" - Loaded p{idx}: {len(part_rows)} rows")

        if missing:
            print(f"WARNING: Missing parts: {missing}")

        if args.dedup:
            seen = set()
            deduped = []
            for r in rows:
                k = r.get("task_id") or r.get("name") or r.get("id")
                if k in seen:
                    continue
                seen.add(k)
                deduped.append(r)
            print(f"Dedup: {len(rows)} -> {len(deduped)}")
            rows = deduped

        # Write merged
        write_jsonl(merged_out, rows)
        print(f"Merged output: {merged_out} ({len(rows)} rows)")
        parts_used = args.parts

    # Summary
    s = summarize(rows)
    print(f"Summary: total={s['total']} solved={s['solved']} pass_rate={s['pass_rate']:.2f}%")
    write_summary_md(summary_out, args.dataset, run_name, s, parts_used, merged_out)
    print(f"Summary written to: {summary_out}")

    if args.compute_missing:
        try:
            from datasets.DatasetFactory import DatasetFactory
            dataset_cls = DatasetFactory.get_dataset_class(args.dataset)
            dataset = dataset_cls()
            ids = [
                (it.get(getattr(dataset, "id_key", "id")) or it.get("name") or it.get("id"))
                for it in dataset.data
            ]
            done = set()
            for r in rows:
                done.add(r.get("task_id") or r.get("name") or r.get("id"))
            missing_idx = [i for i, tid in enumerate(ids) if tid not in done]
            ranges = []
            if missing_idx:
                s0 = missing_idx[0]
                prev = s0
                for x in missing_idx[1:]:
                    if x == prev + 1:
                        prev = x
                    else:
                        ranges.append((s0, prev + 1))
                        s0 = x
                        prev = x
                ranges.append((s0, prev + 1))
            print(f"Missing count: {len(missing_idx)}")
            print(f"Missing ranges: {ranges}")
        except Exception as e:
            print(f"Failed to compute missing indices: {e}")


if __name__ == "__main__":
    main()