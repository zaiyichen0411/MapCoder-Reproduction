import os
from importlib.machinery import SourceFileLoader
from types import ModuleType

_mod_path = os.path.join("src", "evaluate-et-dataset.py")
et_mod: ModuleType = SourceFileLoader("evaluate_et_dataset", _mod_path).load_module()
generate_et_dataset = getattr(et_mod, "generate_et_dataset")
_build_run_name = getattr(et_mod, "_build_run_name")


def gen_one(strategy: str):
    model = "QwenCoder480b"
    language = "Python3"
    temperature = "0.0"
    pass_at_k = 1
    results_dir = "results"

    normal_dataset = "HumanEval"
    et_dataset = "HumanEvalET"

    run_name_normal = _build_run_name(model, strategy, normal_dataset, language, temperature, pass_at_k)
    normal_path = os.path.join(results_dir, normal_dataset, f"{run_name_normal}-merged.jsonl")
    if not os.path.exists(normal_path):
        normal_path = os.path.join(results_dir, f"{run_name_normal}-merged.jsonl")
    if not os.path.exists(normal_path):
        raise FileNotFoundError(f"Normal merged not found for {strategy}: {normal_path}")

    et_out_dir = os.path.join(results_dir, normal_dataset, "ET")
    os.makedirs(et_out_dir, exist_ok=True)
    run_name_et = _build_run_name(model, strategy, et_dataset, language, temperature, pass_at_k)
    et_out_path = os.path.join(et_out_dir, f"{run_name_et}.jsonl")

    print(f"Generating ET for {strategy} -> {et_out_path}")
    et_data_path = os.path.join("data", "HumanEval", "HumanEvalET.jsonl")
    generate_et_dataset(normal_path, et_out_path, ET_DATA_PATH=et_data_path)


def main():
    for strat in ["Analogical", "CoT", "SelfPlanning", "MapCoder", "Direct"]:
        gen_one(strat)


if __name__ == "__main__":
    main()