# Review a skill

Report findings; change nothing until the person picks which to fix (then `update.md`).

1. Run the validator and the skill's tests; record the results.
2. Rank three realistic requests with `scripts/find_skill.py`. The skill should win its own requests and lose others'. Two skills that win the same requests overlap: propose narrowing one description or merging them.
3. Read `SKILL.md` as an agent would: is every step doable from the text alone, is each command complete, does the error table cover the traps the backlog or changelog mention?
4. Read the README as a newcomer: could they use the skill without asking anyone?
5. Check drift: outside tools or pages it relies on (`sources.yaml` if present) still behave as written; no point-in-time content crept into procedures; folders still fit `reference/conventions.md` -> Layout.
6. Report each finding with the file, the problem, and a proposed fix, most important first.
