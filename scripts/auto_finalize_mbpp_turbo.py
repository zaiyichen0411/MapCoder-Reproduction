import os
import time
from typing import List, Dict

try:
    import importlib
    mr = importlib.import_module('scripts.merge_results')
except Exception:
    import merge_results as mr  # fallback when running from scripts cwd

RESULTS_DIR = os.path.join(os.getcwd(), 'results')
FINAL_RESULTS_DIR = os.path.join(os.getcwd(), 'final-results')

MODEL = 'QwenCoderTurbo'
DATASET = 'MBPP'
LANGUAGE = 'Python3'
TEMPERATURE = '0.0'
PASS_AT_K = 1
PARTS = 6

STRATEGIES = ['Analogical', 'CoT', 'SelfPlanning']


def shards_exist_for_strategy(strategy: str) -> bool:
    run_name = mr.build_run_name(MODEL, strategy, DATASET, LANGUAGE, TEMPERATURE, PASS_AT_K)
    for idx in range(1, PARTS + 1):
        candidates = mr.candidate_shard_paths(RESULTS_DIR, run_name, idx)
        if not any(os.path.exists(p) for p in candidates):
            return False
    return True


def merge_and_summarize(strategy: str) -> Dict[str, str]:
    run_name = mr.build_run_name(MODEL, strategy, DATASET, LANGUAGE, TEMPERATURE, PASS_AT_K)
    merged_out = os.path.join(RESULTS_DIR, DATASET, f"{run_name}-merged.jsonl")
    rows: List[dict] = []
    missing: List[int] = []
    for idx in range(1, PARTS + 1):
        found_path = None
        for p in mr.candidate_shard_paths(RESULTS_DIR, run_name, idx):
            if os.path.exists(p):
                found_path = p
                break
        if not found_path:
            missing.append(idx)
            continue
        part_rows = mr.read_jsonl(found_path)
        rows.extend(part_rows)
        print(f"[{strategy}] Loaded p{idx}: {len(part_rows)} rows")

    if missing:
        print(f"[{strategy}] WARNING: Missing parts: {missing}")

    # Write merged
    mr.write_jsonl(merged_out, rows)
    print(f"[{strategy}] Merged -> {merged_out} ({len(rows)} rows)")

    # Write per-strategy summary into final-results/<MODEL>/<DATASET>/summary_<Strategy>.md
    summary = mr.summarize(rows)
    summary_dir = os.path.join(FINAL_RESULTS_DIR, MODEL, DATASET)
    os.makedirs(summary_dir, exist_ok=True)
    summary_out = os.path.join(summary_dir, f"summary_{strategy}.md")
    mr.write_summary_md(summary_out, DATASET, run_name, summary, PARTS, merged_out)
    print(f"[{strategy}] Summary -> {summary_out}")
    return {"merged": merged_out, "summary": summary_out}


def update_overview_and_charts():
    # Regenerate overview for Turbo and all charts
    os.system(f"python scripts/generate_model_overview.py --models {MODEL}")
    os.system("python scripts/generate_progress_charts.py")
    print("Refreshed overview and charts.")


def main():
    print("Auto finalize MBPP (Turbo) — waiting for shards to complete...")
    merged_done = {st: False for st in STRATEGIES}
    # Poll until all strategies finish
    while True:
        all_done = True
        for st in STRATEGIES:
            if not merged_done[st]:
                if shards_exist_for_strategy(st):
                    print(f"Detected completion: {st}")
                    try:
                        merge_and_summarize(st)
                        merged_done[st] = True
                        # After each completed strategy, refresh overview/charts to reflect progress
                        update_overview_and_charts()
                    except Exception as e:
                        print(f"ERROR merging {st}: {e}")
                else:
                    all_done = False
        if all_done:
            print("All MBPP strategies merged and summaries updated.")
            break
        time.sleep(60)  # poll every minute


if __name__ == '__main__':
    main()