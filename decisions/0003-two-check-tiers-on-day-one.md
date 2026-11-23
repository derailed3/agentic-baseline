# 0003: day one runs two check tiers

- Status: Accepted (2026-11-22)
- Affects: `scripts/verify.py`, `.github/workflows/checks.yml`, `scripts/github_protect.py`

## Context

The pattern has three check tiers: the agent's own checks, a commit hook on the machine, and the required server check. The hook can be bypassed with one flag, so it catches mistakes early but enforces nothing.

## Decision

Day one runs tier 1 (`scripts/verify.py`, which the agent runs and reports before every pull request) and tier 3 (`checks.yml`, required by branch protection on `main`, for administrators too). A commit hook may come later, and if it does it is installed in this repository only, never machine-wide.

## Consequences

Until a hook exists, run `scripts/deploy_skills.py` by hand after a skill change. The server check is the one that cannot be skipped.
