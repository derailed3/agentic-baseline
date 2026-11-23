# Notes Actions Extract

**Turns meeting notes into a checklist of their action items, so nothing agreed in a meeting gets lost.**

Ask your agent "what are the action items in these notes?" and give it the file. Lines that start with `Action:` or `TODO:` (with or without a bullet) become a checklist, in order:

```text
- [ ] send the draft to the team
- [ ] book the room
```

It never invents items: if none are marked, it says so and asks how your notes mark them.

This skill is also the repository's worked example of a complete skill: a guide, one workflow, one script and its test.
