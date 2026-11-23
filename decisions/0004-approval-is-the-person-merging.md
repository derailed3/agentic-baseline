# 0004: approval is the person merging

- Status: Accepted (2026-11-22)
- Affects: `AGENTS.md` -> Approval and Finishing a task, `scripts/github_protect.py`

## Context

The pattern asks for an approving vote before merge. GitHub never lets a pull request's author approve their own change, so in a one-person repository a required vote would block every merge, and an agent casting the vote under the person's own sign-in would leave no record that it was agent-cast.

## Decision

Branch protection requires pull requests and passing checks, with zero required approving votes. The person's decision to merge is the approval. Agents never approve or vote. An agent merges only when the person said "land it" for that change, and only once the required checks pass.

## Consequences

Requester and approver are the same person; the required checks and the person's reading are the controls. When a second person joins, or agents open pull requests under their own identity, replace this record: require one approving vote from someone other than the author, and give agents a separate machine account so their actions are recorded apart.
