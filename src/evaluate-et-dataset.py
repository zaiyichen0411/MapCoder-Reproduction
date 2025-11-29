from utils.jsonl import read_jsonl, write_jsonl
from evaluations.func_evaluate import evaluate_io_et
from models.ModelFactory import ModelFactory
import re
import os
import argparse


def generate_et_dataset(
        NORMAL_RESULTS_PATH,
        ET_RESULTS_PATH,
        ET_DATA_PATH=".\\data\\HumanEval\\HumanEvalET.jsonl",
        repair_attempts: int = 0,
        repair_model: str = "QwenCoder480b",
        language: str = "Python3",
        timeout: int = 10,
):
    dataset = read_jsonl(ET_DATA_PATH)
    data_dict = {}
    for item in dataset:
        data_dict[item["task_id"]] = {"et_item": item}

    results = read_jsonl(NORMAL_RESULTS_PATH)
    for result in results:
        data_dict[result.get("task_id")]["result"] = result

    correct_count = 0
    et_results = []
    for key, value in data_dict.items():
        item = value["et_item"]
        result = value.get("result", None)
        if result is None:
            continue
        # Prefer the latest improved code when available; fall back to solution
        if isinstance(result.get("source_codes"), list) and result["source_codes"]:
            generated_code = result["source_codes"][-1]
        else:
            generated_code = result.get("solution", "")

        passed = evaluate_io_et(
            item['test_case_list'],
            generated_code,
            timeout=timeout,
            prompt=item["prompt"]
        )

        if passed:
            result["is_solved"] = True
            correct_count += 1
        else:
            # Optional one-step repair using model with tests context
            improved = False
            cur_code = generated_code
            if repair_attempts and item.get("prompt"):
                try:
                    model = ModelFactory.get_model_class(repair_model)(temperature=0.0)
                    for _ in range(max(0, int(repair_attempts))):
                        msgs = [
                            {
                                "role": "system",
                                "content": (
                                    "You are a debugging agent. Improve the given solution to satisfy extended tests. "
                                    "Return only the corrected code fenced in triple backticks with an explicit language tag."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Problem description:\n{item['prompt']}\n\n"
                                    f"Current code:\n{cur_code}\n\n"
                                    f"Extended tests:\n{item['test_case_list']}\n\n"
                                    f"Target language: {language}. Return only the improved solution inside a fenced code block."
                                )
                            }
                        ]
                        resp, _pt, _ct = model.prompt(msgs)
                        m = re.search(r"```[a-zA-Z0-9+#]*\n([\s\S]*?)```", resp)
                        if m:
                            cur_code = m.group(1).strip()
                        else:
                            cur_code = resp.strip()
                        ok = evaluate_io_et(item['test_case_list'], cur_code, timeout=timeout, prompt=item["prompt"])
                        if ok:
                            improved = True
                            break
                except Exception:
                    improved = False
            result["is_solved"] = bool(improved)
            if improved:
                sc = result.get("source_codes") or []
                if not isinstance(sc, list):
                    sc = [str(sc)]
                sc.append(cur_code)
                result["source_codes"] = sc

        et_results.append(result)
        print(
            f"Accuracy: {correct_count}/{len(et_results)} = {correct_count/len(et_results):.2f}")
    # write_jsonl(ET_RESULTS_PATH, et_results)

    et_results = sorted(
        et_results,
        key=lambda x: int(x["task_id"].split('/')[-1])
    )

    write_jsonl(ET_RESULTS_PATH, et_results)
    print(
        f"Accuracy: {correct_count}/{len(et_results)} = {correct_count/len(et_results):.2f}")


def generate_et_dataset_mbpp(
        NORMAL_RESULTS_PATH,
        ET_RESULTS_PATH,
        ET_DATA_PATH=".\\data\\MBPPEval\\MBPP_ET.jsonl",
        repair_attempts: int = 0,
        repair_model: str = "QwenCoder480b",
        language: str = "Python3",
        timeout: int = 10,
):
    dataset = read_jsonl(ET_DATA_PATH)
    data_dict = {}
    for item in dataset:
        data_dict[item["task_id"]] = {"et_item": item}

    results = read_jsonl(NORMAL_RESULTS_PATH)
    for result in results:
        task_id = int(result["name"].split("_")[1])
        data_dict[task_id]["result"] = result

    correct_count = 0
    et_results = []
    for key, value in data_dict.items():
        item = value["et_item"]
        result = value.get("result", None)
        if result is None:
            continue

        # Prefer the latest improved code when available; fall back to solution
        if isinstance(result.get("source_codes"), list) and result["source_codes"]:
            generated_code = result["source_codes"][-1]
        else:
            generated_code = result.get("solution", "")

        passed = evaluate_io_et(
            item['test_list'],
            generated_code,
            timeout=timeout
        )

        if passed:
            result["is_solved"] = True
            correct_count += 1
        else:
            improved = False
            cur_code = generated_code
            if repair_attempts:
                try:
                    model = ModelFactory.get_model_class(repair_model)(temperature=0.0)
                    for _ in range(max(0, int(repair_attempts))):
                        msgs = [
                            {
                                "role": "system",
                                "content": (
                                    "You are a debugging agent. Improve the given solution to satisfy extended tests. "
                                    "Return only the corrected code fenced in triple backticks with an explicit language tag."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Current code:\n{cur_code}\n\n"
                                    f"Extended tests:\n{item['test_list']}\n\n"
                                    f"Target language: {language}. Return only the improved solution inside a fenced code block."
                                )
                            }
                        ]
                        resp, _pt, _ct = model.prompt(msgs)
                        m = re.search(r"```[a-zA-Z0-9+#]*\n([\s\S]*?)```", resp)
                        if m:
                            cur_code = m.group(1).strip()
                        else:
                            cur_code = resp.strip()
                        ok = evaluate_io_et(item['test_list'], cur_code, timeout=timeout)
                        if ok:
                            improved = True
                            break
                except Exception:
                    improved = False
            result["is_solved"] = bool(improved)
            if improved:
                sc = result.get("source_codes") or []
                if not isinstance(sc, list):
                    sc = [str(sc)]
                sc.append(cur_code)
                result["source_codes"] = sc

        et_results.append(result)
        print(
            f"Accuracy: {correct_count}/{len(et_results)} = {correct_count/len(et_results):.2f}")
    # write_jsonl(ET_RESULTS_PATH, et_results)

    et_results = sorted(
        et_results,
        key=lambda x: int(x["name"].split("_")[1])
    )

    write_jsonl(ET_RESULTS_PATH, et_results)
    print(
        f"Accuracy: {correct_count}/{len(et_results)} = {correct_count/len(et_results):.2f}")

def _build_run_name(model: str, strategy: str, dataset: str, language: str, temperature: str, pass_at_k: int) -> str:
    try:
        t = float(temperature)
        temperature = f"{t:.1f}"
    except Exception:
        temperature = str(temperature)
    return f"{model}-{strategy}-{dataset}-{language}-{temperature}-{pass_at_k}"


def _find_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description="Generate ET (extended tests) results from normal results")
    parser.add_argument("--dataset", type=str, choices=["HumanEvalET", "MBPPET"], required=True)
    parser.add_argument("--strategy", type=str, required=True)
    parser.add_argument("--model", type=str, default="QwenCoderTurbo")
    parser.add_argument("--language", type=str, default="Python3")
    parser.add_argument("--temperature", type=str, default="0.0")
    parser.add_argument("--pass_at_k", type=int, default=1)
    parser.add_argument("--repair_attempts", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument("--normal_results_path", type=str, default=None)
    parser.add_argument("--et_results_path", type=str, default=None)
    parser.add_argument("--et_data_path", type=str, default=None)

    args = parser.parse_args()

    # Determine dataset specifics
    if args.dataset == "HumanEvalET":
        normal_dataset = "HumanEval"
        et_dir = os.path.join(args.results_dir, normal_dataset, "ET")
        et_data_path = args.et_data_path or ".\\data\\HumanEval\\HumanEvalET.jsonl"
    else:  # MBPPET
        normal_dataset = "MBPP"
        et_dir = os.path.join(args.results_dir, normal_dataset, "ET")
        et_data_path = args.et_data_path or ".\\data\\MBPPEval\\MBPP_ET.jsonl"

    run_name_normal = _build_run_name(args.model, args.strategy, normal_dataset, args.language, args.temperature, args.pass_at_k)
    run_name_et = _build_run_name(args.model, args.strategy, args.dataset, args.language, args.temperature, args.pass_at_k)

    # Resolve normal results path candidates (merged preferred)
    normal_candidates = []
    if args.normal_results_path:
        normal_candidates.append(args.normal_results_path)
    normal_candidates.append(os.path.join(args.results_dir, f"{run_name_normal}-merged.jsonl"))
    normal_candidates.append(os.path.join(args.results_dir, normal_dataset, f"{run_name_normal}-merged.jsonl"))

    normal_path = _find_existing(normal_candidates)
    if not normal_path:
        raise FileNotFoundError(f"Normal results not found. Checked: {normal_candidates}")

    # ET output path
    et_path = args.et_results_path or os.path.join(et_dir, f"{run_name_et}.jsonl")
    os.makedirs(os.path.dirname(et_path), exist_ok=True)

    print(f"Generating ET results for {run_name_et}")
    print(f" - Normal results: {normal_path}")
    print(f" - ET data: {et_data_path}")
    print(f" - Output: {et_path}")

    if args.dataset == "HumanEvalET":
        generate_et_dataset(normal_path, et_path, ET_DATA_PATH=et_data_path, repair_attempts=args.repair_attempts, repair_model=args.model, language=args.language, timeout=args.timeout)
    else:
        generate_et_dataset_mbpp(normal_path, et_path, ET_DATA_PATH=et_data_path, repair_attempts=args.repair_attempts, repair_model=args.model, language=args.language, timeout=args.timeout)


if __name__ == "__main__":
    main()


