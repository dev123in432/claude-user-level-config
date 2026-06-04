---
name: sleep-dream
description: Periodic memory maintenance for the auto-memory system. Prunes stale memories to an archive, consolidates duplicates and broken links, and "dreams" - picks the highest-friction session since the last run (max 7 days back) and proposes a memory that would have eased it, then simulates the session to confirm. Modelled on sleep-stage consolidation (NREM replay, SHY pruning, REM counterfactual simulation, overfitted-brain regularisation, threat-simulation gating). Use when memory feels cluttered or weekly as routine hygiene.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
---

## When to invoke

User-invoked via `/sleep-dream`. Not automatic. Args:

- no args - run all phases
- `--phase prune` / `consolidate` / `dream` - single phase
- `--dry-run` - show all candidates, take no actions
- `--window 14d` - override the 7-day dream look-back cap

## Phase 0: Wake up (no changes)

Find the active memory directory. It lives under `~/.claude/projects/{project-hash}/memory/` where `{project-hash}` is the current working directory with `:`, `\`, and space all replaced by `-` (e.g. `C:\Users\dinne\repos\foo bar` becomes `C--Users-dinne-repos-foo-bar`).

If uncertain, Glob `~/.claude/projects/*/memory/MEMORY.md` and pick the hash matching cwd. Bail with a friendly message if no memory dir exists for the current project.

Read `{memory_dir}/.sleep-log.md` to find the last run timestamp. Create the file with an empty header if missing. This anchors the dream window.

State out loud: "Memory dir: {path}. Last sleep: {date or 'never'}."

## Phase 1: Drowsy - inventory + mechanical scan (no changes)

> **Caveat:** the Grep (ripgrep) tool returns NO matches inside `~/.claude/projects/.../memory/` because of an ignore rule in that tree. Don't trust an empty Grep result there - use the Read tool or Bash `grep`/`findstr` instead. This bit a previous run.

Inline (no subagent):

- Glob `{memory_dir}/*.md` - total count
- Type counts via Bash: `grep -h "^type:" {memory_dir}/*.md | sort | uniq -c` (frontmatter is top-level `type:`, NOT nested under `metadata:`)
- Read `MEMORY.md` - line count
- Glob `{memory_dir}/archive/**/*.md` - archive size
- List files added since last run (mtime > last-run timestamp)

Then run the mechanical-health helper - it computes ground truth that subagents must NOT guess at (real on-disk file existence, the real `[[link]]` graph, real MEMORY.md index membership, age, near-duplicate descriptions):

```
python {skill_dir}/analyze_memory.py {memory_dir} --repo {cwd} --today {today} > %TEMP%\mem-report.json
```

Read the JSON. It is the authoritative input for Phase 2 and Phase 3 - prefer its `flags`, `referents_missing`, `inbound_links`, `indexed_in_memory_md`, and `near_duplicate_descriptions` over any subagent's prose claim about the same facts.

Output a 5-line summary. No changes. If `--phase prune` / `consolidate` / `dream` was set, proceed to that phase only. Otherwise continue.

## Phase 2: Light sleep - prune (user-approved)

Feed the Phase 1 `mem-report.json` to the scout - it carries the mechanical ground truth so the scout spends its judgement on interpretation, not on re-deriving (and mis-guessing) facts. Spawn Explore subagent. Brief:

> You are the prune scout for sleep-dream. Read-only. Use Read + Bash `grep`/`findstr` (the Grep/ripgrep tool silently returns nothing in the memory dir - do not rely on it).
>
> Memory dir: `{memory_dir}`. Today: `{today}`. Last sleep: `{last_run}`.
> Mechanical report (authoritative for file-existence, links, index membership, age): `{path_to_mem-report.json}` - Read it first.
>
> Your job is JUDGEMENT on top of the report's facts, not re-deriving them. For each `flags` entry in the report, decide whether it is a real prune candidate. Apply these rules - they encode mistakes a previous run made:
>
> 1. **Resolution markers > 30 days old** (`resolved-marker` flag): genuine archive candidate IF the resolution is durable and the memory no longer guides live work.
> 2. **Expired point-in-time claims** (`expired-point-in-time` flag): if the WHOLE memory is point-in-time, archive. If only one line inside an otherwise-live memory is stale, this is a CONTENT REFRESH (Phase 3), not a prune - say so.
> 3. **Missing referents** (`referents_missing` flag): the report already confirmed these paths are absent on disk. But DECIDE WHY before flagging:
>    - **Path drift** - the file exists at a nearby path (search for the basename). -> content refresh, NOT prune.
>    - **Planned/aspirational** - memory describes a file "to be created" / "planned" / "not started". Correctly missing. -> KEEP, do not flag.
>    - **Placeholder** - the path is a template/example (e.g. `NN-foo.md`, `{name}`). Ignore.
>    - **Genuinely deleted/retired** (e.g. renamed to `zzz*.old`) - the memory's guidance is now dead. -> real prune candidate.
> 4. **Superseded memories**: only flag a memory as superseded if ANOTHER MEMORY FILE explicitly overrides it (look for `**Overrides**`/`supersedes` in other files' bodies). A MEMORY.md index line that merely points at the file is NOT a supersession - flagging that is a circular error. Never flag a memory as "superseded by MEMORY.md line N".
> 5. **Stale `predicts:` claims**: for memories with a `predicts:` field > 30 days old, grep session JSONL under `~/.claude/projects/{project-hash}/*/*.jsonl` for the prediction's keywords. Flag only if never matched.
> 6. **Orphans** (`orphan` flag in report = no inbound links AND not in MEMORY.md): this usually means UNDISCOVERABLE, not stale. Default disposition is "index into MEMORY.md" (Phase 3), NOT archive - unless the content is also independently stale. Ignore the `.sleep-log` orphan flag (it is the log file).
>
> Return a clean markdown table: `filename | report_flag | your_verdict (prune / refresh / index / keep) | one-line reason`. Cap at 15 rows. No prose. Distinguish prune from refresh/index clearly - do not inflate the prune list.

Receive the table. Sanity-check it against `mem-report.json` yourself before showing the user - reject any "superseded by MEMORY.md" verdict and any prune of a planned/aspirational referent. Render the filtered table. AskUserQuestion with options:

- Archive all
- Archive selectively (then iterate per-row)
- Skip prune

For approved files:
- Move to `{memory_dir}/archive/{YYYY-MM}/{filename}` (create dir if missing - use Bash `mkdir`)
- Remove the matching `MEMORY.md` line via Edit
- Record in a transient `pruned_this_run` list for the log

Report what was archived.

## Phase 3: Deep sleep - consolidate (user-approved)

Spawn Explore subagent. Brief:

> You are the consolidation scout for sleep-dream. Read-only. Use Glob/Grep/Read only.
>
> Memory dir: `{memory_dir}`.
>
> Find consolidation opportunities:
>
> 1. **Near-duplicates**: pairs of files whose `description:` lines are >60% lexically similar OR whose bodies cover the same topic (same recurring nouns/slugs). Suggest merge-forward (keep the most-recent or most-linked; fold the other's distinctive content in).
> 2. **Orphan files**: files in `{memory_dir}/` (top level, not archive/) with NO matching entry in `MEMORY.md`. Suggest adding a one-line entry.
> 3. **Dangling MEMORY.md pointers**: lines in `MEMORY.md` that link to a slug whose file doesn't exist in `{memory_dir}/`. Suggest removing the line.
> 4. **Missing inter-memory links**: pairs of memory bodies that mention each other's topic (by name or slug) in prose but lack a `[[other-slug]]` link. Suggest backfill.
>
> For each opportunity, return: `kind | files_involved | proposed_change_one_line | rationale_one_line`. Cap at 12 rows.

Render the table. AskUserQuestion: approve all / selective / skip.

For approved:
- Merge - Edit the kept file to fold in new content; archive the merged-from file (Phase 2 archive path)
- Orphan - Edit `MEMORY.md` to add the line in the appropriate section
- Dangling - Edit `MEMORY.md` to remove the line
- Link backfill - Edit the relevant file to add `[[slug]]` in the right sentence

## Phase 4: REM - dream (the what-if loop, user-approved)

This is the substantive phase. Pattern: friction-gate -> replay -> simulate -> generalise -> integrate -> tag.

### Pre-check: friction trigger

Spawn Explore subagent. Brief:

> You are the friction scout. Read-only. Glob/Grep/Read.
>
> Session transcript root: `~/.claude/projects/{project-hash}/`. Window: sessions modified since `{last_run}` OR within the last 7 days, whichever shorter. (Override: `--window` arg if present.)
>
> Glob `**/*.jsonl` excluding `**/subagents/*`. For each in-window session file, compute a friction score:
>
> - +1 per user correction phrase: `\bno\b`, `\bdon't\b`, `\bstop\b`, `\bactually\b`, `\bno wait\b`, `\bno not\b`, `I said`, `I told you`
> - +1 per user clarification introducing new context: `\bby the way\b`, `\bfor context\b`, `should have mentioned`, `actually it's`, `forgot to say`
> - +1 per Explore subagent dispatch (count `"subagent_type":"Explore"` or similar)
> - +1 if assistant turn count > 30
> - +1 per tool denial (`tool was rejected`) or plan rejection
>
> Return ranked list: `session_id | mtime | score | one_line_topic_inferred_from_first_user_turn`. Cap at 10. Highest score first.

Receive the list. If top score < 3, report "Quiet week. Nothing to dream about." and skip the rest of Phase 4. Else pick the top session.

### 4a: Replay extraction

Spawn Explore subagent. Brief:

> You are the replay scout for sleep-dream. Read-only. Glob/Grep/Read.
>
> Read this session in detail: `{session_path}`. JSONL - one message per line, fields `type`, `message.role`, `message.content`, `timestamp`.
>
> Identify:
>
> 1. **Goal eventually achieved**: in 1-2 sentences, what did the user + assistant collectively figure out by session end? This is the HER hindsight goal.
> 2. **Friction moments**: turns where the assistant lacked context the user later provided, or where the assistant flailed (multiple Explore dispatches, wrong file, asked for clarification that was answerable from memory). For each, quote the relevant 1-2 turns briefly.
> 3. **Candidate memories**: propose 1-3 candidates whose existence at session start would have shortcut the friction. For each: provisional `name`, `description`, `metadata.type`, draft body (with **Why:** / **How to apply:** for feedback/project types), and which transcript moment(s) it addresses.
>
> Format candidates as markdown. Don't write files - propose only.

Receive candidates. Pass to 4b.

### 4b: Counterfactual simulation

For each candidate, spawn an Explore subagent. Brief:

> You are the dream simulator. Read-only.
>
> Original session: `{session_path}`. Read it.
>
> Candidate memory to inject into context at session start:
> ```
> {full candidate frontmatter + body}
> ```
>
> Question: with this memory present in the assistant's MEMORY.md context at session start, how would the assistant's response to the user's FIRST message have differed? Specifically score on these signals (1 point each):
>
> - Skips an Explore subagent dispatch that was previously needed (+1)
> - Answers directly instead of asking a clarifying question (+1)
> - Picks the correct file/path/approach on the first try (rather than after correction) (+1)
> - Avoids a wrong assumption the user later corrected (+1)
>
> Reason out loud about the assistant's likely first response with and without the memory. Then return:
>
> - Score (0-4)
> - One-line specific explanation of the first-response shift (must name the specific tool call or file path that would change - reject vague "would have done better")

Drop any candidate scoring 0. Keep candidates scoring >=1.

### 4c: Generalisation pass

For each surviving candidate, spawn an Explore subagent. Brief:

> You are the dream regulariser. Read-only.
>
> Candidate memory:
> ```
> {candidate}
> ```
>
> Original session: `{session_path}`.
>
> Produce 2-3 variants on a specificity ladder:
> - v1 - specific (exact paths, names, dates - the original)
> - v2 - pattern level (the rule: "when working on X, Y applies")
> - v3 - principle level (most abstract: "always check Y before assuming Z")
>
> For each variant, re-run the 4b simulation (would this variant have helped the original session? score 0-4).
>
> Return all variants with scores. Recommend the MOST GENERAL variant that still scores >=1. Rationale: prefer memories that help neighbouring future situations, not only this one session (overfitted-brain regulariser).
>
> If only v1 scores, return v1 and flag `overfit_risk: true`.

Keep the recommended variant. Discard the others.

### 4d: Schema integration check

Spawn Explore subagent. Brief:

> You are the schema integrator. Read-only.
>
> Candidate memory:
> ```
> {recommended variant}
> ```
>
> Existing memory dir: `{memory_dir}`. Glob the directory and Read any memory whose `description:` or filename suggests topical overlap with this candidate.
>
> For each overlapping memory found, propose either:
> - MERGE-FORWARD - update the existing memory to fold in this candidate's distinctive content (preferred when overlap > 50%)
> - SIDE-BY-SIDE - keep separate, add `[[link]]` between them
>
> Return: recommendation (`new` / `merge-into:{slug}` / `side-by-side-with:{slug}`), one-line rationale, and if merge: the proposed Edit (old_string / new_string for the existing memory).

### 4e: Predictive tagging

For the final candidate (or the merge-forward target), draft a `predicts:` frontmatter line. One sentence describing the future situation this memory should help with. Inline reasoning, no subagent needed.

Example: `predicts: "Next time the user starts an EN-pattern Bronze load, recall the Scope 2 carve-out twin convention before asking which view to use."`

Also add `dreamt_from: "{session_id} / {session_date}"` for provenance.

### 4f: Present to user

For each final candidate:

```
## Dream candidate: {slug}

Source session: {session_id} ({date}) - friction score {n}
Specificity: v2 (pattern level) - "{one-line of body}"
Predicts: {predicts text}

### Counterfactual
Without this memory, the assistant {what it did}.
With this memory, the assistant would {specific tool/file change}.

### Schema integration
{new / merge-into / side-by-side}

### Proposed memory (frontmatter + body)
{full file content}
```

AskUserQuestion per candidate: Save / Skip / Edit-then-save.

For Save: Write the file, add MEMORY.md line in the right section (Feedback / Active Work / References / Pending Decisions depending on type).
For Edit: take the user's revision verbatim, save that.
For Skip: discard.

## Phase 5: Wake up - log

Append to `{memory_dir}/.sleep-log.md`:

```markdown
## {YYYY-MM-DD HH:MM}

- Pruned: {n} -> archive/{YYYY-MM}/ ({comma-list of slugs})
- Consolidated: {summary - "2 link backfills, 1 orphan registered, 1 merge"}
- Dream: session {session_id} (friction {score}) -> {n} candidates -> {n_kept} kept ({slugs})
  - Kept variant level: {v1/v2/v3}
  - Predicts: {predicts line}
- Duration: {wall_time}
```

## End-of-run output

Render to user:

```
Slept.
Memory: {N_before} -> {N_after} files ({n_archived} archived to archive/{YYYY-MM}/).
Consolidated: {summary}.
Dream: session {id} (friction {n}) -> {n_kept} new memory ({slug}.md, {variant_level}).
  Counterfactual: {one-line specific shift}.
  Predicts: {predicts text}
Next sleep: ~7 days.
```

If a phase was skipped (e.g. quiet-week dream), say so explicitly: `Dream: skipped - quiet week (max friction {n}).`

## New memory frontmatter fields (dream-phase only)

Memories created by Phase 4 get two optional fields beyond the standard schema:

```yaml
predicts: "Next time {situation}, recall {memory content} before {default action}"
dreamt_from: "{session_id} / {YYYY-MM-DD}"
```

`predicts:` becomes a stale-signal for future Phase 2 runs (see Phase 2 step 5).
`dreamt_from:` is provenance only - never a prune signal on its own.

## Cautions

- **Never delete a memory file.** Phase 2 archives, never `rm`. Recoverable from `archive/{YYYY-MM}/`.
- **Never write a dream memory without 4b passing.** If simulation scores 0, the candidate is noise.
- **Respect user edits.** If the user picks "Edit-then-save", their text wins verbatim - don't re-prettify.
- **Don't run Phase 4 if `--phase prune` or `--phase consolidate` was specified.** Single-phase mode is single-phase.
- **Don't multi-dream in one run.** Pick the top session only. If the week was unusually busy, the user can re-run after reviewing.
