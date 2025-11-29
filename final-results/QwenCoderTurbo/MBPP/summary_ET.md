# MBPP-ET Summary — QwenCoderTurbo · MapCoder

Run configuration
- Dataset: `MBPP-ET`
- Model: `QwenCoderTurbo`
- Strategy: `MapCoder`
- Language: `Python3`
- Temperature: `0.0`
- Pass@k: `1`
- ET data: `data/MBPPEval/MBPP_ET.jsonl`
- ET results file: `results/MBPP/ET/QwenCoderTurbo-MapCoder-MBPPET-Python3-0.0-1.jsonl`

Metrics
- Total samples: `397`
- Solved: `218`
- Pass@1: `54.91%`

Validation
- Counted by reading ET JSONL (`is_solved` flag).
- Cross-checked with merged MBPP normal results for consistency.

Notes
- MBPP-ET uses extended tests to validate correctness beyond MBPP unit tests.