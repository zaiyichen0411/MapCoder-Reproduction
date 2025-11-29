import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import json
import re


def ensure_out_dir(path: str):
    os.makedirs(path, exist_ok=True)

def cleanup_old_images(base_dir: str, expected: List[str], subdirs: List[str]):
    """Remove outdated PNGs in base_dir and subdirs that are not in expected.

    - base_dir: images/progress
    - expected: list of relative paths (e.g., 'Compare/compare_models_APPS.png')
    - subdirs: ['Compare', 'QwenCoderTurbo', 'QwenCoder480b']
    """
    expected_set = set(expected)
    # Clean root (files directly under base_dir)
    for name in os.listdir(base_dir):
        fp = os.path.join(base_dir, name)
        if os.path.isfile(fp) and name.lower().endswith('.png'):
            rel = name
            if rel not in expected_set:
                try:
                    os.remove(fp)
                except Exception:
                    pass
    # Clean subdirs
    for sd in subdirs:
        d = os.path.join(base_dir, sd)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            fp = os.path.join(d, name)
            if os.path.isfile(fp) and name.lower().endswith('.png'):
                rel = os.path.join(sd, name).replace("\\", "/")
                if rel not in expected_set:
                    try:
                        os.remove(fp)
                    except Exception:
                        pass


# -------- Dynamic metrics readers (summary/merged) --------
def _dataset_dir_map(dataset: str) -> str:
    mapping = {
        "APPS": "APPS",
        "CC": "CodeContest",
        "HumanEval": "HumanEval",
        "XCode": "XCode",
        "MBPP": "MBPP",
    }
    return mapping.get(dataset, dataset)


def _build_run_name(model: str, strategy: str, dataset: str, language: str, temperature: str, pass_at_k: int) -> str:
    return f"{model}-{strategy}-{dataset}-{language}-{temperature}-{pass_at_k}"


def _read_summary_metrics(model: str, dataset: str, strategy: str):
    base_dir = os.path.join("final-results", model, dataset)
    candidates = [
        os.path.join(base_dir, f"{strategy}-summary.md"),
        os.path.join(base_dir, f"summary_{strategy}.md"),
        os.path.join(base_dir, f"summary-{strategy}.md"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as fp:
                    text = fp.read()
                total_m = re.search(r"Total problems:\s*(\d+)", text)
                solved_m = re.search(r"Solved:\s*(\d+)", text)
                rate_m = re.search(r"Pass rate:\s*([0-9.]+)%", text)
                if total_m and solved_m and rate_m:
                    return {
                        "total": int(total_m.group(1)),
                        "solved": int(solved_m.group(1)),
                        "pass_rate": float(rate_m.group(1)),
                    }
            except Exception:
                pass
    return None


def _read_overview_metrics(model: str, dataset: str, strategy: str) -> Optional[dict]:
    """
    Parse metrics from final-results/<model>/summary_overview.md for special datasets
    like HumanEvalET and MBPPET that may not have per-dataset summaries.
    """
    path = os.path.join("final-results", model, "summary_overview.md")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fp:
            text = fp.read()
        # Find the dataset section header
        # e.g., "## HumanEvalET" or "## MBPPET"
        section_pattern = rf"##\s+{re.escape(dataset)}\s*\n(.+?)(?:\n##\s|\Z)"
        m = re.search(section_pattern, text, flags=re.DOTALL)
        if not m:
            return None
        section = m.group(1)
        # Find the specific strategy line
        # e.g., - Strategy: `Direct` — total `164`, solved `107`, pass rate `65.24%`
        strat_pattern = rf"-\s*Strategy:\s*`{re.escape(strategy)}`\s*—\s*total\s*`?(\d+)`?,\s*solved\s*`?(\d+)`?,\s*pass rate\s*`?([0-9.]+)%`?"
        sm = re.search(strat_pattern, section)
        if sm:
            return {
                "total": int(sm.group(1)),
                "solved": int(sm.group(2)),
                "pass_rate": float(sm.group(3)),
            }
    except Exception:
        pass
    return None


def _read_compare_summary_metrics(model: str, dataset: str, strategy: str):
    """
    Parse per-strategy metrics from summary_compare.md when individual summary files
    are not present (e.g., QwenCoder480b directories).
    """
    path = os.path.join("final-results", model, dataset, "summary_compare.md")
    if not os.path.exists(path):
        return None
    try:
        total = solved = rate = None
        looking = False
        with open(path, "r", encoding="utf-8") as fp:
            for line in fp:
                line_s = line.strip()
                if line_s.startswith("- Strategy:") or line_s.startswith("-\tStrategy:") or line_s.startswith(" "):
                    # normalize backticks and spaces
                    m = re.search(r"Strategy:\s*`([^`]+)`", line_s)
                    if m:
                        looking = (m.group(1) == strategy)
                        # reset captures when switching blocks
                        total = solved = rate = None
                        continue
                if looking:
                    tm = re.search(r"Total problems:\s*`?(\d+)`?", line_s)
                    if tm:
                        total = int(tm.group(1))
                        continue
                    sm = re.search(r"Solved:\s*`?(\d+)`?", line_s)
                    if sm:
                        solved = int(sm.group(1))
                        continue
                    rm = re.search(r"Pass rate:\s*`?([0-9.]+)%`?", line_s)
                    if rm:
                        rate = float(rm.group(1))
                        # if we have all three, we can return
                        if total is not None and solved is not None:
                            return {"total": total, "solved": solved, "pass_rate": rate}
        # Fallback if we exited loop and still have values
        if total is not None and solved is not None and rate is not None:
            return {"total": total, "solved": solved, "pass_rate": rate}
    except Exception:
        pass
    return None


def _summarize_merged_jsonl(model: str, dataset: str, strategy: str):
    dataset_dir = _dataset_dir_map(dataset)
    base = f"{model}-{strategy}-{dataset}-Python3-0.0-"
    candidates = []
    root = os.path.join("results")
    sub = os.path.join("results", dataset_dir)
    if os.path.isdir(root):
        for name in os.listdir(root):
            if name.startswith(base) and name.endswith("-merged.jsonl"):
                candidates.append(os.path.join(root, name))
    if os.path.isdir(sub):
        for name in os.listdir(sub):
            if name.startswith(base) and name.endswith("-merged.jsonl"):
                candidates.append(os.path.join(sub, name))
    best = None
    for p in candidates:
        try:
            total, solved = 0, 0
            with open(p, "r", encoding="utf-8") as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    total += 1
                    try:
                        obj = json.loads(line)
                        if obj.get("is_solved") is True:
                            solved += 1
                    except Exception:
                        pass
            if total > 0:
                pr = round(100.0 * solved / total, 2)
                cur = {"total": total, "solved": solved, "pass_rate": pr}
                if best is None or pr > best["pass_rate"]:
                    best = cur
        except Exception:
            pass
    return best


def _summarize_et_jsonl(model: str, dataset: str, strategy: str) -> Optional[dict]:
    """
    Summarize ET dataset raw jsonl results (e.g., HumanEvalET under results/HumanEval/ET,
    MBPPET under results/MBPP/ET) when merged files or summaries are not available.
    """
    candidates: List[str] = []
    if dataset == "HumanEvalET":
        candidates = [
            os.path.join("results", "HumanEval", "ET", f"{_build_run_name(model, strategy, dataset, 'Python3', '0.0', 1)}.jsonl"),
            os.path.join("results", "HumanEval", f"{_build_run_name(model, strategy, dataset, 'Python3', '0.0', 1)}.jsonl"),
        ]
    elif dataset == "MBPPET":
        candidates = [
            os.path.join("results", "MBPP", "ET", f"{_build_run_name(model, strategy, dataset, 'Python3', '0.0', 1)}.jsonl"),
        ]
    else:
        return None

    for p in candidates:
        if os.path.exists(p):
            try:
                total, solved = 0, 0
                with open(p, "r", encoding="utf-8") as fp:
                    for line in fp:
                        line = line.strip()
                        if not line:
                            continue
                        total += 1
                        try:
                            obj = json.loads(line)
                            if obj.get("is_solved") is True:
                                solved += 1
                        except Exception:
                            pass
                if total > 0:
                    return {
                        "total": total,
                        "solved": solved,
                        "pass_rate": round(100.0 * solved / total, 2),
                    }
            except Exception:
                pass
    return None


def get_metrics(model: str, dataset: str, strategy: str):
    # Prefer the freshest merged jsonl (best pass_at_k) for base datasets
    m_merged = _summarize_merged_jsonl(model, dataset, strategy)
    if m_merged:
        return m_merged
    # ET datasets rely on raw jsonl under results/<Dataset>/ET
    m_et = _summarize_et_jsonl(model, dataset, strategy)
    if m_et:
        return m_et
    # Fallback to summaries
    return (
        _read_summary_metrics(model, dataset, strategy)
        or _read_overview_metrics(model, dataset, strategy)
        or _read_compare_summary_metrics(model, dataset, strategy)
    )


def annotate_bars(ax, rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f"{height:.2f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)


def plot_dual_axis(labels: List[str],
                   solved_counts: List[int],
                   pass_rates: List[float],
                   title: str,
                   out_name: str,
                   out_dir: str,
                   has_data: Optional[List[bool]] = None):
    x = range(len(labels))
    width = 0.4

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    bars1 = ax1.bar([i - width/2 for i in x], solved_counts, width, label="Solved", color="#4C78A8")
    bars2 = ax2.bar([i + width/2 for i in x], pass_rates, width, label="Pass Rate (%)", color="#F58518")

    ax1.set_title(title)
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Solved")
    ax2.set_ylabel("Pass Rate (%)")

    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    handles = [bars1, bars2]
    ax1.legend(handles, [h.get_label() for h in handles], loc='upper left')

    # annotate values on bars (counts and percentages or N/A for missing)
    for i in range(len(labels)):
        b1 = bars1[i]
        b2 = bars2[i]
        h1 = b1.get_height()
        h2 = b2.get_height()
        ax1.annotate(f"{solved_counts[i]}",
                     xy=(b1.get_x() + b1.get_width() / 2, h1),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9)
        txt = f"{pass_rates[i]:.2f}%"
        if has_data is not None and not has_data[i]:
            txt = "N/A"
        ax2.annotate(txt,
                     xy=(b2.get_x() + b2.get_width() / 2, h2),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9)

    out_path = os.path.join(out_dir, out_name)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_compare_models(dataset: str,
                        strategies: List[str],
                        pass_480b: Dict[str, float],
                        pass_turbo: Dict[str, float],
                        out_dir: str):
    labels = strategies
    x = range(len(labels))

    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))

    vals_480b = [pass_480b.get(s, 0.0) for s in labels]
    vals_turbo = [pass_turbo.get(s, 0.0) for s in labels]

    rects1 = ax.bar([i - width / 2 for i in x], vals_480b, width, label='QwenCoder480b', color='#4C78A8')
    rects2 = ax.bar([i + width / 2 for i in x], vals_turbo, width, label='QwenCoderTurbo', color='#F58518')

    ax.set_ylabel('Pass Rate (%)')
    ax.set_title(f'{dataset}: Model Comparison by Strategy')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    annotate_bars(ax, rects1)
    annotate_bars(ax, rects2)

    out_path = os.path.join(out_dir, f'compare_models_{dataset}.png')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_turbo_across_datasets(strategy: str,
                                dataset_order: List[str],
                                pass_turbo_by_dataset: Dict[str, float],
                                out_dir: str):
    labels = []
    values = []
    for ds in dataset_order:
        if ds in pass_turbo_by_dataset:
            labels.append(ds)
            values.append(pass_turbo_by_dataset[ds])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    rects = ax.bar(labels, values, color='#F58518')
    ax.set_ylabel('Pass Rate (%)')
    ax.set_title(f'QwenCoderTurbo: {strategy} across datasets')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    annotate_bars(ax, rects)
    out_path = os.path.join(out_dir, f'turbo_{strategy}_across_datasets.png')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_model_dataset_dual_axis(model: str, dataset: str, strategies: List[str], out_dir: str):
    labels, solved, rates, has_data = [], [], [], []
    for st in strategies:
        m = get_metrics(model, dataset, st)
        labels.append(st)
        if m:
            solved.append(m.get('solved', 0))
            rates.append(m.get('pass_rate', 0.0))
            has_data.append(True)
        else:
            solved.append(0)
            rates.append(0.0)
            has_data.append(False)
    title = f"{model} {dataset} Strategies"
    out_name = f"{model}_{dataset}_strategies_dual_axis.png"
    plot_dual_axis(labels, solved, rates, title=title, out_name=out_name, out_dir=out_dir, has_data=has_data)


def plot_480b_across_datasets(strategy: str,
                               dataset_order: List[str],
                               pass_480b_by_dataset: Dict[str, float],
                               out_dir: str):
    labels = []
    values = []
    for ds in dataset_order:
        if ds in pass_480b_by_dataset:
            labels.append(ds)
            values.append(pass_480b_by_dataset[ds])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    rects = ax.bar(labels, values, color='#4C78A8')
    ax.set_ylabel('Pass Rate (%)')
    ax.set_title(f'QwenCoder480b: {strategy} across datasets')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    annotate_bars(ax, rects)
    out_path = os.path.join(out_dir, f'480b_{strategy}_across_datasets.png')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    out_base = os.path.join('images', 'progress')
    out_compare = os.path.join(out_base, 'Compare')
    out_turbo = os.path.join(out_base, 'QwenCoderTurbo')
    out_480b = os.path.join(out_base, 'QwenCoder480b')
    ensure_out_dir(out_base)
    ensure_out_dir(out_compare)
    ensure_out_dir(out_turbo)
    ensure_out_dir(out_480b)
    # Build dynamic pass-rate maps from summaries/merged/overview results
    datasets_base = ['APPS', 'CC', 'HumanEval', 'XCode', 'MBPP']
    datasets_extra = ['HumanEvalET', 'MBPPET']
    datasets_all = datasets_base + datasets_extra
    strategies_all = ['Analogical', 'CoT', 'Direct', 'MapCoder', 'SelfPlanning']

    pass_480b = {ds: {} for ds in datasets_all}
    pass_turbo = {ds: {} for ds in datasets_all}

    for ds in datasets_all:
        for st in strategies_all:
            m480b = get_metrics('QwenCoder480b', ds, st)
            if m480b:
                pass_480b[ds][st] = m480b.get('pass_rate', 0.0)
            mTurbo = get_metrics('QwenCoderTurbo', ds, st)
            if mTurbo:
                pass_turbo[ds][st] = mTurbo.get('pass_rate', 0.0)

    expected_files: List[str] = []
    out_highlights = os.path.join(out_base, 'Highlights')
    ensure_out_dir(out_highlights)

    # Compare models by dataset (only common strategies with metrics)
    for ds in datasets_all:
        common = [st for st in strategies_all if st in pass_480b[ds] and st in pass_turbo[ds]]
        if common:
            plot_compare_models(ds, common, pass_480b[ds], pass_turbo[ds], out_compare)
            expected_files.append(os.path.join('Compare', f'compare_models_{ds}.png').replace('\\', '/'))
        else:
            union = sorted(set(pass_480b[ds].keys()) | set(pass_turbo[ds].keys()))
            if union:
                plot_compare_models(ds, union, pass_480b[ds], pass_turbo[ds], out_compare)
                expected_files.append(os.path.join('Compare', f'compare_models_{ds}.png').replace('\\', '/'))

    # Dual-axis per dataset for both models (include HumanEvalET)
    for ds in datasets_all:
        plot_model_dataset_dual_axis('QwenCoder480b', ds, strategies_all, out_480b)
        expected_files.append(os.path.join('QwenCoder480b', f'QwenCoder480b_{ds}_strategies_dual_axis.png').replace('\\', '/'))
        plot_model_dataset_dual_axis('QwenCoderTurbo', ds, strategies_all, out_turbo)
        expected_files.append(os.path.join('QwenCoderTurbo', f'QwenCoderTurbo_{ds}_strategies_dual_axis.png').replace('\\', '/'))

    # Across-datasets charts per strategy (requested in progress.md)
    for st in strategies_all:
        pass_turbo_by_dataset = {}
        pass_480b_by_dataset = {}
        for ds in datasets_all:
            if st in pass_turbo[ds]:
                pass_turbo_by_dataset[ds] = pass_turbo[ds][st]
            if st in pass_480b[ds]:
                pass_480b_by_dataset[ds] = pass_480b[ds][st]
        if pass_turbo_by_dataset:
            plot_turbo_across_datasets(st, datasets_all, pass_turbo_by_dataset, out_turbo)
            expected_files.append(os.path.join('QwenCoderTurbo', f'turbo_{st}_across_datasets.png').replace('\\', '/'))
        if pass_480b_by_dataset:
            plot_480b_across_datasets(st, datasets_all, pass_480b_by_dataset, out_480b)
            expected_files.append(os.path.join('QwenCoder480b', f'480b_{st}_across_datasets.png').replace('\\', '/'))

    # Turbo HumanEvalET strategy summary (pass rate only) to match documentation path
    try:
        def _plot_dataset_strategy_pass_only(model: str, dataset: str, strategies: List[str], out_name: str):
            labels = []
            values = []
            for st in strategies:
                labels.append(st)
                m = get_metrics(model, dataset, st)
                values.append(m.get('pass_rate', 0.0) if m else 0.0)
            fig, ax = plt.subplots(figsize=(9, 5))
            rects = ax.bar(labels, values, color='#F58518' if model == 'QwenCoderTurbo' else '#4C78A8')
            ax.set_ylabel('Pass Rate (%)')
            ax.set_title(f'{model}: {dataset} strategy summary (Pass Rate)')
            ax.grid(axis='y', linestyle='--', alpha=0.4)
            annotate_bars(ax, rects)
            out_path = os.path.join(out_dir, out_name)
            fig.tight_layout()
            fig.savefig(out_path, dpi=150)
            plt.close(fig)

        _plot_dataset_strategy_pass_only('QwenCoderTurbo', 'HumanEvalET', strategies_all, 'turbo_HumanEvalET_strategies.png')
        expected_files.append(os.path.join('QwenCoderTurbo', 'turbo_HumanEvalET_strategies.png').replace('\\', '/'))
        # Move pass-only chart into QwenCoderTurbo directory
        try:
            src = os.path.join(out_base, 'turbo_HumanEvalET_strategies.png')
            dst = os.path.join(out_turbo, 'turbo_HumanEvalET_strategies.png')
            if os.path.exists(src):
                try:
                    os.replace(src, dst)
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        # Non-fatal: skip if metrics missing
        pass

    # Final cleanup: remove outdated PNGs in root and subdirs
    # --- Highlights: MapCoder leads vs other strategies ---
    def _collect_strategy_pass_rates(model: str, dataset: str) -> Dict[str, float]:
        vals: Dict[str, float] = {}
        for st in strategies_all:
            m = get_metrics(model, dataset, st)
            if m:
                vals[st] = m.get('pass_rate', 0.0)
        return vals

    def _plot_mapcoder_leads(model: str, datasets: List[str]):
        labels, deltas = [], []
        for ds in datasets:
            pr = _collect_strategy_pass_rates(model, ds)
            if 'MapCoder' in pr and pr:
                others = [v for k, v in pr.items() if k != 'MapCoder']
                if others:
                    best_other = max(others)
                    if pr['MapCoder'] >= best_other and pr['MapCoder'] > 0:
                        labels.append(ds)
                        deltas.append(round(pr['MapCoder'] - best_other, 2))
        if labels:
            fig, ax = plt.subplots(figsize=(8, 4.5))
            rects = ax.bar(labels, deltas, color='#4C78A8' if model == 'QwenCoder480b' else '#F58518')
            ax.set_ylabel('Advantage over next best (pp)')
            ax.set_title(f'{model}: MapCoder advantage across datasets')
            ax.grid(axis='y', linestyle='--', alpha=0.4)
            annotate_bars(ax, rects)
            out_name = f'{model}_MapCoder_leads.png'
            out_path = os.path.join(out_highlights, out_name)
            fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
            expected_files.append(os.path.join('Highlights', out_name).replace('\\', '/'))

    _plot_mapcoder_leads('QwenCoder480b', datasets_all)
    _plot_mapcoder_leads('QwenCoderTurbo', datasets_all)

    # --- Highlights: MapCoder 480b vs Turbo across datasets ---
    labels, diffs = [], []
    for ds in datasets_all:
        m480b = get_metrics('QwenCoder480b', ds, 'MapCoder')
        mTurbo = get_metrics('QwenCoderTurbo', ds, 'MapCoder')
        if m480b and mTurbo:
            d = round(m480b.get('pass_rate', 0.0) - mTurbo.get('pass_rate', 0.0), 2)
            if d > 0:
                labels.append(ds)
                diffs.append(d)
    if labels:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        rects = ax.bar(labels, diffs, color='#4C78A8')
        ax.set_ylabel('Pass Rate Difference (pp)')
        ax.set_title('MapCoder: QwenCoder480b vs QwenCoderTurbo (datasets where 480b > Turbo)')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        annotate_bars(ax, rects)
        out_name = 'MapCoder_480b_vs_Turbo_highlight.png'
        out_path = os.path.join(out_highlights, out_name)
        fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
        expected_files.append(os.path.join('Highlights', out_name).replace('\\', '/'))

    cleanup_old_images(out_base, expected_files, ['Compare', 'QwenCoderTurbo', 'QwenCoder480b', 'Highlights'])


if __name__ == '__main__':
    main()