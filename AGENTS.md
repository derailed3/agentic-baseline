# Repository contract

This is the canonical instruction file for every agent working in this repository. Per-tool files (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) are pointers to it: edit this file, not the pointers. Procedure for one kind of task belongs in a skill under `.agents/skills/`, so it loads only when relevant.

## Start here

| Need | Read or run |
|---|---|
| What this repository is for | `README.md` |
| First session on a machine | `sh scripts/setup.sh` (macOS, Linux, cloud) or `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1` (Windows) |
| Which skill fits a task | `python .agents/skills/meta-skills-govern/scripts/find_skill.py "<task>"` |
| How to create, change, review or retire a skill | `.agents/skills/meta-skills-govern/SKILL.md` |
| Why something is the way it is | `decisions/` |

## Layout and ownership

| Path | Holds |
|---|---|
| `.agents/skills/` | Hand-written skills, the only copy you edit. `.agents/skills/README.md` indexes them |
| `.claude/skills/` | Ignored mirror of `.agents/skills/` for a tool that scans only its own folder; written by `scripts/deploy_skills.py`, kept current by the skill guard (`registry/skill-host.yaml` -> `mirrors`) |
| `.data/` | Ignored: everything the repository downloads or produces (models, samples, run output, scratch, helper tools). Nothing is written outside the repository |
| `scripts/` | Repository automation: setup, the worktree helper, deploy, verify, scans, branch protection |
| `tests/` | Tests for repository scripts, and trigger cases (`tests/trigger_cases.yaml`) |
| `registry/` | Project-specific settings that skills and scripts refer to by key |
| `decisions/` | Decision records, binding until replaced |
| `docs/` | Guides for people: everyday use, code-host setup |
| `.worktrees/` | Ignored; one folder per task |

## Non-negotiable rules

1. Work in a task worktree. Run `python scripts/task_worktree.py start <type>/<slug>` before the first write to any file in this repository, and work only inside the folder it prints. Only pure reads, and outside-system actions that touch no repository file, are exempt. Never commit to `main`.
2. Edit only `.agents/skills/`, never a generated copy. Skills are self-contained: never reach into another skill's folder or above your own. Every skill change bumps its version and adds a changelog section. Create and change skills through `.agents/skills/meta-skills-govern/`.
3. Write to outside systems only through a script made for that system that previews by default. Get explicit approval before any outside, irreversible or ambiguous write.
4. Never commit personal data, credentials, tokens or secrets. CI scans every change; a secret that reached history must be rotated, not just deleted.
5. Back every claim with a check, a test or a stated limitation. Say plainly when a check could not run.
6. Put temporary files in your own scratch folder, never in the repository and never at a drive root.

## Commands

    python scripts/verify.py                                   # everything the server checks, run locally
    python .agents/skills/meta-skills-govern/scripts/validate_skills.py   # the validator alone
    python scripts/run_tests.py                                # all tests (every tests/ folder)
    python scripts/deploy_skills.py                            # rewrite the skill mirrors (the guard does this on every checkout, merge, commit)
    python scripts/skill_guard.py install|status               # the repository-local git hooks that keep mirrors current and check skills before commit
    python scripts/task_worktree.py start|status|pr|finish|check|list ...

## Approval

Stop for a person's explicit approval before: pushing, opening or merging a pull request (unless the request already said so, below), publishing, sending mail, deleting anything, changing this file, `registry/`, `decisions/` or `.github/`, or weakening any check.

Merging is the person's act. This repository requires passing checks, not an approving vote, because a code host does not let a pull request's author approve their own change (`decisions/0004-approval-is-the-person-merging.md`). An agent never approves or votes on a pull request.

## Finishing a task

| The person says | You may | You may not |
|---|---|---|
| "Do this" | Change and verify in a worktree, then ask what next | Push, open a pull request, merge |
| "Do this and open a PR" | Commit, `task_worktree.py pr --apply`, report the link | Merge |
| "Do this and land it" | All of the above, and merge once the required checks pass | Bypass or weaken checks |

If the person did not say, stop with the change made and ask: keep refining, open a pull request, or land it when checks pass. "Urgent" never bypasses these rules. After a merge, run `task_worktree.py finish <slug>`.

Report the state you reached: implemented, committed, pull request opened, awaiting checks, merged, cleaned up. End with a receipt: files changed, checks run with their results, what you did not do and why, assumptions, next step.
