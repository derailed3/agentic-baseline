# Conventions

What every skill in this repository looks like, and the rules the validator enforces. Short on purpose: it is read on every create and update.

## Layout

```text
.agents/skills/<skill-name>/
|-- README.md        required: the guide for people
|-- SKILL.md         required: the main guide for the agent, with frontmatter
|-- CHANGELOG.md     required: one section per version, newest first
|-- workflows/       one file per intent, named in SKILL.md's routing table
|-- reference/       lookup tables, templates, known traps
|-- scripts/         automation the agent runs
|-- tests/           tests of the scripts (test_*.py, run by unittest), kept apart from them
|-- examples/        small, individually valid samples
|-- schemas/         versioned, frozen schemas for file formats the skill reads or writes
|-- sources.yaml     the outside things the skill rests on, with the date each was checked
`-- docs/TODO.md     the living backlog: built, proven, open
```

Only the three files at the top are required. Any other folder is fine when the skill says what belongs in it. Group files before a folder passes about a dozen. Name folders by lasting purpose (`reference/`, not `round2/`).

## Frontmatter

```yaml
---
name: notes-actions-extract        # equals the folder name
description: >-                     # what it does and when to use it, in the words people type; under ~400 characters
  ...
version: 1.0.0                      # MAJOR.MINOR.PATCH; every change bumps it
distribution: portable              # portable: runs from its own folder anywhere | repository: needs this repo's scripts or registry
generality: general                 # general: a range of requests | specific: one named job (then add context, owner role, review_by)
tags: [domain:notes, pattern:standalone]   # pattern: router | standalone | internal
keywords:                           # phrases people use; "rx:" marks a regular expression
  - action items
---
```

## Naming

`{domain}-{resource}-{action}`, lowercase letters, digits and hyphens, for example `notes-actions-extract`; a router skill may be `{domain}-{resource}`. Name by the job, not the tool.

## Body order of SKILL.md

Title and one-line purpose; **When to Use** (and when not); **Routing** (intent to workflow) or **Execution** (steps); **Parameters**; **Output Format**; **Error Handling** (symptom, cause, fix). Keep it under about 150 lines; move phase detail into `workflows/`.

## Rules

1. **Self-contained.** A skill uses only files in its own folder, plus repository files it declares in frontmatter (`uses_repo`) and registry keys (`config`). Never a path into another skill, and never a parent-folder step out of your own.
2. **Project-agnostic.** No deployment values (owner names, ids, URLs of one project, people) in a skill: they live in `registry/` and the skill names the key.
3. **Every change bumps the version** and adds a changelog section: PATCH for a fix, MINOR for something new that keeps old use working, MAJOR when old use breaks or a script moves.
4. **No point-in-time content** in procedures (dates, counts, run results, screenshots). Those go in the changelog, the backlog or your scratch folder.
5. **One paragraph per line** in Markdown; no hard wrapping.
6. **Agent-neutral wording.** Do not name a specific agent tool in a skill.
7. **Trigger cases.** Add the requests a new or changed skill must win to `tests/trigger_cases.yaml`.

## Validator rules (`scripts/validate_skills.py`)

| Id | Rule |
|---|---|
| R1 | The folder has `README.md`, `SKILL.md` and `CHANGELOG.md` |
| R2 | `SKILL.md` starts with frontmatter that parses as YAML |
| R3 | The frontmatter has `name`, `description` and `version` |
| R4 | `name` equals the folder name |
| R5 | `name` is lowercase letters, digits and hyphens, in two or three parts |
| R6 | `description` is at most 1024 characters (a warning above 400) |
| R7 | `version` is `MAJOR.MINOR.PATCH` |
| R8 | The newest `CHANGELOG.md` version equals the frontmatter `version` |
| R9 | `SKILL.md` has "When to Use"; a skill with `scripts/` or a code block also has "Parameters" and "Error Handling" |
| R10 | Every workflow SKILL.md names exists, and every file in `workflows/` is named |
| R11 | No file reaches into another skill's folder or climbs out of its own (a parent-folder step) |
| R12 | No file contains an absolute path |
| R13 | Every skill is listed in `.agents/skills/README.md` |
| R14 | No run-evidence folders (`evidence`, `rounds`, `runs`, `scratch`) outside test fixtures |
| R15 | Text files use LF line endings |
| R16 | `SKILL.md` is at most 500 lines (a warning above 150) |
