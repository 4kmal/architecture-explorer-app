param([switch]$NoOpen)

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$runtimeDirectory = Join-Path $root '.runtime'
$runtimeFile = Join-Path $runtimeDirectory 'host.json'
$hostScript = Join-Path $root 'scripts\explorer-host.mjs'
$node = Get-Command node -ErrorAction SilentlyContinue

if (-not $node) {
    throw 'Node.js was not found. Install Node.js 20 or newer to run the local editor and Codex bridge.'
}

$runtime = $null
if (Test-Path -LiteralPath $runtimeFile) {
    try {
        $runtime = Get-Content -Raw -LiteralPath $runtimeFile | ConvertFrom-Json
        if (-not (Get-Process -Id $runtime.pid -ErrorAction SilentlyContinue)) {
            $runtime = $null
        } else {
            try {
                Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 -Uri "http://127.0.0.1:$($runtime.port)/api/bridge/status" | Out-Null
            } catch {
                $runtime = $null
            }
        }
    } catch {
        $runtime = $null
    }
}

if (-not $runtime) {
    New-Item -ItemType Directory -Force -Path $runtimeDirectory | Out-Null
    if (Test-Path -LiteralPath $runtimeFile) {
        Remove-Item -LiteralPath $runtimeFile -Force
    }
    Start-Process -FilePath $node.Source -ArgumentList @('scripts/explorer-host.mjs') -WorkingDirectory $root -WindowStyle Hidden
    for ($attempt = 0; $attempt -lt 60; $attempt += 1) {
        Start-Sleep -Milliseconds 100
        if (Test-Path -LiteralPath $runtimeFile) {
            try {
                $runtime = Get-Content -Raw -LiteralPath $runtimeFile | ConvertFrom-Json
                if ($runtime.port) { break }
            } catch {
                $runtime = $null
            }
        }
    }
}

if (-not $runtime.port) {
    throw 'The Explorer host did not start. Check whether ports 8080 through 8089 are available.'
}

$url = "http://127.0.0.1:$($runtime.port)/"
if ($NoOpen) { Write-Output $url }
else { Start-Process $url }
