# Changelog

Notable changes to this skill, newest first. Versions follow [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-11-23

### Changed
- Skills live in `.agents/skills/` (the tracked source); paths in this skill and its tests follow. The mirrors are kept current by `scripts/skill_guard.py`.

## [0.2.0] - 2026-11-22

### Changed
- The keyword search also scores words of each skill's own name, so a request such as "detect every shot" finds `media-shot-detect` even before its keywords are written. A naming review found the search ignored names entirely.

## [0.1.0] - 2026-11-22

### Added
- Routing for create, update, review and retire; the conventions page; the validator (rules R1 to R16) and the keyword search.
