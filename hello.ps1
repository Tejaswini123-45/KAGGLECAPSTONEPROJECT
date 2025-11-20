$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venv = Join-Path $scriptDir "crew_venv\Scripts\python.exe"

if (Test-Path $venv) {
    & $venv (Join-Path $scriptDir "chat.py") @args
} else {
    & python (Join-Path $scriptDir "chat.py") @args
}

Read-Host -Prompt "Press Enter to exit"
