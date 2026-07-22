---
name: hello1
description: Session orientation, trial A (evidence only). Git activity is the source of truth; status docs are never summarised, only mined for a pick-up line. Invoke via /hello1 only, never automatically.
allowed-tools: Read, Grep, Glob, Bash
---

Orient me fast from what actually changed, not from what status docs claim.
Works in any repo. Whole output 15 lines or fewer. Launchpad, not a report.

## Principle

Recent churn IS the state. A status doc only earns trust if it changed as
recently as the work it describes, and this skill does not even check that:
it goes straight to the evidence. Docs are read for one thing only, a
pick-up line.

## Gather (run directly, no subagent)

1. `git status --short` -- uncommitted work is the most alive thing here.
2. `git log --oneline -10` and
   `git log --since="14 days ago" --name-only --pretty=format:` --
   cluster touched files into zones (a zone = a tasks/{x} folder, or a
   top-level folder otherwise). Rank zones: uncommitted beats committed,
   newer beats older.
3. Read the actual work in the hottest zone. `git diff` for uncommitted
   files, or `git show` on the newest commit touching the zone if clean.
   Read enough of the changed hunks and surrounding file to say in plain
   words what was mid-flight. Judgement over ceremony: you are working out
   "what was this person doing", not filling a template.
4. Pick-up line: grep the hot zone's task.md and readme.md for a line
   starting `PICKUP:` or `NEXT:` (case-insensitive). If found, quote it
   verbatim with file and date. This is the only doc content allowed into
   the output.

Do NOT open focus.md, status reports, or summarise task.md checklists.

## Hub extras (claude-assistant repo only)

- `tail -2 state/bookend/runlog.jsonl` -- if no "ev":"start" stamp from
  today, warn loudly as the first line of output.
- `.venv/Scripts/python.exe scripts/routines-due.py --check --today <TODAY>`
  -- print its output verbatim if it printed anything.
- Read `tasks/relationship/context.md` plus the first unchecked item in its
  tasks.md (OneDrive symlink, invisible to git, so the scan misses it).
  Surface as the first status line, one line, no incident detail. Never
  write it into any committed file.

## Output

```
## Working on
{zone + one plain sentence of what the diff and commits show was
mid-flight, with dates}

## Pick-up line
{verbatim quote (file, date). Omit section if none found.}

## Git
{branch, last commit hash and date, N uncommitted files}

## Your move
{ONE action, verb-first, ending with "done when ...". Derived from the
evidence, not from a checklist.}
```

Rules: every claim carries a date. No bare -ing status words ("in
progress", "rebuilding") without an actor and a date. If the evidence is
ambiguous, say so in one line and make Your move the check that resolves it.
