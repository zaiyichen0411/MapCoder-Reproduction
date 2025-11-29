# Evaluation Progress Tracker

> 中文注释：本页用于跟踪各数据集评测进度与关键指标。
> 术语说明：`solved` 表示通过题目数；`pass rate` 为通过率；`Compare` 为该数据集的对比汇总页（位于 `final-results` 目录）。

## Completed Strategies and Metrics

- APPS — `QwenCoder480b`
  - CoT: total `140`, solved `64`, pass rate `45.71%`
  - Analogical: total `140`, solved `49`, pass rate `35.00%`
  - Direct: total `140`, solved `76`, pass rate `54.29%`
  - SelfPlanning: total `140`, solved `71`, pass rate `50.71%`
  - MapCoder: total `140`, solved `71`, pass rate `50.71%`
  - Compare: `final-results\QwenCoder480b\APPS\summary_compare.md`
  - 说明：`Compare` 指向 APPS 的结果对比页，合并文件路径在对比页中列出。

- CodeContest (CC) — `QwenCoder480b`
  - CoT: total `30`, solved `13`, pass rate `43.33%`
  - Direct: total `30`, solved `13`, pass rate `43.33%`
  - SelfPlanning: total `30`, solved `9`, pass rate `30.00%`
  - MapCoder: total `30`, solved `11`, pass rate `36.67%`
  - Analogical: total `30`, solved `5`, pass rate `16.67%`
  - Compare: `final-results\QwenCoder480b\CC\summary_compare.md`
  - 说明：`Compare` 指向 CC 的结果对比页，指标来源于合并结果统计。

- HumanEval — `QwenCoder480b`
  - CoT: total `164`, solved `153`, pass rate `93.29%`
  - Analogical: total `164`, solved `124`, pass rate `75.61%`
  - Direct: total `164`, solved `157`, pass rate `95.73%`
  - SelfPlanning: total `164`, solved `158`, pass rate `96.34%`
  - MapCoder: total `164`, solved `118`, pass rate `71.95%`
  - Compare: `final-results\QwenCoder480b\HumanEval\summary_compare.md`
  - 说明：`Compare` 指向 HumanEval 的结果对比页；合并与分片 JSONL 位于 `results\HumanEval`。

- XCode — `QwenCoder480b`
  - Direct: total `106`, solved `23`, pass rate `21.70%`
  - CoT: total `106`, solved `28`, pass rate `26.42%`
  - Analogical: total `106`, solved `1`, pass rate `0.94%`
  - SelfPlanning: total `106`, solved `28`, pass rate `26.42%`
  - MapCoder: total `106`, solved `21`, pass rate `19.81%`
  - Compare: `final-results\QwenCoder480b\XCode\summary_compare.md`
  - 说明：`Compare` 指向 XCode 的结果对比页，路径已与整理后的目录同步。

- MBPP — `QwenCoder480b`
  - Direct: total `397`, solved `219`, pass rate `55.16%`
  - CoT: total `397`, solved `339`, pass rate `85.39%`
  - SelfPlanning: total `397`, solved `332`, pass rate `83.63%`
  - MapCoder: total `397`, solved `295`, pass rate `74.31%`
  - Analogical: total `397`, solved `257`, pass rate `64.74%`
  - Compare: `final-results\QwenCoder480b\MBPP\summary_compare.md`
  - 说明：`Compare` 指向 MBPP 的结果对比页；合并结果在 `results\MBPP`。

- APPS — `QwenCoderTurbo`
  - CoT: total `140`, solved `19`, pass rate `13.57%`
  - Analogical: total `140`, solved `19`, pass rate `13.57%`
  - SelfPlanning: total `140`, solved `14`, pass rate `10.00%`
  - MapCoder: total `140`, solved `14`, pass rate `10.00%`
  - Overview: `final-results\QwenCoderTurbo\summary_overview.md`
  - 说明：Turbo 的 APPS 结果均为分片合并后统计，合并文件位于 `results\APPS`。

- CodeContest (CC) — `QwenCoderTurbo`
  - CoT: total `30`, solved `3`, pass rate `10.00%`
  - Analogical: total `30`, solved `3`, pass rate `10.00%`
  - SelfPlanning: total `30`, solved `3`, pass rate `10.00%`
  - MapCoder: total `30`, solved `1`, pass rate `3.33%`
  - Overview: `final-results\QwenCoderTurbo\summary_overview.md`
  - 说明：Turbo 的 CC 结果合并文件位于 `results\CodeContest`。

- HumanEval — `QwenCoderTurbo`
  - CoT: total `164`, solved `138`, pass rate `84.15%`
  - Analogical: total `164`, solved `138`, pass rate `84.15%`
  - SelfPlanning: total `164`, solved `136`, pass rate `82.93%`
  - MapCoder: total `164`, solved `125`, pass rate `76.22%`
  - Overview: `final-results\QwenCoderTurbo\summary_overview.md`
  - 说明：Turbo 的 HumanEval 合并与分片 JSONL 位于 `results\HumanEval`。

- XCode — `QwenCoderTurbo`
  - CoT: total `106`, solved `5`, pass rate `4.72%`
  - Analogical: total `106`, solved `1`, pass rate `0.94%`
  - SelfPlanning: total `106`, solved `1`, pass rate `0.94%`
  - MapCoder: total `106`, solved `5`, pass rate `4.72%`
  - Overview: `final-results\QwenCoderTurbo\summary_overview.md`
  - 说明：Turbo 的 XCode 合并文件位于 `results\XCode`。

- MBPP — `QwenCoderTurbo`
  - MapCoder: total `397`, solved `304`, pass rate `76.57%`
  - Overview: `final-results\QwenCoderTurbo\summary_overview.md`
  - 说明：Turbo 的 MBPP 当前仅统计 `MapCoder` 策略；合并文件位于 `results\MBPP`。

- HumanEvalET — `QwenCoderTurbo`
  - Analogical: total `164`, solved `119`, pass rate `72.56%`
  - CoT: total `164`, solved `124`, pass rate `75.61%`
  - SelfPlanning: total `164`, solved `122`, pass rate `74.39%`
  - MapCoder: total `164`, solved `115`, pass rate `70.12%`
  - Compare: `final-results\QwenCoder480b\HumanEvalET\summary_compare.md`
  - 说明：HumanEvalET 为扩展测试集；结果 JSONL 位于 `results\HumanEval\ET`。

## Active / Recent Jobs

- HumanEvalET — `Analogical` (model: `QwenCoderTurbo`, language: `Python3`, temperature `0.0`, pass_at_k `1`)
  - Command: `python src/evaluate-et-dataset.py --dataset HumanEvalET --strategy Analogical --model QwenCoderTurbo --language Python3 --temperature 0.0 --pass_at_k 1 --results_dir results`
  - Status: `completed`
  - Results: `results\HumanEval\ET\QwenCoderTurbo-Analogical-HumanEvalET-Python3-0.0-1.jsonl`（已统计并汇总至上方）
  - 说明：上述命令已完成并计入指标；`temperature=0.0` 代表确定性采样，`pass_at_k=1` 为单样本评估。

## Logs Reference (sharded runs)

- APPS: `APPS_Ana_*.log`, `APPS_CoT_*.log`, `APPS_Map_*.log`, `APPS_SP_*.log`
- CC: `CC_Ana_*.log`, `CC_CoT_*.log`, `CC_Map_*.log`, `CC_SP_*.log`
- XCode: `XCode_Ana_*.log`, `XCode_CoT_*.log`, `XCode_Map_*.log`, `XCode_SP_*.log`
- HumanEval: `he_ana_*.log`, `he_cot_*.log`, `he_direct_*.log`, `he_mc_*.log`, `he_sp_*.log`

> 注释：HumanEval 重试日志命名为 `he_<strategy>_retry_<n>.log`；日志已归档至 `archive\logs`，详见该目录的 `README.md`。

> 注：本页会在任务完成或有新并行任务启动时持续更新，确保与各 `summary_compare.md` 保持一致。

## Charts (Pass Rate)

- 模型对比（同一数据集、同一策略）：
  - APPS: ![APPS 模型对比](images/progress/compare_models_APPS.png)
  - CodeContest: ![CC 模型对比](images/progress/compare_models_CC.png)
  - HumanEval: ![HumanEval 模型对比](images/progress/compare_models_HumanEval.png)
  - XCode: ![XCode 模型对比](images/progress/compare_models_XCode.png)
  - MBPP: ![MBPP 模型对比](images/progress/compare_models_MBPP.png)

- Turbo 跨数据集的策略表现：
  - CoT: ![Turbo CoT 跨数据集](images/progress/turbo_CoT_across_datasets.png)
  - Analogical: ![Turbo Analogical 跨数据集](images/progress/turbo_Analogical_across_datasets.png)
  - SelfPlanning: ![Turbo SelfPlanning 跨数据集](images/progress/turbo_SelfPlanning_across_datasets.png)
  - MapCoder: ![Turbo MapCoder 跨数据集](images/progress/turbo_MapCoder_across_datasets.png)
  - HumanEvalET 策略汇总: ![Turbo HumanEvalET 策略汇总](images/progress/turbo_HumanEvalET_strategies.png)

- 480b 跨数据集的策略表现：
  - Direct: ![480b Direct 跨数据集](images/progress/480b_Direct_across_datasets.png)
  - CoT: ![480b CoT 跨数据集](images/progress/480b_CoT_across_datasets.png)
  - Analogical: ![480b Analogical 跨数据集](images/progress/480b_Analogical_across_datasets.png)
  - SelfPlanning: ![480b SelfPlanning 跨数据集](images/progress/480b_SelfPlanning_across_datasets.png)
  - MapCoder: ![480b MapCoder 跨数据集](images/progress/480b_MapCoder_across_datasets.png)

> 说明：以上为柱状图文件相对路径，图片生成脚本见 `scripts/generate_progress_charts.py`。若图片尚未生成，可先运行脚本或暂用上方数值对比。

## Charts (Dual Axis)

- 480b Direct 跨数据集（Solved + Pass Rate）: ![480b Direct Dual Axis](images/progress/480b_direct_datasets_dual_axis.png)
- 480b 在 HumanEval 策略（Solved + Pass Rate）: ![480b HumanEval Strategies Dual Axis](images/progress/480b_humaneval_strategies_dual_axis.png)
- Turbo Direct 跨数据集（Solved + Pass Rate）: ![Turbo Direct Dual Axis](images/progress/turbo_direct_datasets_dual_axis.png)
- Turbo 在 HumanEval 策略（Solved + Pass Rate）: ![Turbo HumanEval Strategies Dual Axis](images/progress/turbo_humaneval_strategies_dual_axis.png)