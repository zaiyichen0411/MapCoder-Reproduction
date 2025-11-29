param(
    [string]$Root = "$(Get-Location)",
    [string]$Version = "v0.1.10",
    [string]$GzPath = "",
    [string]$JsonlOutPath = "",
    [string]$JsonlSourcePath = "",
    [string]$Url = "",
    [int]$TimeoutSec = 120,
    [string]$Proxy = "",
    [switch]$ProxyDefaultCreds,
    [switch]$UseCurl,
    [string]$ProxyUser = "",
    [string]$ProxyPass = "",
    [switch]$Download,
    [switch]$CopyToCache,
    [switch]$SetOverride,
    [switch]$RunAll
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Warning $msg }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$CacheDir = Join-Path $env:LOCALAPPDATA "evalplus\evalplus\Cache"
if (!(Test-Path $CacheDir)) { New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null }

function Decompress-GzipToJsonl([string]$gz, [string]$outJsonl) {
    Write-Info "Decompressing: $gz -> $outJsonl"
    $in = [IO.File]::OpenRead($gz)
    try {
        $gzip = New-Object IO.Compression.GzipStream($in, [IO.Compression.CompressionMode]::Decompress)
        $out = [IO.File]::Create($outJsonl)
        try {
            $buffer = New-Object byte[] 8192
            while (($read = $gzip.Read($buffer, 0, $buffer.Length)) -gt 0) {
                $out.Write($buffer, 0, $read)
            }
        } finally {
            $out.Dispose()
            $gzip.Dispose()
        }
    } finally {
        $in.Dispose()
    }
    Write-Info "Decompressed JSONL created: $outJsonl"
}

function Ensure-Dir([string]$path) {
    $dir = Split-Path -Path $path -Parent
    if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
}

$finalJsonl = $null

try {
    if ($JsonlSourcePath) {
        if (!(Test-Path $JsonlSourcePath)) { throw "JsonlSourcePath not found: $JsonlSourcePath" }
        Write-Info "Using existing JSONL: $JsonlSourcePath"
        $finalJsonl = $JsonlSourcePath
        if ($CopyToCache) {
            $cacheTarget = Join-Path $CacheDir "HumanEvalPlus-$Version.jsonl"
            Write-Info "Copying to cache: $cacheTarget"
            Copy-Item -Force -Path $finalJsonl -Destination $cacheTarget
            $finalJsonl = $cacheTarget
        } elseif ($JsonlOutPath) {
            Ensure-Dir $JsonlOutPath
            Write-Info "Copying to: $JsonlOutPath"
            Copy-Item -Force -Path $finalJsonl -Destination $JsonlOutPath
            $finalJsonl = $JsonlOutPath
        }
    } elseif ($GzPath) {
        if (!(Test-Path $GzPath)) { throw "GzPath not found: $GzPath" }
        if (-not $JsonlOutPath) {
            $gzDir = Split-Path -Path $GzPath -Parent
            $JsonlOutPath = Join-Path $gzDir "HumanEvalPlus-$Version.jsonl"
        }
        Ensure-Dir $JsonlOutPath
        Decompress-GzipToJsonl -gz $GzPath -outJsonl $JsonlOutPath
        $finalJsonl = $JsonlOutPath
        if ($CopyToCache) {
            $cacheTarget = Join-Path $CacheDir "HumanEvalPlus-$Version.jsonl"
            Write-Info "Copying to cache: $cacheTarget"
            Copy-Item -Force -Path $finalJsonl -Destination $cacheTarget
            $finalJsonl = $cacheTarget
        }
    } elseif ($Download) {
        if (-not $Url -or $Url -eq "") {
            $Url = "https://github.com/evalplus/humanevalplus_release/releases/download/$Version/HumanEvalPlus.jsonl.gz"
        }
        $tmpGz = Join-Path $env:TEMP "HumanEvalPlus-$Version.jsonl.gz"
        Write-Info "Downloading: $Url"
        try {
            if ($UseCurl) {
                Write-Info "Using curl.exe fallback"
                $args = @('-L', '--max-time', $TimeoutSec, '-o', $tmpGz)
                if ($Proxy -ne "") { $args += @('--proxy', $Proxy) }
                if ($ProxyUser -ne "") { $args += @('--proxy-user', "${ProxyUser}:${ProxyPass}") }
                $args += $Url
                $p = Start-Process -FilePath "curl.exe" -ArgumentList $args -Wait -PassThru -NoNewWindow
                if ($p.ExitCode -ne 0) { throw "curl exit code $($p.ExitCode)" }
            } else {
                $iwParams = @{ Uri = $Url; OutFile = $tmpGz; UseBasicParsing = $true; TimeoutSec = $TimeoutSec; Headers = @{ 'User-Agent' = 'Mozilla/5.0' } }
                if ($Proxy -ne "") {
                    $iwParams['Proxy'] = $Proxy
                    $iwParams['ProxyUseDefaultCredentials'] = [bool]$ProxyDefaultCreds
                    if ($ProxyUser -ne "") {
                        $secure = ConvertTo-SecureString $ProxyPass -AsPlainText -Force
                        $cred = New-Object System.Management.Automation.PSCredential($ProxyUser, $secure)
                        $iwParams['ProxyCredential'] = $cred
                    }
                }
                Invoke-WebRequest @iwParams
            }
        } catch {
            Write-Warn "Primary download failed: $($_.Exception.Message)"
            Write-Info "Trying BITS transfer fallback"
            try {
                Start-BitsTransfer -Source $Url -Destination $tmpGz -ErrorAction Stop
            } catch {
                Write-Err "Download failed: $($_.Exception.Message)"
                throw
            }
        }
        if (-not $JsonlOutPath) { $JsonlOutPath = Join-Path $CacheDir "HumanEvalPlus-$Version.jsonl" }
        Ensure-Dir $JsonlOutPath
        Decompress-GzipToJsonl -gz $tmpGz -outJsonl $JsonlOutPath
        $finalJsonl = $JsonlOutPath
    } else {
        throw "Please provide -JsonlSourcePath or -GzPath or -Download"
    }

    if ($SetOverride) {
        Write-Info "Setting HUMANEVAL_OVERRIDE_PATH to: $finalJsonl"
        $env:HUMANEVAL_OVERRIDE_PATH = $finalJsonl
    }

    if ($RunAll) {
        $runner = Join-Path $Root "scripts\run_evalplus_qwen_all.ps1"
        if (!(Test-Path $runner)) { throw "Runner script not found: $runner" }
        Write-Info "Launching: run_evalplus_qwen_all.ps1 -OverridePath $finalJsonl"
        & powershell -ExecutionPolicy Bypass -File $runner -OverridePath $finalJsonl
    } else {
        Write-Info "Prepared JSONL: $finalJsonl"
        Write-Info "You can now run: powershell -ExecutionPolicy Bypass -File scripts\run_evalplus_qwen_all.ps1 -OverridePath `"$finalJsonl`""
    }
} catch {
    Write-Err "Failed: $($_.Exception.Message)"
    exit 1
}