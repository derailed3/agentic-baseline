# Everyday use

How to work with an agent in this repository, safely, whether or not you write code.

## A first session

1. Open your agent in the repository folder. If setup has never run on this machine, ask: *"Set up this repository: read AGENTS.md and run the first-session setup."*
2. Ask questions first; nothing is written, so nothing can break: *"What does this repository do?"*, *"Which skills exist?"*, *"Which skill would I use to list the action items in my notes?"*
3. Ask a skill to produce something outside the repository: *"List the action items in this notes file."*
4. Ask for a small change, and say where to stop: *"Fix the typo in the notes skill's README. Do this."* The agent starts a task worktree, makes the change, bumps the skill's patch version, runs the checks and stops.
5. Before a bigger change, ask for the plan: *"Before changing anything, tell me how you would add X and which files you would touch."*

## How to phrase a request

Name four things: **the outcome** (what should exist or be true), **the context** (which skill, file or system), **the limits** (what not to touch, what to ask first) and **the endpoint**:

| You say | The agent may | It may not |
|---|---|---|
| "Do this" | Change and verify in a worktree, then ask what next | Push, open a pull request, merge |
| "Do this and open a PR" | Commit, push and open the pull request | Merge |
| "Do this and land it" | All of that, and merge once the required checks pass | Bypass or weaken checks |

## Reading the receipt

Every agent finishes with a receipt. Check five things:

1. **The state**: implemented, committed, pull request opened, awaiting checks, merged, cleaned up. "Done" without a state is a warning sign.
2. **The files**: they match what you asked for. Ask about any surprise, especially `AGENTS.md`, `registry/`, `decisions/` or `.github/`.
3. **The checks, with numbers**: "22 tests passed" is evidence; "I ran the tests" is not. A SKIPPED check says why, and SKIPPED never means passed.
4. **The assumptions**: each is a decision made for you; correct any you disagree with.
5. **The next step**: it matches the endpoint you asked for.

## When to stop the agent

- It wants to send, publish, delete or close something and you are not sure of the effect.
- It proposes to change `AGENTS.md`, a decision record, the checks or the registry.
- Its receipt has no evidence, or claims a check passed that did not run.
- It tried the same thing twice and failed both times, or asks to bypass a check.
- The change touches personal data, credentials or secrets.
- You cannot explain in your own words what the change does.

## Habits that help

- One task per session where you can; long sessions blur the agent's memory.
- When an agent repeats a mistake, ask it to add the lesson to the skill's Error Handling table (through `meta-skills-govern`), or to propose a validator rule.
- Never edit `.claude/skills/` or `.agents/skills/`; they are regenerated from `skills/`.

## Adding an agent tool

1. Find the file name the tool reads for instructions and add a one-line pointer file under that name: *"Read and follow `AGENTS.md` at the repository root; it is the canonical instruction file. Edit that file, not this one."* Add it to `registry/layout.txt` if it sits at the root.
2. Find where it looks for skills with a probe: make a throwaway skill with a unique name in a candidate folder, start a new session, and ask the agent which skills it can see.
3. If it does not read an existing copy folder, add its folder to `registry/skill-targets.txt` and `.gitignore`, run `python scripts/deploy_skills.py`, and confirm the probe again.
