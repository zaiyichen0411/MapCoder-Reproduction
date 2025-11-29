# Logs Archive

本目录用于集中归档评测运行产生的日志文件，并按照数据集与策略分类管理，便于排查与复盘。

## 结构约定
- APPS/、CC/、XCode/：分别存放对应数据集的运行日志，按策略子目录划分。
- HumanEval/：存放 HumanEval 系列日志，包含标准与重试日志。
- misc/：杂项或系统级输出，例如单次测试、通用输出。

## 命名规范
- 标准日志（HumanEval）：`he_<ana|cot|direct|mc|sp>_<n>.log`
- 重试日志（HumanEval）：`he_<ana|cot|direct|mc|sp>_retry_<n>.log`
- 修复日志（HumanEval）：`he_cot_fix_<n>.log`、`he_sp_retry_<n>.log`
- 其他输出：`output_<n>.log` 或 `single_test.log`

## 示例索引（节选）
- HumanEval/Analogical/：`he_ana_1.log` ~ `he_ana_8.log`
- HumanEval/AnalogicalRetry/：`he_ana_retry_1.log` ~ `he_ana_retry_8.log`
- HumanEval/CoT/：`he_cot_1.log` ~ `he_cot_8.log`
- HumanEval/CoTFix/：`he_cot_fix_1.log` ~ `he_cot_fix_8.log`
- HumanEval/Direct/：`he_direct_1.log` ~ `he_direct_8.log`
- HumanEval/MapCoder/：`he_mc_1.log` ~ `he_mc_8.log`
- HumanEval/SelfPlanning/：`he_sp_1.log` ~ `he_sp_8.log`
- HumanEval/SelfPlanningRetry/：`he_sp_retry_1.log` ~ `he_sp_retry_8.log`
- misc/：`output.log`、`output1.log`、`output2.log`、`single_test.log`

## 维护方式
- 脚本 `scripts/organize_assets.py` 会自动识别并归档根目录 `.log` 文件。
- 如新增命名模式，请在脚本中补充正则规则后运行以更新归档。