Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectDir '.venv\Scripts\python.exe'
function Assert-Exit {
    if ($LASTEXITCODE -ne 0) { throw "Previous command failed: $LASTEXITCODE" }
}
if (-not (Test-Path $pythonExe)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
        Assert-Exit
        & py -3 -m venv (Join-Path $projectDir '.venv')
    } else {
        & python -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
        Assert-Exit
        & python -m venv (Join-Path $projectDir '.venv')
    }
    Assert-Exit
}
& $pythonExe -m pip install --upgrade pip
Assert-Exit
& $pythonExe -m pip install --upgrade --pre -r (Join-Path $projectDir 'requirements.txt')
Assert-Exit
$versions = & $pythonExe -m pip freeze
Assert-Exit
$versions | Set-Content -Encoding UTF8 (Join-Path $projectDir 'installed-versions.txt')
& $pythonExe (Join-Path $projectDir 'extract_audio.py') --doctor
exit $LASTEXITCODE
