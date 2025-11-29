param(
    [string]$Root = "$(Get-Location)",
    [int]$Processes = 8,
    [string]$Temperature = "0.0",
    [int]$PassAtK = 1,
    [string]$Language = "Python3",
    [string[]]$Strategies = @("Direct", "CoT", "Analogical", "SelfPlanning", "MapCoder"),
    [string[]]$Datasets = @("HumanEval", "MBPP", "APPS", "XCode", "CC"),
    [string]$PythonExe = "",
    [switch]$RunEvalPlus,
    [switch]$DiscardPrevious
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Warning $msg }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$Model = "QwenCoder480b"
$RepoRoot = $Root

function Merge-And-Summarize($dataset, $strategy) {
    $args = @(
        "--dataset", $dataset,
        "--strategy", $strategy,
        "--model", $Model,
        "--language", $Language,
        "--temperature", $Temperature,
        "--pass_at_k", $PassAtK,
        "--parts", $Processes,
        "--results_dir", "results"
    )
    Write-Info "Merging shards: $($args -join ' ')"
    & py -3 "$RepoRoot\scripts\merge_results.py" @args
}

function Run-Parallel($dataset, $strategy) {
    $args = @(
        "--dataset", $dataset,
        "--strategy", $strategy,
        "--model", $Model,
        "--language", $Language,
        "--temperature", $Temperature,
        "--pass_at_k", $PassAtK,
        "--processes", $Processes
    )
    if ($PythonExe -ne "") { $args += @("--python-exe", $PythonExe) }
    if ($DiscardPrevious) { $args += @("--discard-previous-run") }
    Write-Info "Running parallel: $($args -join ' ')"
    & py -3 "$RepoRoot\scripts\run_parallel.py" @args
}

function Generate-HEP-Samples($strategy) {
    $args = @(
        "--model", $Model,
        "--strategy", $strategy,
        "--language", $Language,
        "--temperature", $Temperature,
        "--pass_at_k", $PassAtK,
        "--results_dir", "results",
        "--out_dir", "results\HumanEvalPlus"
    )
    Write-Info "Generating HumanEvalPlus samples: $($args -join ' ')"
    & py -3 "$RepoRoot\scripts\generate_humanevalplus_samples.py" @args
}

function Evaluate-HEP-Strategy($strategy) {
    $base = Join-Path $RepoRoot "results\HumanEvalPlus"
    $samples = Join-Path $base "$Model-$strategy-HumanEvalPlus-samples.jsonl"
    if (!(Test-Path $samples)) {
        Write-Warn "Samples not found for ${strategy}: $samples"
        return
    }
    $outdir = Join-Path $base $strategy
    if (!(Test-Path $outdir)) { New-Item -ItemType Directory -Force -Path $outdir | Out-Null }
    Set-Location $outdir
    Write-Info "Evaluating EvalPlus: humaneval --samples $samples"
    py -3 -m evalplus.evaluate humaneval --samples $samples
    Set-Location $RepoRoot
}

foreach ($d in $Datasets) {
    foreach ($s in $Strategies) {
        $dp = if ($DiscardPrevious) { " (discard_previous)" } else { "" }
        Write-Info "=== Dataset: $d | Strategy: $s | Model: $Model$dp ==="
        Run-Parallel -dataset $d -strategy $s
        Merge-And-Summarize -dataset $d -strategy $s
    }
}

# HumanEvalPlus pipeline (optional via -RunEvalPlus)
if ($RunEvalPlus) {
    Write-Info "Preparing HumanEvalPlus samples and evaluation for model: $Model"
    foreach ($s in $Strategies) {
        Generate-HEP-Samples -strategy $s
        Evaluate-HEP-Strategy -strategy $s
    }
    Write-Info "Writing summary for HumanEvalPlus"
    & py -3 "$RepoRoot\src\summarize_humanevalplus.py" --model $Model
}

Write-Info "All tasks dispatched."