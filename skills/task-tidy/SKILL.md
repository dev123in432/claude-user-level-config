---
name: task-tidy
description: Deep cleanup of a bloated task.md (and its readme.md) back to the canonical shape - runs the deterministic linter for the mechanical fixes, then does the semantic pass (distill inbox dumps into actions, lift prose to readme/design docs, regroup by phase). Invoke via /task-tidy, or when quick-goodbye escalates a file needing more than a light touch. Portable across repos.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

Restore a bloated `task.md` to the canonical shape in `task-docs.md` (sibling file). This is the "real
cleanup" that `quick-goodbye` hands off when a file needs more than ~15 edits. The rules are in
`task-docs.md`; ready-to-copy skeletons are in `templates/`.

Two halves: the **linter** does the safe mechanical fixes deterministically; **you** do the semantic
judgment the linter deliberately will not.

## Step 1 - pick the target

- If the user named a file/folder, use it.
- Else the dominant `tasks/<folder>/` of this session (most file ops).
- `--all` only if the user asks to sweep the whole repo.

## Step 2 - mechanical pass (deterministic, first)

Run the bundled linter with `--fix` on the target task.md, from the repo root. The linter is stdlib-only,
so a plain `python` works in any repo:

```
python "$HOME/.claude/skills/task-tidy/task_md_lint.py" --file "tasks/<folder>/task.md" --fix
```

(PowerShell: use `"$env:USERPROFILE\.claude\skills\task-tidy\task_md_lint.py"`.) This collapses stacked
PICKUP blocks to the newest, stamps undated `[x]` with `(done <today>)`, sweeps `[x]` older than 5 days,
and strips `Done`/`Completed Steps`/`Resolved out of scope` archive blocks. It is idempotent.

## Step 3 - semantic pass (judgment; the linter will not do this)

Read the now-smaller file and fix what needs judgment, against `task-docs.md`:

- **PICKUP**: ensure the single surviving PICKUP block reflects current truth (rewrite if it still calls
  something "next" that is already done). Two lines: `PICKUP YYYY-MM-DD:` + `NEXT: ... Done when ...`.
- **Inbox dumps**: for each `## Inbox from ...` section, distill each live item into a `- [ ]` action in
  the right group, drop what is done/superseded, then delete the section (a one-line pointer to the source
  file in `Processed/` is fine). Preserve any item flagged IMPORTANT / "awaiting reply".
- **Lift prose out**: move durable rationale, gotchas, and decisions to `readme.md` (gotchas/config) or a
  design doc (decisions). task.md keeps only actions.
- **Drop transcript noise**: pasted command output, SQL/PowerShell blocks, wide mapping tables, `>> Error:`
  logs, `>>`/`>>>` author notes. If a number in a dump is load-bearing, move it to a readme gotcha; else drop.
- **Regroup by phase/priority**, not by status: `## Now`, `## Next / Backlog`, `## Awaiting external`,
  `## Recently done` (last ~5 days, dated), `## Open bugs` (one-line pointer to BUGS.md).
- **readme.md**: if it carries `- [ ]`/`- [x]` items or `## Status`/`## Now`/`## Next`/`## Pickup`
  headings or a live PICKUP block, move that state into task.md and leave readme with durable facts + a
  pointer to task.md.

Bias to remove. A misleading line is worse than a missing one; git holds the history.

## Step 4 - verify

Run `--check` on the target and confirm it is CLEAN (or explain any residual WARNING, e.g. a legitimately
long backlog):

```
python "$HOME/.claude/skills/task-tidy/task_md_lint.py" --file "tasks/<folder>/task.md" --check
```

## Step 5 - report

Short summary: what the mechanical pass changed, what you distilled/lifted/dropped in the semantic pass,
and anything you deliberately kept (open bugs, awaiting-reply items). End with: "Done. `git diff` to verify."

Never commit - the user handles commits.
