import os
import re
from typing import Dict, List, Tuple

# We reuse the summarize logic from summarize_merged.py via local import
try:
    from summarize_merged import summarize
except Exception:
    # Minimal fallback if import path resolution differs when executed from IDE
    import importlib
    summarize = importlib.import_module('scripts.summarize_merged').summarize


DATASET_DIRS = ['APPS', 'CodeContest', 'HumanEval', 'XCode', 'MBPP']


def find_merged_files(dataset_dir: str) -> List[str]:
    files = []
    for name in os.listdir(dataset_dir):
        if name.endswith('-merged.jsonl'):
            files.append(os.path.join(dataset_dir, name))
    return sorted(files)


def parse_run_info(filename: str) -> Tuple[str, str, str]:
    base = os.path.basename(filename)
    # Example: QwenCoderTurbo-Direct-APPS-Python3-0.0-1-merged.jsonl
    m = re.match(r'(?P<model>QwenCoder(?:480b|Turbo))-(?P<strategy>[^-]+)-(?P<dataset>[^-]+)-', base)
    if not m:
        return 'UnknownModel', 'UnknownStrategy', 'UnknownDataset'
    return m.group('model'), m.group('strategy'), m.group('dataset')


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def write_overview_md(dataset_dir: str, dataset: str, metrics_by_model: Dict[str, Dict[str, dict]]):
    out_path = os.path.join(dataset_dir, 'summary_overview.md')
    lines: List[str] = []
    lines.append(f'# Results Overview — {dataset}\n')
    for model in sorted(metrics_by_model.keys()):
        lines.append(f'\n## {model}\n')
        # Order strategies consistently
        order = ['Analogical', 'CoT', 'Direct', 'MapCoder', 'SelfPlanning']
        for st in order:
            if st in metrics_by_model[model]:
                m = metrics_by_model[model][st]
                merged_rel = m['file'].replace('\\', '/').replace(os.getcwd().replace('\\', '/'), '').lstrip('/')
                lines.append(f"- Strategy: `{st}` — total `{m['total']}`, solved `{m['solved']}`, pass rate `{m['pass_rate']:.2f}%` (merged: `{merged_rel}`)")
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(lines) + '\n')


def write_compare_md(dataset_dir: str, dataset: str, metrics_by_model: Dict[str, Dict[str, dict]]):
    out_path = os.path.join(dataset_dir, 'summary_compare.md')
    lines: List[str] = []
    lines.append(f'# Compare Summary — {dataset}\n')
    order = ['Analogical', 'CoT', 'Direct', 'MapCoder', 'SelfPlanning']
    models = sorted(metrics_by_model.keys())
    for st in order:
        # include if any model has this strategy
        any_has = any(st in metrics_by_model.get(m, {}) for m in models)
        if not any_has:
            continue
        lines.append(f'\n- Strategy: `{st}`')
        for model in models:
            if st in metrics_by_model[model]:
                m = metrics_by_model[model][st]
                lines.append(f"  - {model}: total `{m['total']}`, solved `{m['solved']}`, pass rate `{m['pass_rate']:.2f}%`")
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(lines) + '\n')


def generate_dataset_summaries(results_root: str, dataset: str):
    dataset_dir = os.path.join(results_root, dataset)
    ensure_dir(dataset_dir)
    merged_files = find_merged_files(dataset_dir)
    metrics_by_model: Dict[str, Dict[str, dict]] = {}

    for f in merged_files:
        model, strategy, ds = parse_run_info(f)
        try:
            total, solved, pass_rate = summarize(f, None)
        except Exception:
            continue
        cur = metrics_by_model.setdefault(model, {}).get(strategy)
        if (cur is None) or (pass_rate > cur.get('pass_rate', 0.0)):
            metrics_by_model[model][strategy] = {
                'total': total,
                'solved': solved,
                'pass_rate': pass_rate,
                'file': f,
            }

    # Write summaries only if we have any metrics
    if metrics_by_model:
        write_overview_md(dataset_dir, dataset, metrics_by_model)
        write_compare_md(dataset_dir, dataset, metrics_by_model)


def main():
    results_root = os.path.join(os.getcwd(), 'results')
    for ds in DATASET_DIRS:
        generate_dataset_summaries(results_root, ds)


if __name__ == '__main__':
    main()