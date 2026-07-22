---
name: hello3
description: Session orientation, trial C (breadcrumb protocol). A dated PICKUP line written at session close is the primary orientation source; falls back to a git evidence scan when the breadcrumb is missing or stale. Invoke via /hello3 only, never automatically.
allowed-tools: Read, Grep, Glob, Bash
---

The cheapest reliable orientation is a note from past-you. This skill
makes the pick-up line a first-class protocol instead of an occasional
habit, and uses evidence scanning only as the fallback. Works in any
repo. Output 12 lines or fewer when the breadcrumb is fresh.

## The convention

The active task.md carries a PICKUP block at the very top:

```
PICKUP 2026-07-21: loaded 486 elec + 43 gas to DEV via anti-join views.
NEXT: run ERM_30 gate in per_row mode. Done when TEST section 10 shows
529 loaded, 0 leaked_held.
```

One or two lines. What landed (with date), the next move, its done-check.
Written at session close by /goodbye or by hand. This skill reads it; it
never writes it.

(One-line addition for the /goodbye skill to make this stick: "Before
wrapping up, write or refresh the PICKUP block at the top of the active
task.md: what landed with dates, the next move, its done-when.")

## Steps (run directly, no subagent)

1. Find the hot zone fast: `git status --short` plus
   `git log --oneline -5 --name-only`. The zone with uncommitted or most
   recent changes is the active task.
2. Read the top of that zone's task.md looking for a `PICKUP` block.
3. Freshness test: PICKUP date vs the newest change in the zone
   (git log dates, fs mtime for uncommitted).
   - FRESH (no work newer than the breadcrumb): trust it. Lead with it.
   - STALE (work happened after it was written): say so in one line
     ("PICKUP dated 07-18 but work continued to 07-21, treating as
     unreliable") and fall back to the evidence scan below.
   - MISSING: one line ("no PICKUP block in {zone}/task.md") and fall
     back.
4. Fallback evidence scan (only when stale or missing): read the actual
   uncommitted diff or the newest commits in the zone, enough to say in
   plain words what was mid-flight, with dates. Do not summarise the
   task.md checklist; do not open focus.md.

## Hub extras (claude-assistant repo only)

- `tail -2 state/bookend/runlog.jsonl` -- warn loudly first line if no
  "ev":"start" stamp from today.
- `.venv/Scripts/python.exe scripts/routines-due.py --check --today <TODAY>`
  -- print verbatim if non-empty.
- Read `tasks/relationship/context.md` + first unchecked task (symlink,
  invisible to git). First status line, one line, no detail, never into
  committed files.

## Output (breadcrumb fresh)

```
## Pick-up
{the PICKUP block verbatim (task.md, date)}

## Git sanity
{branch, last commit hash and date, N uncommitted -- one line. Flag in
one more line only if git looks inconsistent with the breadcrumb, e.g.
uncommitted files the breadcrumb does not mention.}

## Your move
{the NEXT line from the breadcrumb, restated verb-first with its
done-check}
```

## Output (fallback)

```
## No usable breadcrumb
{one line: missing, or stale since when}

## Working on (per evidence)
{one plain sentence of what the diff and commits show, with dates}

## Git
{branch, last commit, N uncommitted}

## Your move
{ONE action, verb-first, "done when ...". End by offering to write a
fresh PICKUP block once the state is confirmed.}
```

Rules: every claim carries a date. No bare -ing status words without an
actor and a date. Doc claims outside the PICKUP block are not status.
