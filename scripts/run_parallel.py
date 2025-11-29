import argparse
import math
import os
import sys
import shutil
import subprocess
from datetime import datetime


def resolve_python_exe(explicit: str | None = None) -> list[str]:
    """
    Resolve a Python interpreter command.
    Returns a list suitable for Popen, e.g. ["python"] or ["py", "-3"].
    """
    if explicit:
        return [explicit]
    if shutil.which("python"):
        return ["python"]
    if shutil.which("py"):
        return ["py", "-3"]
    raise RuntimeError("No Python interpreter found on PATH (python/py).")


def compute_slices(total: int, processes: int, start: int | None, end: int | None):
    start = 0 if start is None else max(0, start)
    end = total if end is None else min(total, end)
    if end <= start:
        raise ValueError(f"Invalid slice range: start={start} end={end}")

    n = end - start
    chunk = math.ceil(n / processes)
    slices = []
    cur = start
    i = 0
    while cur < end:
        nxt = min(cur + chunk, end)
        slices.append((cur, nxt, i + 1))
        cur = nxt
        i += 1
    return slices


def main():
    parser = argparse.ArgumentParser(description="Parallel runner for MapCoder")
    parser.add_argument("--dataset", type=str, default="HumanEval")
    parser.add_argument("--strategy", type=str, default="MapCoder")
    parser.add_argument("--model", type=str, default="GPT4")
    parser.add_argument("--language", type=str, default="Python3")
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--pass_at_k", type=int, default=1)
    parser.add_argument("--processes", type=int, default=4)
    parser.add_argument("--quiet", action="store_true", help="Pass --quiet to child runs to reduce logging")
    parser.add_argument("--start-index", type=int, default=None)
    parser.add_argument("--end-index", type=int, default=None)
    parser.add_argument("--python-exe", type=str, default=None, help="Explicit python executable, e.g. C\\Python311\\python.exe")
    parser.add_argument("--logs-prefix", type=str, default="output_", help="Log file prefix, e.g. output_")
    parser.add_argument("--discard-previous-run", action="store_true", help="Discard existing shard result files before starting")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_path = os.path.join(repo_root, "src")
    sys.path.insert(0, src_path)

    # Load dataset to determine total size
    try:
        from datasets.DatasetFactory import DatasetFactory
        dataset_cls = DatasetFactory.get_dataset_class(args.dataset)
        dataset = dataset_cls()
        total = len(dataset.data)
    except Exception as e:
        raise RuntimeError(f"Failed to load dataset '{args.dataset}': {e}")

    slices = compute_slices(total, args.processes, args.start_index, args.end_index)
    py_cmd = resolve_python_exe(args.python_exe)

    print(f"Starting parallel run: {args.model}-{args.strategy}-{args.dataset}-{args.language}\n"
          f"Time: {datetime.now()}\n"
          f"Total samples: {total}, processes: {args.processes}, slices: {len(slices)}")

    processes = []
    for start, end, idx in slices:
        log_name = f"{args.logs_prefix}{idx}.log"
        log_path = os.path.join(repo_root, log_name)
        cmd = py_cmd + [
            os.path.join(repo_root, "src", "main.py"),
            "--dataset", args.dataset,
            "--strategy", args.strategy,
            "--model", args.model,
            "--language", args.language,
            "--temperature", str(args.temperature),
            "--pass_at_k", str(args.pass_at_k),
            "--start-index", str(start),
            "--end-index", str(end),
            "--results-suffix", f"p{idx}",
        ]
        if args.quiet:
            cmd.append("--quiet")
        if args.discard_previous_run:
            cmd.append("--discard-previous-run")

        print(f"Launching process {idx}: range [{start}, {end}) -> {log_name}")
        log_fp = open(log_path, "w", encoding="utf-8")
        p = subprocess.Popen(cmd, stdout=log_fp, stderr=log_fp, cwd=repo_root)
        processes.append((p, log_fp, log_name))

    # Wait for all processes
    failures = []
    for p, log_fp, log_name in processes:
        rc = p.wait()
        log_fp.close()
        if rc != 0:
            failures.append((log_name, rc))

    if failures:
        print("Some processes failed:")
        for log_name, rc in failures:
            print(f" - {log_name}: exit code {rc}")
        sys.exit(1)

    print("All processes completed successfully.")


if __name__ == "__main__":
    main()