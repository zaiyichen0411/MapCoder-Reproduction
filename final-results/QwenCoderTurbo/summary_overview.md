# QwenCoderTurbo Final Results Overview

## Highlights
- MapCoder 在 `XCode` 与 `CC` 中相对更优（XCode `19.81%`、CC `60.71%`），对 I/O 约束更友好。
- 与 QwenCoder480b 对比：在多数数据集上 Turbo 落后于 480b 的 MapCoder 表现（详见图像）。

## APPS
- Strategy: `Analogical` — total `140`, solved `19`, pass rate `13.57%` (merged: `results/APPS/QwenCoderTurbo-Analogical-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `140`, solved `19`, pass rate `13.57%` (merged: `results/APPS/QwenCoderTurbo-CoT-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `140`, solved `0`, pass rate `0.00%` (merged: `results/APPS/QwenCoderTurbo-Direct-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `140`, solved `14`, pass rate `10.00%` (merged: `results/APPS/QwenCoderTurbo-MapCoder-APPS-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `140`, solved `14`, pass rate `10.00%` (merged: `results/APPS/QwenCoderTurbo-SelfPlanning-APPS-Python3-0.0-1-merged.jsonl`)

## HumanEval
- Strategy: `Analogical` — total `164`, solved `138`, pass rate `84.15%` (merged: `results/HumanEval/QwenCoderTurbo-Analogical-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `164`, solved `152`, pass rate `92.68%` (merged: `results/HumanEval/QwenCoderTurbo-CoT-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `164`, solved `118`, pass rate `71.95%` (merged: `results/HumanEval/QwenCoderTurbo-Direct-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `188`, solved `117`, pass rate `62.23%` (merged: `results/HumanEval/QwenCoderTurbo-MapCoder-HumanEval-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `164`, solved `136`, pass rate `82.93%` (merged: `results/HumanEval/QwenCoderTurbo-SelfPlanning-HumanEval-Python3-0.0-1-merged.jsonl`)

## XCode
- Strategy: `Analogical` — total `106`, solved `1`, pass rate `0.94%` (merged: `results/XCode/QwenCoderTurbo-Analogical-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `106`, solved `5`, pass rate `4.72%` (merged: `results/XCode/QwenCoderTurbo-CoT-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `106`, solved `0`, pass rate `0.00%` (merged: `results/XCode/QwenCoderTurbo-Direct-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `106`, solved `21`, pass rate `19.81%` (merged: `results/QwenCoderTurbo-MapCoder-XCode-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `106`, solved `1`, pass rate `0.94%` (merged: `results/XCode/QwenCoderTurbo-SelfPlanning-XCode-Python3-0.0-1-merged.jsonl`)

## MBPP
- Strategy: `Analogical` — total `186`, solved `128`, pass rate `68.82%` (merged: `results/MBPP/QwenCoderTurbo-Analogical-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `CoT` — total `397`, solved `316`, pass rate `79.60%` (merged: `results/MBPP/QwenCoderTurbo-CoT-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `Direct` — total `397`, solved `214`, pass rate `53.90%` (merged: `results/MBPP/QwenCoderTurbo-Direct-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `MapCoder` — total `397`, solved `304`, pass rate `76.57%` (merged: `results/MBPP/QwenCoderTurbo-MapCoder-MBPP-Python3-0.0-1-merged.jsonl`)
- Strategy: `SelfPlanning` — total `397`, solved `315`, pass rate `79.35%` (merged: `results/MBPP/QwenCoderTurbo-SelfPlanning-MBPP-Python3-0.0-1-merged.jsonl`)

## CC
- Strategy: `MapCoder` — total `28`, solved `17`, pass rate `60.71%` (merged: `results/QwenCoderTurbo-MapCoder-CC-Python3-0.0-1-merged.jsonl`)

## HumanEvalET
- Strategy: `Analogical` — total `164`, solved `119`, pass rate `72.56%` (file: `results/HumanEval/ET/QwenCoderTurbo-Analogical-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `CoT` — total `164`, solved `124`, pass rate `75.61%` (file: `results/HumanEval/ET/QwenCoderTurbo-CoT-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `Direct` — total `164`, solved `107`, pass rate `65.24%` (file: `results/HumanEval/QwenCoderTurbo-Direct-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `MapCoder` — total `164`, solved `115`, pass rate `70.12%` (file: `results/HumanEval/ET/QwenCoderTurbo-MapCoder-HumanEvalET-Python3-0.0-1.jsonl`)
- Strategy: `SelfPlanning` — total `164`, solved `122`, pass rate `74.39%` (file: `results/HumanEval/ET/QwenCoderTurbo-SelfPlanning-HumanEvalET-Python3-0.0-1.jsonl`)
