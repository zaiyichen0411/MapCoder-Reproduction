import os
import json
import argparse


def count_file(fp: str):
    solved = 0
    total = 0
    with open(fp, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            total += 1
            try:
                obj = json.loads(ln)
                if obj.get('is_solved', False):
                    solved += 1
            except Exception:
                # Ignore malformed lines
                pass
    return solved, total


def fmt_rate(solved: int, total: int) -> str:
    if total == 0:
        return "0.00%"
    return f"{solved/total*100:.2f}%"


def build_markdown(metrics: dict) -> str:
    lines = ["# HumanEvalET Summary Compare", ""]
    # Include Direct to align with five-strategy requirement
    order = ["Analogical", "CoT", "Direct", "MapCoder", "SelfPlanning"]
    for strat in order:
        m = metrics.get(strat, {})
        lines.append(f"- Strategy: `{strat}`")
        lines.append(f"- Total problems: `{m.get('total', 0)}`")
        lines.append(f"- Solved: `{m.get('solved', 0)}`")
        lines.append(f"- Pass rate: `{m.get('rate', '0.00%')}`")
        lines.append(f"- Result file: `{m.get('file', '')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize HumanEvalET metrics into markdown compare page")
    parser.add_argument("--model", type=str, default="QwenCoderTurbo", help="Model name, e.g., QwenCoderTurbo or QwenCoder480b")
    parser.add_argument("--results_dir", type=str, default=os.path.join("results", "HumanEval", "ET"))
    parser.add_argument("--out_dir", type=str, default=None, help="Output dir under final-results/<model>/HumanEvalET")
    args = parser.parse_args()

    base_dir = args.results_dir
    model = args.model
    files = {
        "Analogical": os.path.join(base_dir, f"{model}-Analogical-HumanEvalET-Python3-0.0-1.jsonl"),
        "CoT": os.path.join(base_dir, f"{model}-CoT-HumanEvalET-Python3-0.0-1.jsonl"),
        "Direct": os.path.join(base_dir, f"{model}-Direct-HumanEvalET-Python3-0.0-1.jsonl"),
        "MapCoder": os.path.join(base_dir, f"{model}-MapCoder-HumanEvalET-Python3-0.0-1.jsonl"),
        "SelfPlanning": os.path.join(base_dir, f"{model}-SelfPlanning-HumanEvalET-Python3-0.0-1.jsonl"),
    }

    metrics = {}
    for strat, fp in files.items():
        if not os.path.exists(fp):
            solved, total, rate = 0, 0, "0.00%"
        else:
            solved, total = count_file(fp)
            rate = fmt_rate(solved, total)
        metrics[strat] = {"solved": solved, "total": total, "rate": rate, "file": fp.replace("/", "\\")}

    md = build_markdown(metrics)

    out_dir = args.out_dir or os.path.join("final-results", model, "HumanEvalET")
    os.makedirs(out_dir, exist_ok=True)
    out_fp = os.path.join(out_dir, "summary_compare.md")
    with open(out_fp, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote: {out_fp}")


if __name__ == "__main__":
    main()