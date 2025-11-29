import os
import json
from typing import Dict, Any, List


STRATEGIES = [
    "Analogical",
    "CoT",
    "Direct",
    "MapCoder",
    "SelfPlanning",
]

RESULTS_BASE = os.path.join("results", "humanevalplus")

MODEL_NAME = None
SUMMARY_DIR = None


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def find_json_files(directory: str) -> List[str]:
    files = []
    if os.path.exists(directory):
        for f in os.listdir(directory):
            if f.lower().endswith(".json"):
                files.append(os.path.join(directory, f))
    return files


def extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    metrics = {}
    for k, v in data.items():
        if isinstance(v, (int, float, str)):
            metrics[k] = v
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, (int, float, str)):
                    metrics[f"{k}.{kk}"] = vv
    return metrics


def write_summary_md(strategy: str, metrics: Dict[str, Any], status: str) -> None:
    ensure_dir(SUMMARY_DIR)
    filename = os.path.join(SUMMARY_DIR, f"{strategy}-summary.md")
    lines = []
    lines.append(f"# HumanEvalPlus Summary ({strategy})")
    lines.append("")
    lines.append(f"Model: {MODEL_NAME}")
    lines.append(f"Strategy: {strategy}")
    lines.append(f"Status: {status}")
    lines.append("")
    if metrics:
        lines.append("## Metrics")
        for k in sorted(metrics.keys()):
            lines.append(f"- {k}: {metrics[k]}")
    else:
        lines.append("No metrics found. Ensure evaluation completed and outputs exist.")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_compare_md(strategy_status: Dict[str, str]) -> None:
    ensure_dir(SUMMARY_DIR)
    filename = os.path.join(SUMMARY_DIR, "summary_compare.md")
    lines = []
    lines.append(f"# HumanEvalPlus Summary Compare ({MODEL_NAME})")
    lines.append("")
    for strat in STRATEGIES:
        status = strategy_status.get(strat, "unknown")
        lines.append(f"- {strat}: {status}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Summarize HumanEvalPlus results")
    parser.add_argument("--model", type=str, default="QwenCoderTurbo", help="Model name for summary output directory")
    args = parser.parse_args()

    global MODEL_NAME, SUMMARY_DIR
    MODEL_NAME = args.model
    SUMMARY_DIR = os.path.join("final-results", MODEL_NAME, "HumanEvalPlus")

    ensure_dir(SUMMARY_DIR)
    strategy_status: Dict[str, str] = {}
    for strat in STRATEGIES:
        out_dir = os.path.join(RESULTS_BASE, strat)
        json_files = find_json_files(out_dir)
        metrics = {}
        status = "pending"

        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                file_metrics = extract_metrics(data)
                if file_metrics:
                    metrics.update(file_metrics)
                    status = "completed"
            except Exception:
                continue

        write_summary_md(strat, metrics, status)
        strategy_status[strat] = status

    write_compare_md(strategy_status)


if __name__ == "__main__":
    main()