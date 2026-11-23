# Contributing

Whether the change comes from a person or an agent, it follows the same path.

1. **Start a task worktree.** `python scripts/task_worktree.py start <type>/<slug>` (types: feature, fix, docs, skill, chore, batch). Work only in the folder it prints. Never commit to `main`.
2. **Change skills through the meta-skill.** `skills/meta-skills-govern/SKILL.md` routes create, update, review and retire. Edit only `skills/`; every skill change bumps its `version` and adds a `CHANGELOG.md` section; add trigger cases to `tests/trigger_cases.yaml` for the requests a skill must win.
3. **Verify.** `python scripts/verify.py` runs what the server runs. Fix every FAIL; a SKIPPED check runs in CI.
4. **Open a pull request.** Write the description in a file (the template in `.github/pull_request_template.md` lists what to include), then `python scripts/task_worktree.py pr --title "..." --body-file <file>` to preview and add `--apply` to push and open it.
5. **Merge when the checks pass.** Merging is the person's decision; an agent merges only when told "land it" for that change, and never approves or votes.
6. **Clean up.** `python scripts/task_worktree.py finish <slug>` removes the worktree once GitHub confirms the pull request merged at that exact commit.

Changes to `AGENTS.md`, `registry/`, `decisions/` or `.github/` need the person's explicit approval in the request, and deserve a slower read. A new top-level file or folder is declared in `registry/layout.txt` and `AGENTS.md` in the same pull request.

Never commit personal data, credentials, tokens or secrets. The scans will catch most; if one reaches history, rotate the secret, do not just delete the line.
