import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DEST = ROOT / "archive" / "logs"
RESULTS_ROOT = ROOT / "results"

DATASET_MAP = {
    "APPS": "APPS",
    "CC": "CodeContest",
    "HumanEval": "HumanEval",
    "MBPP": "MBPP",
    "XCode": "XCode",
}

STRATEGY_MAP = {
    "Ana": "Analogical",
    "CoT": "CoT",
    "Map": "MapCoder",
    "SP": "SelfPlanning",
    "direct": "Direct",
    "mc": "MapCoder",
    "ana": "Analogical",
    "cot": "CoT",
    "sp": "SelfPlanning",
}

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def organize_logs():
    moves = []
    patterns = [
        (r"^(APPS)_(Ana|CoT|Map|SP)_\d+\.log$", lambda m: (m.group(1), STRATEGY_MAP[m.group(2)])),
        (r"^(CC)_(Ana|CoT|Map|SP)_\d+\.log$", lambda m: (m.group(1), STRATEGY_MAP[m.group(2)])),
        (r"^(XCode)_(Ana|CoT|Map|SP)_\d+\.log$", lambda m: (m.group(1), STRATEGY_MAP[m.group(2)])),
        # HumanEval standard logs, e.g., he_cot_1.log
        (r"^he_(ana|cot|direct|mc|sp)_\d+\.log$", lambda m: ("HumanEval", STRATEGY_MAP[m.group(1)])),
        # HumanEval retry logs, e.g., he_ana_retry_1.log
        (r"^he_(ana|cot|direct|mc|sp)_retry_\d+\.log$", lambda m: ("HumanEval", f"{STRATEGY_MAP[m.group(1)]}Retry")),
        (r"^he_cot_fix_\d+\.log$", lambda m: ("HumanEval", "CoTFix")),
        (r"^he_sp_retry_\d+\.log$", lambda m: ("HumanEval", "SelfPlanningRetry")),
        (r"^output_\d+\.log$", lambda m: ("misc", "system")),
    ]

    for name in os.listdir(ROOT):
        if not name.endswith(".log"):
            continue
        for pat, f in patterns:
            m = re.match(pat, name)
            if m:
                dataset, strategy = f(m)
                dest_dir = LOG_DEST / dataset / strategy
                ensure_dir(dest_dir)
                src = ROOT / name
                dst = dest_dir / name
                shutil.move(str(src), str(dst))
                moves.append((src, dst))
                break
    return moves

def organize_results_jsonl():
    moves = []
    # Move QwenCoder480b-* jsonl from results root to dataset subfolders.
    for name in os.listdir(RESULTS_ROOT):
        if not name.endswith(".jsonl"):
            continue
        # Expect patterns like QwenCoder480b-<Strategy>-<Dataset>-Python3-...
        m = re.match(r"^(QwenCoder480b|QwenCoderTurbo)-([A-Za-z]+)-(APPS|CC|HumanEval|MBPP|XCode)-.*\.jsonl$", name)
        if not m:
            continue
        model, strategy, dataset_key = m.groups()
        dataset_folder = DATASET_MAP.get(dataset_key, dataset_key)
        dest_dir = RESULTS_ROOT / dataset_folder
        ensure_dir(dest_dir)
        src = RESULTS_ROOT / name
        dst = dest_dir / name
        # Skip if already in place
        if src == dst:
            continue
        shutil.move(str(src), str(dst))
        moves.append((src, dst))
    return moves

def main():
    log_moves = organize_logs()
    res_moves = organize_results_jsonl()
    print(f"Moved logs: {len(log_moves)}")
    for s, d in log_moves[:10]:
        print(f"  {s} -> {d}")
    if len(log_moves) > 10:
        print("  ...")

    print(f"Moved results jsonl: {len(res_moves)}")
    for s, d in res_moves[:10]:
        print(f"  {s} -> {d}")
    if len(res_moves) > 10:
        print("  ...")

if __name__ == "__main__":
    main()