#!/bin/sh
# One-step machine setup for macOS, Linux and cloud workspaces. Safe to run again.
#   sh scripts/setup.sh
# Makes .venv with the Python packages, writes the skill mirrors, installs the skill guard (repository-local
# git hooks that keep the mirrors current), and runs every check.
# Installs nothing system-wide; when Python 3.10+ or its venv module is missing, it uses uv,
# which installs into your home folder without admin rights.
set -eu
cd "$(dirname "$0")/.."

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done

if [ ! -x .venv/bin/python ]; then
  if [ -n "$PY" ] && "$PY" -m venv .venv 2>/dev/null; then
    echo "created .venv with $PY"
  else
    rm -rf .venv
    if ! command -v uv >/dev/null 2>&1; then
      echo "installing uv (no admin rights needed) to make the virtual environment"
      curl -LsSf https://astral.sh/uv/install.sh | sh
      PATH="$HOME/.local/bin:$PATH"; export PATH
    fi
    uv venv --python 3.12 .venv
  fi
fi

. .venv/bin/activate
if python -m pip --version >/dev/null 2>&1; then
  python -m pip install -q --upgrade pip
  python -m pip install -q -r requirements.txt
else
  uv pip install -q -r requirements.txt
fi

python scripts/deploy_skills.py
python scripts/skill_guard.py install
echo
python scripts/verify.py
echo
echo "Ready. Activate the environment in new terminals with:  . .venv/bin/activate"
echo "Then start every task with:  python scripts/task_worktree.py start <type>/<slug>"
