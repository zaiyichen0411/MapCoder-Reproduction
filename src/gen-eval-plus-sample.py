from utils.jsonl import read_jsonl, write_jsonl
from utils.parse import parse_response
import argparse
import os


def _ensure_typing_header(code: str) -> str:
    code = code or ""
    if "from typing import *" not in code:
        return "from typing import *\n" + code
    return code


def generate_ep_dataset_humaneval(normal_results_path: str, ep_samples_path: str):
    samples = []
    results = read_jsonl(normal_results_path)
    for result in results:
        completion = ""
        try:
            if isinstance(result.get("source_codes"), list) and result["source_codes"]:
                completion = result["source_codes"][-1]
        except Exception:
            completion = ""

        if not completion:
            # Fallback to parsing the latest response
            responses = result.get("responses", [])
            if isinstance(responses, list) and responses:
                completion = parse_response(responses[-1])

        completion = _ensure_typing_header(completion)

        samples.append({
            "task_id": result.get("task_id"),
            "solution": completion,
        })

    write_jsonl(ep_samples_path, samples)


MBPP_EXCLUDE = set([
    "Mbpp/304", "Mbpp/393", "Mbpp/399", "Mbpp/401", "Mbpp/408",
    "Mbpp/411", "Mbpp/417", "Mbpp/434", "Mbpp/443", "Mbpp/444",
    "Mbpp/452", "Mbpp/464", "Mbpp/584", "Mbpp/617", "Mbpp/625",
    "Mbpp/627", "Mbpp/738", "Mbpp/747", "Mbpp/756", "Mbpp/776",
    "Mbpp/802", "Mbpp/228", "Mbpp/291",
])


def generate_ep_dataset_mbpp(normal_results_path: str, ep_samples_path: str):
    samples = []
    results = read_jsonl(normal_results_path)
    for result in results:
        completion = ""
        try:
            if isinstance(result.get("source_codes"), list) and result["source_codes"]:
                completion = result["source_codes"][-1]
        except Exception:
            completion = ""

        if not completion:
            responses = result.get("responses", [])
            if isinstance(responses, list) and responses:
                completion = parse_response(responses[-1])

        # Derive task_id from name (e.g., Mbpp/304)
        name = result.get("name", "")
        try:
            task_id = "Mbpp/" + name.split("_")[1]
        except Exception:
            # Fallback: require explicit task_id if name is missing
            task_id = result.get("task_id")

        if task_id in MBPP_EXCLUDE:
            continue

        completion = _ensure_typing_header(completion)
        samples.append({
            "task_id": task_id,
            "solution": completion,
        })

    write_jsonl(ep_samples_path, samples)


def main():
    parser = argparse.ArgumentParser(description="Generate EvalPlus samples from normal result JSONL.")
    parser.add_argument("--dataset", choices=["human", "mbpp"], required=True, help="Target dataset type")
    parser.add_argument("--in", dest="input_path", required=True, help="Normal results JSONL path")
    parser.add_argument("--out", dest="output_path", required=True, help="EvalPlus samples JSONL output path")

    args = parser.parse_args()

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(args.output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if args.dataset == "human":
        generate_ep_dataset_humaneval(args.input_path, args.output_path)
    else:
        generate_ep_dataset_mbpp(args.input_path, args.output_path)


if __name__ == "__main__":
    main()
