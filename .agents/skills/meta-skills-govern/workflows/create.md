# Create a skill

1. **Is a skill the right container?** A skill is for a recurring task with steps worth writing down. A one-off belongs in a request; a rule for every task belongs in `AGENTS.md` (needs approval); durable reasoning belongs in a decision record.
2. **Search for overlap.** Run `python .agents/skills/meta-skills-govern/scripts/find_skill.py "<the request in the person's words>"`. If an existing skill scores well, read it: extending it (`update.md`) usually beats a new skill. When the top two are close, show the person both before creating a third.
3. **Classify it.** Choose `distribution` (portable or repository) and `generality` (general or specific) with the person, and the name by `reference/conventions.md` -> Naming.
4. **Gather requirements.** The requests it must answer, in the person's words; the inputs and defaults; what it produces; what it must never do; any software it needs (then it gets a `workflows/setup.md` with per-platform install steps and a check script).
5. **Lay it out, then write it.** Create `.agents/skills/<name>/` with `SKILL.md`, `README.md` and `CHANGELOG.md` (version `0.1.0`, section `### Added`), plus only the folders it needs. Follow the body order in `reference/conventions.md`. Write the README for a person who has never used it: what it does, an example, what it needs.
6. **Index and triggers.** Add a row to `.agents/skills/README.md`, and two or more cases to `tests/trigger_cases.yaml` that must rank the new skill first.
7. **Prove it.** Run it once on a real or realistic request. Add a test for each script. Then run the validate-and-deploy block in `SKILL.md`, and report with a receipt.
