# Task-folder documentation structure (canonical)

Single source of truth for what `task.md` and `readme.md` should contain in every `tasks/<stream>/`
folder, across all repos. The sibling `task_md_lint.py` is the executable form of these rules; the
`task-tidy`, `quick-goodbye`, `task-hygiene` and `hello` skills all defer to it. When this doc and the
script disagree, fix both.

## The three-way split

- `task.md` - the live surface. Current state only. Read at `/hello`, updated as work progresses.
- `readme.md` - stable orientation. Durable why / design / config / gotchas. Rarely changes. No live state.
- Design docs (`design/NN-*.md`) - durable decisions and the reasoning behind them.

Git log is the history record. If a line is only interesting as "what happened when", it belongs in git,
not in either file.

## task.md

Shape:

1. One `PICKUP` block at the very top, dated, two logical lines:
   - `PICKUP YYYY-MM-DD: <what is true now / what landed>`
   - `NEXT: <the single next move>. Done when <concrete check>.`
   Rewrite it each session. Never stack a second PICKUP block; older pickups live in git.
2. A short set of live actions as `- [ ]` / `- [x]` items, grouped by phase or priority (e.g. `## Now`,
   `## Next / Backlog`, `## Awaiting external`), never grouped by status. The bracket is the status.
3. `## Recently done` (optional) - `[x]` items from the last ~5 days, each stamped `(done YYYY-MM-DD)`.
4. `## Open bugs` (optional) - a one-line pointer to `BUGS.md`. Never restate bug detail.

Retention: every `[x]` gets a trailing `(done YYYY-MM-DD)`. Sweep items whose stamp is more than 5 days
old (git holds them). Lift any durable insight to readme.md or a design doc before deleting.

Do NOT put in task.md:

- More than one PICKUP block.
- `### Done <date>` / `## Completed Steps` / `### Resolved or out of scope` archive blocks, or
  `~~...~~ **DONE**` strikethrough churn.
- Un-triaged `## Inbox from ...` dumps. Distill each into `[ ]` actions, then tombstone the section.
- Pasted command output, SQL / PowerShell run blocks, wide result or mapping tables, `>> Error:` logs.
- Author self-notes (`>>` / `>>>`). Decide the point, edit the item, delete the note.
- Explanatory prose, setup walkthroughs, or per-step rationale. Those go to readme.md or a design doc.

Length is not itself a fault. A large but disciplined backlog (one PICKUP, dated ticks, bugs delegated)
is fine; the smells above are the fault.

## readme.md

Carries durable facts only:

- One-line task summary + a pointer to task.md for live state.
- Overview / what this delivers.
- Architecture pointers (links to design docs).
- Environment / config notes (key vault names, env vars, lakehouse IDs).
- Gotchas that bit us once and would bite again.
- "How to resume" as a brief pointer to task.md, not a state dump.

Do NOT put in readme.md:

- Any `- [ ]` / `- [x]` checkbox items (those live in task.md).
- `## Status (YYYY-MM-DD)` / `## Now` / `## Next` / `## Pickup` / `## Recently done` headings.
- A live PICKUP block (a one-line pointer to task.md's PICKUP is fine).
- Session-by-session updates or decision logs that change often.

## Skeletons

Ready-to-copy skeletons live alongside this file in `templates/task.md` and `templates/readme.md`.
Good real examples (ESG repo): task.md - `tasks/meters-7544/`, `tasks/facility-usage/`,
`tasks/api-nucleus-fund-ownership/`; readme.md - `tasks/meters-7544/`, `tasks/contracts-4085/`.
