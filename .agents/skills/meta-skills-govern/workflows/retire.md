# Retire a skill

1. **Confirm with the person.** A skill is cheap to keep and costly to rebuild; retire only on an explicit instruction for this skill.
2. **Find every reference**: `git grep -n "<name>"` across the repository (other skills, `tests/trigger_cases.yaml`, `.agents/skills/README.md`, `AGENTS.md`, `docs/`).
3. **Delete the folder** `.agents/skills/<name>/`, its row in `.agents/skills/README.md` and its trigger cases. Point any skill that relied on it elsewhere, with a version bump of its own.
4. A rename is a retire plus a create in the same change: the new skill's changelog names the old one.
5. Run the validate-and-deploy block in `SKILL.md`; the deploy step removes the retired skill from every generated copy. Report with a receipt.
