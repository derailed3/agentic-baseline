# Decisions

Why the repository works the way it does. A record is binding until a new record replaces it; a change that would contradict one names it and replaces it explicitly. Ids are four digits and never renumbered.

Each record states its status, the context, the decision, its consequences, and what it affects, so anyone changing an affected file knows to re-read it.

| Id | Decision | Status |
|---|---|---|
| [0001](0001-skills-folder-is-the-only-copy.md) | `skills/` is the only copy of each skill; per-tool copies are generated | Accepted |
| [0002](0002-work-happens-in-a-task-worktree.md) | Every change happens in its own task worktree and branch | Accepted |
| [0003](0003-two-check-tiers-on-day-one.md) | Day one runs two check tiers: the agent's own and the required server check | Accepted |
| [0004](0004-approval-is-the-person-merging.md) | Approval is the person merging; no required vote, agents never vote | Accepted |
| [0005](0005-secrets-and-personal-data-are-scanned-on-the-server.md) | Secrets and personal data are scanned as a required server check | Accepted |
