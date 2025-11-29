import os
import re
from typing import Dict, List, Tuple

# Reuse summarize from summarize_merged.py
try:
    from summarize_merged import summarize
except Exception:
    import importlib
    summarize = importlib.import_module('scripts.summarize_merged').summarize


DATASETS = ['APPS', 'CC', 'HumanEval', 'XCode', 'MBPP']
ET_DATASET = 'HumanEvalET'
STRATEGY_ORDER = ['Analogical', 'CoT', 'Direct', 'MapCoder', 'SelfPlanning']


def merged_path(model: str, dataset: str, strategy: str, results_root: str) -> str:
    name = f"{model}-{strategy}-{dataset}-Python3-0.0-1-merged.jsonl"
    return os.path.join(results_root, dataset, name)


def find_et_path(model: str, strategy: str, results_root: str) -> str:
    # Prefer ET subdir; fallback to results/HumanEval
    candidates = [
        os.path.join(results_root, 'HumanEval', 'ET', f"{model}-{strategy}-{ET_DATASET}-Python3-0.0-1.jsonl"),
        os.path.join(results_root, 'HumanEval', f"{model}-{strategy}-{ET_DATASET}-Python3-0.0-1.jsonl"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ''


def _read_summary_metrics(model: str, dataset: str, strategy: str, out_root: str):
    base_dir = os.path.join(out_root, model, dataset)
    candidates = [
        os.path.join(base_dir, f"{strategy}-summary.md"),
        os.path.join(base_dir, f"summary_{strategy}.md"),
        os.path.join(base_dir, f"summary-{strategy}.md"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as fp:
                    text = fp.read()
                total_m = re.search(r"Total problems:\s*(\d+)", text)
                solved_m = re.search(r"Solved:\s*(\d+)", text)
                rate_m = re.search(r"Pass rate:\s*([0-9.]+)%", text)
                if total_m and solved_m and rate_m:
                    return {
                        'total': int(total_m.group(1)),
                        'solved': int(solved_m.group(1)),
                        'pass_rate': float(rate_m.group(1)),
                        'file': p,
                    }
            except Exception:
                pass
    return None


def collect_metrics_for_model(model: str, results_root: str, out_root: str) -> Dict[str, Dict[str, dict]]:
    metrics: Dict[str, Dict[str, dict]] = {}
    # Regular datasets
    for ds in DATASETS:
        for st in STRATEGY_ORDER:
            # Prefer final-results per-strategy summary as the canonical source.
            sm = _read_summary_metrics(model, ds, st, out_root)
            if sm:
                metrics.setdefault(ds, {})[st] = sm
                continue

            # Fallback to summarizing merged jsonl if summary is missing.
            path = merged_path(model, ds, st, results_root)
            if os.path.exists(path):
                try:
                    total, solved, rate = summarize(path, None)
                    metrics.setdefault(ds, {})[st] = {
                        'total': total,
                        'solved': solved,
                        'pass_rate': rate,
                        'file': path,
                    }
                except Exception:
                    # If summarize fails, skip; no summary to fall back to.
                    pass

    # HumanEvalET
    ds = ET_DATASET
    for st in STRATEGY_ORDER:
        path = find_et_path(model, st, results_root)
        if not path:
            continue
        # summarize ET jsonl (non-merged single file)
        try:
            total, solved, rate = summarize(path, None)
        except Exception:
            continue
        metrics.setdefault(ds, {})[st] = {
            'total': total,
            'solved': solved,
            'pass_rate': rate,
            'file': path,
        }
    return metrics


def write_model_overview(model: str, metrics_by_dataset: Dict[str, Dict[str, dict]], out_root: str):
    out_dir = os.path.join(out_root, model)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'summary_overview.md')

    lines: List[str] = []
    lines.append(f"# {model} Final Results Overview")
    for ds in ['APPS', 'CC', 'HumanEval', 'XCode', 'MBPP', ET_DATASET]:
        if ds not in metrics_by_dataset:
            continue
        lines.append(f"\n## {ds}" if ds != 'CC' else "\n## CodeContest (CC)")
        for st in STRATEGY_ORDER:
            m = metrics_by_dataset[ds].get(st)
            if not m:
                continue
            file_field = 'merged' if ds != ET_DATASET else 'file'
            merged_rel = m['file'].replace('\\', '/').replace(os.getcwd().replace('\\', '/'), '').lstrip('/')
            if ds == ET_DATASET:
                lines.append(f"- Strategy: `{st}` — total `{m['total']}`, solved `{m['solved']}`, pass rate `{m['pass_rate']:.2f}%` (file: `{merged_rel}`)")
            else:
                lines.append(f"- Strategy: `{st}` — total `{m['total']}`, solved `{m['solved']}`, pass rate `{m['pass_rate']:.2f}%` (merged: `{merged_rel}`)")

    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(lines) + '\n')
    print(f"Wrote: {out_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate model-level overview pages across datasets and ET')
    parser.add_argument('--models', nargs='+', default=['QwenCoderTurbo', 'QwenCoder480b'])
    parser.add_argument('--results_root', default=os.path.join(os.getcwd(), 'results'))
    parser.add_argument('--out_root', default=os.path.join(os.getcwd(), 'final-results'))
    args = parser.parse_args()

    for model in args.models:
        metrics = collect_metrics_for_model(model, args.results_root, args.out_root)
        write_model_overview(model, metrics, args.out_root)


if __name__ == '__main__':
    main()