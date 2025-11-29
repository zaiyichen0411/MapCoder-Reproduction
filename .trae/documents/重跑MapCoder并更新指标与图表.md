## 当前指标（QwenCoderTurbo, Python3, T=0.0, pass@1）
- HumanEval：总 164，MapCoder 125，Pass@1 76.22%（final-results/QwenCoderTurbo/HumanEval/summary_compare.md）
- HumanEval（另一汇总口径）：总 188，MapCoder 117，Pass@1 62.23%（final-results/QwenCoderTurbo/summary_overview.md）
- HumanEval-ET：总 164，MapCoder 115，Pass@1 70.12%（final-results/QwenCoderTurbo/summary_overview.md）
- MBPP：总 397，MapCoder 304，Pass@1 76.57%（final-results/QwenCoderTurbo/MBPP/summary_compare.md）
- APPS：总 140，MapCoder 14，Pass@1 10.00%（final-results/QwenCoderTurbo/APPS/MapCoder-summary.md）
- XCode：总 106，MapCoder 5，Pass@1 4.72%（final-results/QwenCoderTurbo/XCode/MapCoder-summary.md）
- CodeContest：总 10，MapCoder 1，Pass@1 10.00%（final-results/QwenCoderTurbo/CC/summary_MapCoder.md）

## 目标
- 全量重跑 MapCoder 策略：HumanEval、MBPP、APPS、XCode、CC（必要时 HumanEvalET/MBPPET 保持现有）。
- 统一合并与汇总口径，更新各数据集的摘要文件与总览，并重生图像。

## 执行方案
### 1) 重跑命令（PowerShell，使用 `--results-suffix=-fresh` 避免覆盖）
- HumanEval：
  - `python src/main.py --dataset HumanEval --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --results-suffix=-fresh --discard-previous-run`
- MBPP（并行）：
  - `python scripts/run_parallel.py --dataset MBPP --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --processes 4 --results-suffix=-fresh --discard-previous-run`
- APPS（并行）：
  - `python scripts/run_parallel.py --dataset APPS --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --processes 4 --results-suffix=-fresh --discard-previous-run`
- XCode（并行或单进程）：
  - `python scripts/run_parallel.py --dataset XCode --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --processes 4 --results-suffix=-fresh --discard-previous-run`
- CodeContest（CC）：
  - `python src/main.py --dataset CC --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --results-suffix=-fresh --discard-previous-run`

说明：
- 大数据集优先使用 `scripts/run_parallel.py` 以充分利用多核；`--processes` 可按机器资源调大。
- 若已有分片历史（p1…p8），保持一致的 `RUN_NAME` 避免指标口径混乱。

### 2) 合并分片与生成摘要
- 通用合并（示例以 HumanEval）：
  - `python scripts/merge_results.py --dataset HumanEval --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --parts 8 --results_dir results --merged_out results/HumanEval/QwenCoderTurbo-MapCoder-HumanEval-Python3-0.0-1-merged.jsonl --summary_out final-results/QwenCoderTurbo/HumanEval/summary_MapCoder.md`
- 其他数据集类推（将 `--dataset` 与输出路径替换为对应目录，如 `results/APPS/...-merged.jsonl` 与 `final-results/QwenCoderTurbo/APPS/MapCoder-summary.md`）。
- 若单文件无分片，可用：
  - `python scripts/merge_results.py --dataset HumanEval --strategy MapCoder --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --single_path QwenCoderTurbo-MapCoder-HumanEval-Python3-0.0-1-fresh.jsonl --summary_out final-results/QwenCoderTurbo/HumanEval/summary_MapCoder.md`

### 3) 更新总览与对比摘要
- 统一刷新各数据集的 `summary_overview.md` 与 `summary_compare.md`：
  - `python scripts/update_results_summaries.py`
- 该脚本会遍历 `results/<Dataset>/*-merged.jsonl`，写入到 `final-results/<Model>/<Dataset>/summary_overview.md` 与 `summary_compare.md`。

### 4) 生成图像
- 生成模型对比与策略分布图：
  - `python scripts/generate_progress_charts.py`
- 输出目录：`images/progress` 下的 `Compare/`、`QwenCoderTurbo/` 等；脚本会自动清理过期 PNG。

## 交付物
- 每数据集：`final-results/QwenCoderTurbo/<Dataset>/summary_MapCoder.md`（或同名结构），`summary_overview.md`、`summary_compare.md`。
- 统一总览：`final-results/QwenCoderTurbo/summary_overview.md` 更新。
- 图像：`images/progress/Compare/*.png`、`images/progress/QwenCoderTurbo/*.png`。

## 预计耗时与资源
- HumanEval/MBPP：数十分钟到数小时（取决于并发与远程执行速度）。
- APPS/XCode/CC：数据规模与远程执行影响较大，建议 `--processes=4~8`。

## 风险与一致性处理
- 现有文件存在“总数/口径”不一致（如 HumanEval 164 vs 188）；本次统一使用合并后的 `*-merged.jsonl` 作为唯一口径并由 `update_results_summaries.py` 自动生成总览，避免重复统计。
- PowerShell 下参数需使用 `--results-suffix=-xxx` 格式；避免空值导致解析错误。

## 下一步
- 确认后立即按上述命令重跑各数据集；运行完成后合并、刷新摘要，并生成图像。