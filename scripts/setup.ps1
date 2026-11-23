# One-step machine setup for Windows. Safe to run again.
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# Makes .venv with the Python packages, writes the skill mirrors, installs the skill guard (repository-local
# git hooks that keep the mirrors current), and runs every check.
# Installs nothing system-wide; if Python 3.10+ is missing it prints the command that installs it.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

# Find Python 3.10+ and ask it for its own full path. Arguments are written literally: splatting an
# array holding '-3' turns it into '-' '3' in Windows PowerShell, and 'py -' then waits on stdin forever.
$probe = "import sys; print(sys.executable if sys.version_info >= (3, 10) else '')"
$exe = $null
foreach ($c in @('python', 'python3', 'py')) {
    if (-not (Get-Command $c -ErrorAction SilentlyContinue)) { continue }
    # The Microsoft Store 'python' alias writes to stderr; under 'Stop' that would end the script, so probe in try.
    try { $out = if ($c -eq 'py') { & py -3 -c $probe 2>$null } else { & $c -c $probe 2>$null } } catch { continue }
    if ($LASTEXITCODE -eq 0 -and $out -and (Test-Path ($out | Select-Object -Last 1))) { $exe = ($out | Select-Object -Last 1); break }
}
if (-not $exe) {
    Write-Host "Python 3.10 or newer was not found. Install it with:"
    Write-Host "  winget install -e --id Python.Python.3.12"
    Write-Host "then open a new terminal and run this script again."
    exit 1
}

if (-not (Test-Path .venv\Scripts\python.exe)) {
    & $exe -m venv .venv
    Write-Host "created .venv with $exe"
}
$venvPy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $venvPy -m pip install -q --upgrade pip
& $venvPy -m pip install -q -r requirements.txt

& $venvPy scripts/deploy_skills.py
& $venvPy scripts/skill_guard.py install
Write-Host ""
& $venvPy scripts/verify.py
$status = $LASTEXITCODE
Write-Host ""
Write-Host "Ready. Activate the environment in new terminals with:  .venv\Scripts\Activate.ps1"
Write-Host "Then start every task with:  python scripts/task_worktree.py start <type>/<slug>"
exit $status
