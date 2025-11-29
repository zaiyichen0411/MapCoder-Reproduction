import sys
from datetime import datetime
from constants.paths import *

from models.Gemini import Gemini
from models.OpenAI import OpenAIModel

from results.Results import Results

from promptings.PromptingFactory import PromptingFactory
from datasets.DatasetFactory import DatasetFactory
from models.ModelFactory import ModelFactory



import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--dataset", 
    type=str, 
    default="HumanEval", 
    choices=[
        "HumanEval", 
        "MBPP", 
        "APPS",
        "xCodeEval", 
        "XCode",
        "CC", 
    ]
)
parser.add_argument(
    "--strategy", 
    type=str, 
    default="MapCoder", 
    choices=[
        "Direct",
        "CoT",
        "SelfPlanning",
        "Analogical",
        "MapCoder",
    ]
)
parser.add_argument(
    "--model", 
    type=str, 
    default="GPT4", 
    choices=[
        "gpt-3.5-turbo",
        "ChatGPT",
        "GPT4",
        "Gemini",
        "QwenCoderTurbo",
        "TongyiQianwenCoder",
        "QwenCoder480b",
        "MinimaxM2",
    ]
)
parser.add_argument(
    "--temperature", 
    type=float, 
    default=0
)
parser.add_argument(
    "--pass_at_k", 
    type=int, 
    default=1
)
parser.add_argument(
    "--language", 
    type=str, 
    default="Python3", 
    choices=[
        "C",
        "C#",
        "C++",
        "Go",
        "PHP",
        "Python3",
        "Ruby",
        "Rust",
    ]
)
parser.add_argument(
    "--start-index", 
    type=int, 
    default=None
)

parser.add_argument(
    "--end-index", 
    type=int, 
    default=None
)

parser.add_argument(
    "--results-suffix",
    type=str,
    default="",
    help="Suffix for results filename to avoid concurrent writes (e.g., -p1)"
)
parser.add_argument(
    "--quiet",
    action="store_true",
    help="Reduce logging verbosity"
)
parser.add_argument(
    "--discard-previous-run",
    action="store_true",
    help="If set, discard any existing results file before starting this run"
)

args = parser.parse_args()

DATASET = args.dataset
STRATEGY = args.strategy
MODEL_NAME = args.model
TEMPERATURE = args.temperature
PASS_AT_K = args.pass_at_k
LANGUAGE = args.language
START_INDEX = args.start_index
END_INDEX = args.end_index
RESULTS_SUFFIX = args.results_suffix or ""
DISCARD_PREVIOUS_RUN = bool(getattr(args, "discard_previous_run", False))
VERBOSE = not bool(getattr(args, "quiet", False))

RUN_NAME = f"{MODEL_NAME}-{STRATEGY}-{DATASET}-{LANGUAGE}-{TEMPERATURE}-{PASS_AT_K}"
RESULTS_PATH = os.path.abspath(f"./results/{RUN_NAME}{RESULTS_SUFFIX}.jsonl")

print(f"#########################\nRunning start {RUN_NAME}, Time: {datetime.now()}\n##########################\n")

data=DatasetFactory.get_dataset_class(DATASET)()

# slice the data based on the start and end index
if START_INDEX is not None and END_INDEX is not None:
    data.data = data.data[START_INDEX:END_INDEX]

strategy = PromptingFactory.get_prompting_class(STRATEGY)(
    data=data,
    model=ModelFactory.get_model_class(MODEL_NAME)(
        temperature=TEMPERATURE,
    ),
    language=LANGUAGE,
    pass_at_k=PASS_AT_K,
    results=Results(RESULTS_PATH, discard_previous_run=DISCARD_PREVIOUS_RUN),
    verbose=VERBOSE,
)

strategy.run()

print(f"#########################\nRunning end {RUN_NAME}, Time: {datetime.now()}\n##########################\n")

