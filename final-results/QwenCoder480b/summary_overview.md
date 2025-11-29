# QwenCoder480b Final Results Overview

## Highlights
- MapCoder 在 `XCode` 中为最佳策略（`31.13%`），领先其他策略。
- 与 QwenCoderTurbo 对比：在 `APPS`、`HumanEval`、`XCode` 的 MapCoder 表现均高于 Turbo 模型（详见图像）。

## APPS
- Strategy: `Analogical` — total `140`, solved `49`, pass rate `35.00%` (merged: `results/APPS/QwenCoder480b-Analogical-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `140`, solved `64`, pass rate `45.71%` (merged: `results/APPS/QwenCoder480b-CoT-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `140`, solved `76`, pass rate `54.29%` (merged: `results/APPS/QwenCoder480b-Direct-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `128`, solved `62`, pass rate `48.44%` (merged: `results/QwenCoder480b-MapCoder-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `140`, solved `71`, pass rate `50.71%` (merged: `results/APPS/QwenCoder480b-SelfPlanning-APPS-Python3-0.0-1-merged.jsonl`)

## HumanEval
- Strategy: `Analogical` — total `164`, solved `124`, pass rate `75.61%` (merged: `results/HumanEval/QwenCoder480b-Analogical-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `164`, solved `153`, pass rate `93.29%` (merged: `results/HumanEval/QwenCoder480b-CoT-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `164`, solved `157`, pass rate `95.73%` (merged: `results/HumanEval/QwenCoder480b-Direct-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `164`, solved `118`, pass rate `71.95%` (merged: `results/HumanEval/QwenCoder480b-MapCoder-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `164`, solved `158`, pass rate `96.34%` (merged: `results/HumanEval/QwenCoder480b-SelfPlanning-HumanEval-Python3-0.0-1-merged.jsonl`)

## XCode
- Strategy: `Analogical` — total `106`, solved `1`, pass rate `0.94%` (merged: `results/XCode/QwenCoder480b-Analogical-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `106`, solved `28`, pass rate `26.42%` (merged: `results/XCode/QwenCoder480b-CoT-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `106`, solved `23`, pass rate `21.70%` (merged: `results/XCode/QwenCoder480b-Direct-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `106`, solved `33`, pass rate `31.13%` (merged: `results/QwenCoder480b-MapCoder-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `106`, solved `28`, pass rate `26.42%` (merged: `results/XCode/QwenCoder480b-SelfPlanning-XCode-Python3-0.0-1-merged.jsonl`)

## MBPP
- Strategy: `Analogical` — total `397`, solved `257`, pass rate `64.74%` (merged: `results/MBPP/QwenCoder480b-Analogical-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `397`, solved `339`, pass rate `85.39%` (merged: `results/MBPP/QwenCoder480b-CoT-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `397`, solved `219`, pass rate `55.16%` (merged: `results/MBPP/QwenCoder480b-Direct-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `397`, solved `295`, pass rate `74.31%` (merged: `results/MBPP/QwenCoder480b-MapCoder-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `397`, solved `332`, pass rate `83.63%` (merged: `results/MBPP/QwenCoder480b-SelfPlanning-MBPP-Python3-0.0-1-merged.jsonl`)

## HumanEvalET
- Strategy: `Analogical` — total `164`, solved `109`, pass rate `66.46%` (file: `results/HumanEval/ET/QwenCoder480b-Analogical-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `CoT` — total `164`, solved `139`, pass rate `84.76%` (file: `results/HumanEval/ET/QwenCoder480b-CoT-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `Direct` — total `164`, solved `139`, pass rate `84.76%` (file: `results/HumanEval/ET/QwenCoder480b-Direct-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `MapCoder` — total `164`, solved `109`, pass rate `66.46%` (file: `results/HumanEval/ET/QwenCoder480b-MapCoder-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `SelfPlanning` — total `164`, solved `142`, pass rate `86.59%` (file: `results/HumanEval/ET/QwenCoder480b-SelfPlanning-HumanEvalET-Python3-0.0-1.jsonl`)
