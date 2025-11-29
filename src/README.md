# MapCoder src 目录结构与用法

本目录包含评测系统的核心代码，按功能划分为多个子包，便于扩展与维护。

## 目录结构

- `main.py`：入口脚本，运行标准评测流程。
- `evaluate-et-dataset.py`：评测扩展任务（ET）的专用入口。
- `gen-eval-plus-sample.py`：生成 EvalPlus 的样本与结果。
- `summarize_humanevalplus.py`：汇总 HumanEvalPlus 相关结果。

- `constants/`：全局常量与路径、语言映射。
- `datasets/`：各数据集的加载器与工厂（APPS、CodeContest、HumanEval、MBPP、XCode）。
- `evaluations/`：评测流程相关模块（API 通信、执行器、资源限制等）。
- `models/`：模型适配与工厂（Qwen、GPT、OpenAI、Gemini 等）。
- `promptings/`：提示策略（Analogical、CoT、Direct、MapCoder、SelfPlanning）。
- `results/`：结果对象与序列化辅助。
- `utils/`：通用工具（JSONL I/O、解析、Token 统计等）。

## 典型用法

- 运行标准评测（示例）：
  - `python src/main.py --start-index 0 --end-index 1`
- 运行 ET 评测（示例）：
  - `python src/evaluate-et-dataset.py --dataset HumanEvalET --strategy Analogical --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --results_dir results`

## 导入建议

- 数据集工厂：
  - `from datasets.DatasetFactory import DatasetFactory`
- 提示策略工厂：
  - `from promptings.PromptingFactory import PromptingFactory`
- 模型工厂与基类：
  - `from models.ModelFactory import ModelFactory`
  - `from models.Base import BaseModel`
- 评测工具：
  - `from evaluations.func_evaluate import run_functional_evaluation`
  - `from evaluations.executor_utils import execute_with_limits`

## 约定

- 各子包已包含 `__init__.py`，可作为标准 Python 包按需导入。
- 不对现有模块命名进行变更；如需重构命名，将通过单独 PR 并批量改动 import 保持一致。