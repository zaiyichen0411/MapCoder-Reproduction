## 改进目标
- 面向 HumanEval 与 MBPP 提升 MapCoder 的通过率与稳健性，保持推理成本可控。

## 关键改动
1. 提升规划与示例密度（可按数据集动态设置）
- 修改默认参数：`src/promptings/MapCoder.py:43-52`，将 `k=3,t=5` 调整为：
  - HumanEval：`k=4,t=6`
  - MBPP：`k=5,t=6`
- 原因：更丰富的知识库与示例可提升代码生成一致性；适度增加步骤提高边界覆盖。

2. 增强约束与输出规范，明确禁止测试与 I/O
- 代码生成系统提示追加强约束（保留语言围栏，仅函数/程序，不含示例/断言/打印）：`src/promptings/MapCoder.py:394-414`
- 建议追加文本：
  - HumanEval/MBPP：
    - “只实现入口函数，不编写任何 I/O 或顶层测试；不得返回示例断言或打印。”
  - APPS/CodeContest/XCode：
    - “只包含完整可运行主程序；不得包含解释性注释或围栏外文本。”

3. 入口函数一致性强校验
- 在最终代码解析后，若数据集中存在 `entry_point`，对返回代码做轻量检查与修复：
  - 若未找到 `def <entry_point>(` 则触发一次改进循环，反馈为“未实现指定入口函数”。
- 插入位置：`src/promptings/MapCoder.py:424-431` 之后，进入改进循环前进行入口一致性检查。

4. 改进循环重试与超时
- 将改进循环超时从 `10s` 提升至 `15-20s`：`src/promptings/MapCoder.py:432`
- 将 `self.max_retries` 从 `3` 增至 `4`（在 `__init__`）：`src/promptings/MapCoder.py:51-53`
- 原因：减少误判超时导致的失败，提供一次额外修复机会（成本增幅有限）。

5. 结合相似题示例（MBPP）
- 读取 `data/MBPPEval/similar_problems_solutions.jsonl`，按 `name` 或关键词匹配选取 1-2 个相似题的“思路摘要 + 解法片段”，直接填入 `<exemplars>`，降低“凭空造例”偏差。
- 逻辑位置：在“知识库与示例生成”前，先尝试检索，若命中则将检索到的示例并入 `exemplars`；否则回退到模型生成（`src/promptings/MapCoder.py:221-246`）。

6. 规划验证更严格的充分性判据
- 验证提示新增“必须覆盖边界/空输入/重复元素/类型转换”等常见陷阱；若未覆盖则判为 `INCORRECT`：`src/promptings/MapCoder.py:334-361`。
- 目的：提升生成计划与测试的质量，避免“计划正确但测试薄弱”。

7. 代码解析健壮性提升
- `parse_code` 在存在多个代码围栏时，目前取最后一个；建议改为“优先取语言标签匹配且包含入口函数的代码块，否则取最后一个”：`src/promptings/MapCoder.py:104-161`。
- 无围栏回退：增加针对入口函数的首行定位（优先 `def <entry_point>`）。

## 运行参数建议
- HumanEval / MBPP：`--pass_at_k 5` 与 `--temperature 0.2~0.6`（OpenAI/GPT 路径）；Qwen 兼容路径会屏蔽温度与 `top_p`，但 `pass@k` 生效。
- 并行：按资源 `--processes 4~8`；开启 `--discard-previous-run` 避免旧分片干扰。

## 验证方案
- 小规模抽样对比（50 条）先行，确认提升后全量重跑。
- 合并与汇总：`scripts/merge_results.py`、`scripts/update_results_summaries.py`、`scripts/generate_model_overview.py`、`scripts/generate_progress_charts.py`。
- 显著性检验：对全量 MapCoder vs CoT 进行比例差异检验（二项/卡方）。

## 风险与注意
- Token 成本小幅上升（示例/步骤增多、重试增加）；可通过对短题降低 `k/t` 缓解。
- Qwen 兼容接口不支持 `temperature/top_p`；提升主要依赖规划/示例与改进循环。
- 相似题检索需确保文件存在与格式稳定；匹配失败回退到模型生成示例。