Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$scriptFile = Join-Path $PSScriptRoot 'extract_audio.py'
$pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (Test-Path $pythonExe) {
    & $pythonExe $scriptFile @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $scriptFile @args
} else {
    & python $scriptFile @args
}
exit $LASTEXITCODE
