---
name: meta-skills-govern
description: >-
  Create, update, review or retire a skill in this repository, or find which skill fits a task.
  Use for "make a skill for...", "change the X skill", "review this skill", "retire a skill",
  "which skill should I use", or when a skill fails validation.
version: 0.2.1
distribution: repository
generality: general
tags:
  - domain:skills
  - pattern:router
keywords:
  - "rx:\\b(create|make|build|write|add|new)\\b.{0,30}\\bskills?\\b"
  - "rx:\\b(update|change|fix|edit|improve|review|retire|delete|rename)\\b.{0,30}\\bskills?\\b"
  - which skill
  - skill validation
  - skill fails validation
---

# Meta Skills Govern

The one skill whose subject is skills: every skill is created, changed, reviewed and retired through it, so the library stays consistent as it grows.

## When to Use

- Someone wants a new skill, or a change to, review of, or retirement of an existing one.
- Someone asks which skill fits a task, or a skill fails `validate_skills.py`.
- Not for doing the task a skill covers; load that skill instead.

## Routing

| Request | Read |
|---|---|
| Find which skill fits, or check for overlap | Run `scripts/find_skill.py "<request>"`; read the top skills' descriptions |
| Create a skill | `workflows/create.md` |
| Change a skill (fix, extend, rename a section) | `workflows/update.md` |
| Review a skill for quality and drift | `workflows/review.md` |
| Retire a skill | `workflows/retire.md` |
| The layout, frontmatter, naming and validator rules | `reference/conventions.md` |

Every route that changes files starts in a task worktree (`AGENTS.md` rule 1) and ends with the validate-and-deploy block below.

## Parameters

| Input | Required | Default |
|---|---|---|
| The request in the person's words | Yes | None; ask |
| The skill's name, for update, review or retire | For those routes | Found with `scripts/find_skill.py` |

## Validate and deploy

Run from the worktree root after any skill change, and report each result:

    python .agents/skills/meta-skills-govern/scripts/validate_skills.py
    python scripts/run_tests.py
    python scripts/deploy_skills.py

## Output Format

A receipt (`AGENTS.md` -> Finishing a task): the skill and its new version, the files changed, the validator and test results with numbers, and the next step the person chose.

## Error Handling

| Symptom | Cause | Fix |
|---|---|---|
| `R4` name does not equal the folder name | Renamed one but not the other | Make them equal; a rename is a retire plus a create (`workflows/retire.md`) |
| `R8` changelog version differs | Bumped `version` without a changelog section, or the reverse | Add the `## [X.Y.Z] - YYYY-MM-DD` section, newest first |
| `R10` workflow not named in routing | Added a workflow file without a routing row | Add the row, or delete the file |
| `R13` not listed in the index | New skill missing from `.agents/skills/README.md` | Add its row |
| An agent cannot see a new skill | Copies not refreshed, or the tool cached its list | Run `scripts/deploy_skills.py`, then start a new session |
| Two skills both match a request | Overlapping descriptions | Narrow one description, or merge (`workflows/review.md`) |
