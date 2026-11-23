# 0001: skills/ is the only copy of each skill

- Status: Superseded by 0006 (2026-11-23)
- Affects: `skills/`, `scripts/deploy_skills.py`, `registry/skill-targets.txt`, `.gitignore`

## Context

Agent tools look for skills in different folders, and some scan only their own. Keeping a hand-edited copy per tool means the copies drift and nobody knows which is right.

## Decision

`skills/` holds the only hand-written copy of every skill. `scripts/deploy_skills.py` copies it to each folder listed in `registry/skill-targets.txt`; those copies are ignored by Git, carry a marker file, and are never edited. A new tool is added by measuring where it looks (a probe skill) and adding one line to the registry.

## Consequences

A fresh clone has no copies until setup runs. A hand edit to a copy is lost on the next deploy, and `deploy_skills.py --check` reports the divergence first.
