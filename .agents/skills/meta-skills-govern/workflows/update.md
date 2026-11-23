# Update a skill

1. **Read the whole skill first**: `SKILL.md` and every file under it. A router's behaviour lives in its workflows.
2. **Preserve intent.** Narrow or extend; do not silently reverse a rule. If a rule looks wrong, tell the person instead of deleting it.
3. **Edit only `.agents/skills/<name>/`**, never a generated copy.
4. **Bump `version` and write the changelog section in the same change**, newest first: PATCH for a fix, MINOR for something new that keeps old use working, MAJOR when old use breaks or a script moves.
5. **Re-check the description and keywords** if what the skill does changed: they are all an agent matches on. Update `tests/trigger_cases.yaml` with the requests the changed skill must win.
6. **Re-read the README** and fix it if it would now mislead someone who reads only it.
7. Run the validate-and-deploy block in `SKILL.md`, and report with a receipt.
