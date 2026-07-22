---
name: hello2
description: Session orientation, trial B (cross-examination). Compares what the docs claim against what the files and git actually show, and issues a freshness verdict per task. Invoke via /hello2 only, never automatically.
allowed-tools: Read, Grep, Glob, Bash
---

Orient me by cross-examining the docs against the evidence. Git is
forensics, docs are witnesses, and a witness is only credible if their
story is as fresh as the crime scene. Works in any repo. Output 20 lines
or fewer.

## The heuristic (this is the whole idea)

For each active task folder: when did task.md last change, and when did
the WORK in that folder last change? If the work is newer than the doc by
more than ~2 days, the doc is behind reality and its claims are demoted.

## Gather (run directly, no subagent)

1. `git status --short` and `git log --oneline -10`.
2. `git log --since="14 days ago" --name-only --pretty=format:` --
   cluster into zones (tasks/{x} folders). Top 2 zones by recency,
   uncommitted first.
3. For each of the top zones, establish two dates:
   - doc date: `git log -1 --format=%ci -- <zone>/task.md` (use fs mtime
     via `ls -l` instead if task.md shows in git status as modified)
   - work date: newest change to any OTHER file in the zone (from the
     step 2 log, or fs mtime for uncommitted files)
   Verdict per zone:
   - FRESH: doc date >= work date minus 2 days
   - DRIFTED (N days): work is N days newer than the doc
   - SILENT: no task.md exists
4. Read each zone's task.md top status line and first unchecked item,
   but treat them per the verdict: FRESH claims can be reported as
   claims; DRIFTED claims must be paired with what the evidence shows
   (skim the diff or newest commits and say what actually changed).
5. Contradiction rule: if task.md disagrees with itself (top line vs a
   dated done-annotation deeper in), do not resolve it. Report it as one
   line: "CONTRADICTION in task.md: top says X; step N marked done
   YYYY-MM-DD." Resolving it becomes Your move.
6. Pick-up line: grep the hot zones' task.md / readme.md for `PICKUP:`
   or `NEXT:` lines; quote verbatim with date if found.

Do not open focus.md unless it changed within 14 days (check with
`git log -1 --format=%ci -- docs/status/focus.md`). If it is older,
one line at most: "focus.md stale since YYYY-MM-DD, ignored."

## Hub extras (claude-assistant repo only)

- `tail -2 state/bookend/runlog.jsonl` -- no "ev":"start" stamp today
  means warn loudly, first line.
- `.venv/Scripts/python.exe scripts/routines-due.py --check --today <TODAY>`
  -- print verbatim if non-empty.
- Read `tasks/relationship/context.md` + first unchecked task (symlink,
  invisible to git). First status line, one line, no detail, never into
  committed files.

## Output

```
## State (per docs and git -- nothing verified against live systems)
{one line per hot zone:
 {zone} [FRESH|DRIFTED Nd|SILENT]: {doc claim if FRESH; if DRIFTED, what
 the evidence shows the work actually was, with dates}}
{CONTRADICTION lines, if any}

## Pick-up line
{verbatim (file, date). Omit if none.}

## Git
{branch, last commit hash and date, N uncommitted}

## Your move
{ONE action, verb-first, "done when ...". If anything is DRIFTED or
CONTRADICTED, Your move is to reconcile or verify it, and say against
what (live system, a re-read, a query).}
```

Rules: every claim gets a source and date. No bare -ing status words.
Never present a doc claim as system state; the header caveat is
permanent.
