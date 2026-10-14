param(
    [switch]$IncludeDist,
    [switch]$IncludeBuildEnvironment
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$targets = @(
    (Join-Path $PSScriptRoot "build"),
    (Join-Path $PSScriptRoot "__pycache__")
)

if ($IncludeDist) {
    $targets += Join-Path $PSScriptRoot "dist"
}
if ($IncludeBuildEnvironment) {
    $targets += Join-Path $PSScriptRoot ".build-venv"
    $targets += Join-Path $PSScriptRoot ".build-python"
    $targets += Join-Path $PSScriptRoot ".build-tools"
}

foreach ($target in $targets) {
    $resolvedParent = [System.IO.Path]::GetFullPath((Split-Path -Parent $target))
    $projectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
    if ($resolvedParent -ne $projectRoot) {
        throw "Refusing to remove a path outside the project: $target"
    }
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed: $target"
    }
}

Write-Host "Cleanup complete." -ForegroundColor Green
