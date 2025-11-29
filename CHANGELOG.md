# Changelog

## [Unreleased]
- Plan: Rerun QwenCoderTurbo on MBPP (CoT, Analogical, SelfPlanning) and QwenCoder480b on HumanEvalET (Analogical, CoT, Direct, MapCoder, SelfPlanning). Generate ET JSONL and update final summaries.

## [2025-11-12] Docs standardization and ET summary fixes
- Standardize Turbo/MBPP summary pages:
  - Added `summary_Analogical.md` and `summary_CoT.md` (pending placeholders).
  - Added `summary_SelfPlanning.md` (pending placeholder).
  - Updated `summary.md` (MapCoder) with run configuration, metrics, validation notes.
  - Updated `summary_Direct.md` with standardized template and notes.
  - Updated `summary_ET.md` with ET configuration and validation section.
- Corrected 480b HumanEvalET comparison page:
  - Replaced incorrect Turbo file references with 480b pending ET entries.
  - Added run configuration, data sources, and status notes.
- Charts: prepared chart generation via `scripts/generate_progress_charts.py` (execution pending due to terminal contention). Pages include guidance and placeholders for chart embedding.

### Notes
- HumanEvalET ET generation for QwenCoder480b is pending; normal merged results are present under `results/HumanEval/` for all strategies.
- Turbo MBPP CoT/Analogical/SelfPlanning runs are pending. Summary pages are standardized and will auto-populate once merged JSONL are available.