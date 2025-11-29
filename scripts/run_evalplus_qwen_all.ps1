param(
    [string]$Root = "$(Get-Location)",
    [string]$OverridePath = ""
)

$base = Join-Path $Root "results\humanevalplus"
$strategies = @("Analogical", "CoT", "Direct", "MapCoder", "SelfPlanning")
$samples = @{
    Analogical = "QwenCoderTurbo-Analogical-HumanEvalPlus-samples.jsonl";
    CoT = "QwenCoderTurbo-CoT-HumanEvalPlus-samples.jsonl";
    Direct = "QwenCoderTurbo-Direct-HumanEvalPlus-samples.jsonl";
    MapCoder = "QwenCoderTurbo-MapCoder-HumanEvalPlus-samples.jsonl";
    SelfPlanning = "QwenCoderTurbo-SelfPlanning-HumanEvalPlus-samples.jsonl";
}

foreach ($s in $strategies) {
    $outdir = Join-Path $base $s
    if (!(Test-Path $outdir)) { New-Item -ItemType Directory -Force -Path $outdir | Out-Null }
    Set-Location $outdir
    $samplePath = Join-Path $base $samples[$s]
    py -3 -m evalplus.evaluate humaneval --samples $samplePath
}

Set-Location $Root
py -3 src/summarize_humanevalplus.py
$cacheDir = "$env:LOCALAPPDATA\evalplus\evalplus\Cache"
if ($OverridePath -ne "") {
    if (Test-Path $OverridePath) {
        Write-Host "Using local HumanEvalPlus via HUMANEVAL_OVERRIDE_PATH: $OverridePath"
        $env:HUMANEVAL_OVERRIDE_PATH = $OverridePath
    } else {
        Write-Warning "OverridePath provided but file not found: $OverridePath"
    }
} else {
    # If cache file already exists, no download will happen
    $defaultCache = Join-Path $cacheDir "HumanEvalPlus-v0.1.10.jsonl"
    if (Test-Path $defaultCache) {
        Write-Host "Found cached HumanEvalPlus: $defaultCache"
    } else {
        Write-Warning "HumanEvalPlus cache not found. First run requires network OR provide -OverridePath to a local jsonl."
    }
}