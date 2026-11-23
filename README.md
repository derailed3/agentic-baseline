# Agentic Baseline

**A repository set up so AI coding agents can do real work in it safely: one instruction file every agent reads, a library of self-contained skills, a separate workspace per task, and checks that run before anything merges.**

Agents are fast and confident but forgetful. The structure here supplies the memory (skills), the rules (`AGENTS.md`) and the proof (checks on every pull request). It works with any agent tool that reads an instruction file and runs commands, such as Claude Code, GitHub Copilot, Codex, Cursor or Gemini CLI, on macOS, Windows, Linux or a cloud workspace.

## Start

1. Clone the repository and open your agent in its folder.
2. Ask it: *"Set up this repository on this machine: read AGENTS.md and run the first-session setup."* Or run the setup yourself:

   ```
   sh scripts/setup.sh                                          # macOS, Linux, cloud workspace
   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1   # Windows
   ```

   It makes a Python environment, writes the copies of the skills each agent tool reads, and runs every check. It should end with `verify: all checks passed`.
3. Ask for something. Good first requests: *"What does this repository do?"*, *"Which skill would I use to list the action items in my notes?"*, *"Make a skill that drafts my weekly status report."* For anything that changes files, say where to stop: **do this** (change and verify, then ask), **do this and open a PR**, or **do this and land it**. [Everyday use](docs/everyday-use.md) walks through a first session.

## How it fits together

| Piece | Where | What it does |
|---|---|---|
| The instruction file | `AGENTS.md` (pointers: `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) | The rules every agent reads first: where to work, what never to do, how to finish |
| Skills | `skills/` | One folder per recurring task: a guide for the agent, a page for people, a changelog, scripts and tests. Agents read a skill only when a request matches it |
| The meta-skill | `skills/meta-skills-govern/` | Creates, changes, reviews and retires skills, and finds which one fits a task. Holds the validator |
| Task worktrees | `scripts/task_worktree.py` | Every change happens in its own folder and branch under `.worktrees/`, so two agents never edit the same checkout. `finish` cleans up only after GitHub confirms the merge |
| Deploy step | `scripts/deploy_skills.py` | Copies `skills/` to the folders tools scan (`.claude/skills`, `.agents/skills`); the copies are generated and never committed |
| Checks | `scripts/verify.py` locally; `.github/workflows/checks.yml` on every pull request | Validator, tests, trigger cases, layout, line endings, personal-data and secret scans, workflow lint. Branch protection makes them required |
| Registry | `registry/` | Project-specific settings (owner, branch, tool folders), so skills stay generic |
| Decisions | `decisions/` | Why the repository works the way it does; binding until replaced |

## Checks you can trust, and what they cannot prove

The server check is required: GitHub refuses to merge a pull request until every job passes, and nobody pushes straight to `main` (`scripts/github_protect.py`, [code-host setup](docs/code-host-setup.md)). Checks prove that files have the right shape and that known behaviour still works. They do not prove an agent's answer is right; the person merging decides that.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: start a task worktree, change only `skills/` (never a generated copy), bump the skill's version and changelog, run `python scripts/verify.py`, and open a pull request.

## License

MIT, see [LICENSE](LICENSE).
