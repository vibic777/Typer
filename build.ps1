$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Test-PythonWithTk([string]$candidate, [switch]$Launcher) {
    try {
        if ($Launcher) {
            & $candidate -3 -c "import tkinter, sys; root=tkinter.Tk(); root.withdraw(); root.destroy(); print(sys.executable)" *> $null
        } else {
            & $candidate -c "import tkinter, sys; root=tkinter.Tk(); root.withdraw(); root.destroy(); print(sys.executable)" *> $null
        }
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Find-Python {
    $candidates = @(
        (Join-Path $PSScriptRoot ".build-python\python.exe"),
        "C:\Users\$env:USERNAME\AppData\Local\Python\bin\python.exe",
        "python",
        "py"
    )

    foreach ($candidate in $candidates) {
        try {
            if ($candidate -match '^[A-Za-z]:\\' -and -not (Test-Path -LiteralPath $candidate)) { continue }
            if ($candidate -eq "py" -and (Test-PythonWithTk $candidate -Launcher)) { return $candidate }
            if ($candidate -ne "py" -and (Test-PythonWithTk $candidate)) { return $candidate }
        } catch {
            continue
        }
    }

    $toolsDirectory = Join-Path $PSScriptRoot ".build-tools"
    $installer = Join-Path $toolsDirectory "python-3.13.7-amd64.exe"
    $localPython = Join-Path $PSScriptRoot ".build-python"
    New-Item -ItemType Directory -Force -Path $toolsDirectory | Out-Null

    if (-not (Test-Path -LiteralPath $installer)) {
        Write-Host "Downloading the official Python build runtime..."
        Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe" -OutFile $installer
    }

    Write-Host "Installing the local build runtime..."
    $arguments = "/quiet InstallAllUsers=0 TargetDir=`"$localPython`" Include_launcher=0 Include_test=0 Include_tcltk=1 Include_pip=1 Shortcuts=0 AssociateFiles=0 PrependPath=0"
    $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
    if ($process.ExitCode -ne 0) { throw "Local Python installation failed with code $($process.ExitCode)." }

    $installedPython = Join-Path $localPython "python.exe"
    if (-not (Test-PythonWithTk $installedPython)) { throw "The local Python runtime does not contain Tk." }
    return $installedPython
}

$venvPython = Join-Path $PSScriptRoot ".build-venv\Scripts\python.exe"

if ((Test-Path -LiteralPath $venvPython) -and -not (Test-PythonWithTk $venvPython)) {
    Write-Host "The existing build environment is invalid; recreating it..."
    $resolvedEnvironment = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".build-venv"))
    if (-not $resolvedEnvironment.StartsWith([System.IO.Path]::GetFullPath($PSScriptRoot), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a build environment outside the project."
    }
    Remove-Item -LiteralPath $resolvedEnvironment -Recurse -Force
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    $python = Find-Python
    Write-Host "Creating an isolated build environment..."
    if ($python -eq "py") {
        & $python -3 -m venv ".build-venv"
    } else {
        & $python -m venv ".build-venv"
    }
    if ($LASTEXITCODE -ne 0) { throw "Could not create the build environment." }
}

if (-not (Test-PythonWithTk $venvPython)) { throw "The build environment does not contain a working Python/Tk runtime." }

Write-Host "Installing build tools..."
& $venvPython -m pip install --disable-pip-version-check -r "requirements-build.txt"
if ($LASTEXITCODE -ne 0) { throw "Could not install PyInstaller." }

Write-Host "Creating the Windows icon..."
& $venvPython "build_icon.py"
if ($LASTEXITCODE -ne 0) { throw "Could not create the Windows icon." }

Write-Host "Building portable EXE..."
& $venvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "Typer" `
    --icon "icon.ico" `
    --add-data "icon.png;." `
    --version-file "version_info.txt" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "." `
    "typer.py"
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

$exe = Join-Path $PSScriptRoot "dist\Typer.exe"
if (-not (Test-Path -LiteralPath $exe)) { throw "Typer.exe was not created." }

Write-Host ""
Write-Host "Done: $exe" -ForegroundColor Green
Write-Host "The EXE is portable; Python is not required on the target computer."
