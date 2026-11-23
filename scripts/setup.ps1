# One-step machine setup for Windows. Safe to run again.
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# Makes .venv with the Python packages, writes the per-tool skill copies, and runs every check.
# Installs nothing system-wide; if Python 3.10+ is missing it prints the command that installs it.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

$py = $null
foreach ($c in @('py', 'python', 'python3')) {
    if (-not (Get-Command $c -ErrorAction SilentlyContinue)) { continue }
    $extra = if ($c -eq 'py') { @('-3') } else { @() }
    & $c @extra -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $py = @($c) + $extra; break }
}
if (-not $py) {
    Write-Host "Python 3.10 or newer was not found. Install it with:"
    Write-Host "  winget install -e --id Python.Python.3.12"
    Write-Host "then open a new terminal and run this script again."
    exit 1
}

if (-not (Test-Path .venv\Scripts\python.exe)) {
    & $py[0] @($py | Select-Object -Skip 1) -m venv .venv
    Write-Host "created .venv"
}
$venvPy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $venvPy -m pip install -q --upgrade pip
& $venvPy -m pip install -q -r requirements.txt

& $venvPy scripts/deploy_skills.py
Write-Host ""
& $venvPy scripts/verify.py
$status = $LASTEXITCODE
Write-Host ""
Write-Host "Ready. Activate the environment in new terminals with:  .venv\Scripts\Activate.ps1"
Write-Host "Then start every task with:  python scripts/task_worktree.py start <type>/<slug>"
exit $status
