# Registry

Project-specific settings, read by key. Skills never hold these values; they name the key and the script that reads it. The registry holds pointers (an owner, a branch name, a list of folders), never inventories that change on someone else's schedule.

| File | Holds | Read by |
|---|---|---|
| `code-host.yaml` | The code host, owner, repository, shared branch and the account to act as | `scripts/task_worktree.py`, `scripts/github_protect.py` |
| `skill-targets.txt` | The folders agent tools scan for skills | `scripts/deploy_skills.py` |
| `layout.txt` | The declared top-level entries | `scripts/verify.py` |

Changing a registry file needs a person's approval (`AGENTS.md` -> Approval).
