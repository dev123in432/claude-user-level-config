# sleep-dream - improvement backlog

Observations from the first real run (2026-05-27, ESG project memory, 56 files).
Ordered by value-per-effort.

## High value

1. **Make consolidate a cheap deterministic pass; demote the prune scout to judgement-only.**
   Path-drift, orphans, dangling MEMORY.md pointers, and near-dupes are all computed
   deterministically by `analyze_memory.py`. The first prune scout over-flagged with bad
   heuristics (circular "superseded by MEMORY.md line N", claimed a folder was missing
   without checking disk). Root fix applied this run: helper added + briefs hardened. Next
   step: a `--phase health` that runs the helper and proposes fixes with NO subagent at all.
   This is the part most worth running often.

2. **Strip skill-invocation preamble before friction topic-inference.**
   The friction scout labelled 6+ sessions "skills directory configuration friction" - an
   artefact of the `Base directory for this skill: ...` / `<command-name>` / `<system-reminder>`
   boilerplate bleeding into transcripts. Topic inference must skip these before reading the
   first "real" user message. Briefed verbally this run; codify it in the friction-scout brief.

## Medium value

3. **Gate the dream phase higher, or make it opt-in.**
   Dream is the costliest phase (3 subagent dispatches) and its payoff is unproven. Options:
   raise the friction threshold (currently >=3; first run's top was 31, so the floor is far too
   low to be selective), or make full-dream `--phase dream` / monthly rather than part of the
   default weekly run.

4. **Close the loop: measure whether dreamt memories ever fire.**
   Phase 2 step 5 checks stale `predicts:` claims, but there's no signal for the positive case -
   did a dreamt memory actually get recalled/used in a later session? Without that, we can't tell
   if dream earns its cost. Suggestion: on each run, grep sessions since the memory's
   `dreamt_from` date for the memory's distinctive terms; log hits in `.sleep-log.md`. After a
   few runs we'll know if dream is worth keeping.

5. **Beware borderline-generic dream candidates.**
   Candidate 2 this run ("read-once, show a table, batch-edit") is half project-specific
   (`>>>`/fenced-comments marker convention) and half generic working advice. The 4c generaliser
   should bias toward the project-specific kernel and reject candidates whose only durable content
   is generic process advice.

## Cadence recommendation

Don't run the whole skill weekly. Split:
- **health-check (helper + fixes, no subagents):** cheap, run weekly or at session start.
- **prune + dream:** monthly or on-demand; low churn makes weekly wasteful.

## Notes

- `analyze_memory.py` is now a first-class skill asset. Keep it in sync if frontmatter schema
  changes (it expects top-level `type:`, not nested `metadata.type:`).
- ripgrep (the Grep tool) silently returns zero matches inside `~/.claude/projects/.../memory/`
  due to an ignore rule in that tree. Every phase must use Bash grep / Read instead. This bit the
  first run before it was noticed.
