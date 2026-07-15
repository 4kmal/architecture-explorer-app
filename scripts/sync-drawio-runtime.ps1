param([string]$Source = $env:DRAWIO_SOURCE)

if ([string]::IsNullOrWhiteSpace($Source)) {
    throw 'Provide -Source or set DRAWIO_SOURCE to a local draw.io source checkout.'
}

$ErrorActionPreference = 'Stop'
$explorer = Split-Path -Parent $PSScriptRoot
$sourceWebapp = Join-Path $Source 'src\main\webapp'
$target = Join-Path $explorer 'vendor\drawio'

if (-not (Test-Path -LiteralPath $sourceWebapp)) {
    throw "Draw.io webapp source was not found: $sourceWebapp"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
Get-ChildItem -LiteralPath $sourceWebapp -Force | Copy-Item -Destination $target -Recurse -Force
Copy-Item -LiteralPath (Join-Path $Source 'LICENSE') -Destination (Join-Path $target 'LICENSE') -Force
Copy-Item -LiteralPath (Join-Path $Source 'README.md') -Destination (Join-Path $target 'UPSTREAM-README.md') -Force

$appJs = Join-Path $target 'js\diagramly\App.js'
$appSource = Get-Content -LiteralPath $appJs -Raw

if ($appSource -notmatch "'pkx': 'plugins/petakerja-explorer.js'") {
    $appSource = $appSource.Replace('App.pluginRegistry = {', "// Modified by PetaKerja Architecture Explorer: registers the local bridge plugin.`r`nApp.pluginRegistry = {'pkx': 'plugins/petakerja-explorer.js',")
    [System.IO.File]::WriteAllText($appJs, $appSource, [System.Text.UTF8Encoding]::new($false))
}

Write-Host 'Draw.io runtime copied and the pkx bridge registry entry applied.'
