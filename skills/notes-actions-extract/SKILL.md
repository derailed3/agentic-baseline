---
name: notes-actions-extract
description: >-
  Pull the action items out of a meeting notes file and list them as a
  checklist. Use for "what are the action items", "list the TODOs from
  these notes", or "turn my notes into a checklist".
version: x
distribution: portable
generality: general
tags:
  - domain:notes
  - pattern:standalone
keywords:
  - action items
  - meeting notes
  - checklist
  - todos
---

# Notes Actions Extract

Turn a notes file into a checklist of its action items.

## When to Use

- Someone has meeting notes and wants the action items listed.
- Not for writing or summarizing the notes themselves.

## Routing

| Request | Read |
|---|---|
| List the action items in a notes file | workflows/extract.md |

## Parameters

| Input | Required | Default |
|---|---|---|
| Path of the notes file | Yes | None; ask the person |

## Output Format

A Markdown checklist, one `- [ ]` line per action item, in the order they appear in the notes.

## Error Handling

| Symptom | Cause | Fix |
|---|---|---|
| "No action items found." | Items are not marked "Action:" or "TODO:" | Ask the person how items are marked; do not guess |
| "not a file" | Wrong path | Confirm the path with the person |
