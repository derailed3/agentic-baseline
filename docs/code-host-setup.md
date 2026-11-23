# Code-host setup

One-time steps for the builder, on GitHub. Settings for this repository live in `registry/code-host.yaml`.

## 1. Create the repository and push

    gh repo create <owner>/<repo> --public --source . --push      # or --private

## 2. Make the server check required

    python scripts/github_protect.py            # preview
    python scripts/github_protect.py --apply    # apply (repository admin)

This requires a pull request for every change to `main` (administrators included), requires every job in `.github/workflows/checks.yml` to pass on the latest commit, and blocks force-pushes and deletion. It requires no approving vote (`decisions/0004-approval-is-the-person-merging.md`). Also turn on *Automatically delete head branches* in the repository settings.

A pipeline file existing does not mean it is enforced. Prove it:

1. `python scripts/task_worktree.py start fix/prove-required-check`, break a skill on purpose (for example set its `version` to `x`), commit, and open a pull request (`pr --apply`).
2. Confirm GitHub shows the `verify` jobs failing and refuses to merge.
3. Close the pull request without merging, then remove the worktree and branch by hand (`git worktree remove`, `git branch -D`), since `finish` only cleans up merged work.

## 3. Two GitHub accounts on one machine

If you use one GitHub account for work and another for this repository, route by the repository's URL instead of switching accounts.

1. Sign the GitHub CLI in to both: `gh auth login` once per account (`gh auth status` lists them).
2. In your global Git config, turn on path matching for GitHub and send this owner's URLs to that account's token:

```ini
[credential "https://github.com"]
    useHttpPath = true
[credential "https://github.com/<owner>"]
    helper =
    helper = "!f() { test \"$1\" = get || exit 0; echo username=<owner>; echo password=$(gh auth token -u <owner>); }; f"
```

3. Commit under the right email automatically for repositories with that remote, with `~/.gitconfig-<owner>` holding a `[user]` section with that account's email. Add the remote before the first commit.

```ini
[includeIf "hasconfig:remote.*.url:https://github.com/<owner>/**"]
    path = ~/.gitconfig-<owner>
```

4. The repository's own scripts call the GitHub CLI as `gh_account` from `registry/code-host.yaml`, without changing the active account.

Check it: `printf "protocol=https\nhost=github.com\npath=<owner>/x.git\n\n" | git credential fill` should print `username=<owner>`.
