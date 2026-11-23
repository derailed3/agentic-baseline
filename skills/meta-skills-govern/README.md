# Meta Skills Govern

**The skill that looks after all the other skills: it creates, changes, reviews and retires them, and finds which one fits a task.**

Ask your agent in plain words, for example "make a skill that turns meeting notes into a checklist", "which skill should I use to draft a status report?", or "review the notes skill". The agent follows this skill so every skill ends up with the same shape: a guide for the agent, a page for people, a changelog, a version number, and checks that prove the shape is right.

## What you get

- A new or changed skill in its own folder, validated, indexed and visible to every agent tool.
- For "which skill fits": the top matches and why each matched.
- For a review: a list of findings with proposed fixes; nothing changes until you pick.

## Where things live

- `SKILL.md` routes each request to a workflow in `workflows/`.
- `reference/conventions.md` is the layout, naming and rule list every skill follows.
- `scripts/validate_skills.py` checks every skill; `scripts/find_skill.py` ranks skills against a request; `tests/` checks both.
