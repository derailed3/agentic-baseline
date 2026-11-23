# 0005: secrets and personal data are scanned on the server

- Status: Accepted (2026-11-22)
- Affects: `.github/workflows/checks.yml` (job `scan`), `scripts/scan_personal_data.py`, `.gitleaks.toml`

## Context

"Never commit secrets or personal data" written in the instruction file is a request, not a control: anything that must never reach the shared branch needs a server check. The repository is public, so a leak is published the moment it is pushed.

## Decision

The required `scan` job runs gitleaks over the whole history and `scripts/scan_personal_data.py` (Social Security numbers, payment card numbers, phone numbers, email addresses outside example domains) on every pull request. `scripts/verify.py` runs both locally when the tools are installed. A deliberate, harmless example line carries `pii-allow`.

## Consequences

A secret found after a push is already public: rotate it, then remove it. Scans find patterns, not intent; the person merging still reads the change.
