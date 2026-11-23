# 0006: `.agents/skills/` is the source; a guard keeps the mirrors current

- Status: Accepted (2026-11-23)
- Supersedes: 0001
- Affects: `.agents/skills/`, `scripts/deploy_skills.py`, `scripts/skill_guard.py`, `registry/skill-host.yaml`, `.gitignore`, `scripts/setup.*`

## Context

0001 kept skills in a top-level `skills/` folder and generated a copy for every tool, including `.agents/skills/`. Codex and GitHub Copilot CLI read `.agents/skills/` directly, which is also where the owner's other repositories (ai-knowledge, jack-rubin) keep their skills, so one layout across repositories means a copy is not needed there. The copies were also only rewritten when someone ran the deploy script, so a fresh checkout or a merge left them missing or stale.

## Decision

`.agents/skills/` is the only hand-edited, tracked copy. Tools that scan only their own folder get a generated mirror listed under `mirrors:` in `registry/skill-host.yaml` (today `.claude/skills/`), ignored by Git. `scripts/skill_guard.py install` writes repository-local git hooks (in this repository's `.git/hooks`, shared by every worktree, nothing system-wide) that rewrite the mirrors after every checkout, merge, commit and rebase, and run the skill validator before a commit that touches `.agents/skills/`. Setup installs the guard. The hooks hold no logic and do nothing if the script is missing.

## Consequences

A fresh clone gets its mirror and hooks from setup; after that nobody runs the deploy step by hand. A hand edit to a mirror is overwritten on the next git operation. A clone without setup has no hooks; the server check (`deploy_skills.py --check` in verify) still catches a stale mirror in CI only where one exists, so setup remains the first step on every machine.
