# 0002: every change happens in its own task worktree

- Status: Accepted (2026-11-22)
- Affects: `AGENTS.md` rule 1, `scripts/task_worktree.py`, `.worktrees/`

## Context

Two agents, or an agent and a person, editing the same checkout overwrite each other's work, and work committed straight to the shared branch skips every check.

## Decision

Before the first write, `task_worktree.py start <type>/<slug>` creates a branch and a folder under `.worktrees/` from the freshly fetched shared branch. `pr` previews by default and pushes only with `--apply`. `finish` removes the worktree only when GitHub confirms a merged pull request whose head commit equals the worktree's commit, and fails closed otherwise. `check` fails when the shared branch carries local work.

## Consequences

Every change becomes a pull request. Pure reads, and outside-system actions that touch no repository file, are exempt.
