---
name: productivity-sprint
description: ADHD-friendly time-boxed work sprint with mid-point check-in and post-sprint retro. Captures planned vs actual time, scope creep, and qualitative signals into per-session files in OneDrive so estimation gets better over time.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, ScheduleWakeup
---

# productivity-sprint - ADHD-friendly coached work sprints

## What this skill does

David has ADHD. He gets context-switching cost, time blindness, indecision paralysis on starts, and scope drift mid-task. Manual sprint coaching (start time, mid-point check-in, post-sprint retro) helped him land a 30-min sprint of variation feedback authoring on 2026-05-06 in 54 minutes (1.8x estimate, but **sent**).

This skill formalises that pattern. It does five things:

1. **Start a sprint** with goal, "what does done look like", time-box, and task-type tag. Snapshots scope at start so creep is detectable.
2. **Schedule a mid-point check-in** via `ScheduleWakeup`. At the check, asks 3 tight questions: where are you, blocked, scope-creep happened?
3. **Run a finish retro** when the time-box ends (or user invokes). Captures 4 questions: what got done, what threw you off, tag confirm, how do you feel.
4. **Write a session file** to OneDrive (one file per sprint). Frontmatter for status, started, finished, time_box_min, task_type. Body holds the conversation data.
5. **Show rollups**: `today` shows today's sessions; `week` shows this ISO week. Rollups generated on demand by reading the session files (no separate rollup files).

## Where data lives

- **OneDrive root**: `C:\Users\dinne\OneDrive - Accelerate\productivity-coach\`
- **Session files**: `{root}\sessions\YYYY-MM-DD-HHMM-{task-type}-{slug}.md`
- **NEVER** write productivity data into a client repo - the Charter Hall ESG repo and similar are client-facing.

## How to invoke

User types `/productivity-sprint` optionally with an arg:

| Args | Intent |
|---|---|
| (none) | **Auto-detect**. If an active session exists (status `active` in any session file), prompt to mid-check or finish. Otherwise prompt to start. |
| `start` | Force-start a new sprint (warn + confirm if an active one exists). |
| `end` / `finish` / `done` | Run the finish retro on the active session. |
| `mid` / `check` | Run the mid-point check-in. |
| `today` | List today's sessions with their stats. |
| `week` | List this ISO-week's sessions with rollup stats. |
| `abort` | Mark active session `status: aborted`, append a one-line "why aborted" capture, no retro. ADHD users who bail mid-sprint should not leave zombie active sessions. |
| `migrate-from-repo` | One-time: move productivity data out of the Charter Hall ESG repo into OneDrive. (Initial migration helper.) |

## Step 1 - detect state

Always start by determining what's already going on:

```bash
ls "C:/Users/dinne/OneDrive - Accelerate/productivity-coach/sessions/" 2>/dev/null
```

If the folder doesn't exist, create it (`mkdir -p`). If it exists, look for any file whose frontmatter contains `status: active` - use Grep over the sessions folder.

**Stale-active check**: if an active session's `started` is more than 24 hours ago, it's stale. Do not silently treat it as the active sprint. Prompt the user:

> "Found a sprint started YYYY-MM-DD HH:MM still marked active. (a) close it as completed now (with retro), (b) close as aborted (no retro), (c) keep it open and use it as the active sprint."

Take the user's answer and proceed accordingly before doing anything else.

**Multiple-active check**: if more than one file has `status: active`, list them and ask which is the real one; mark the others `status: aborted` with reason `"orphaned - multiple-active resolution"`.

## Step 2 - start a sprint

Triggered when args are `start` (or empty + no active session).

Ask the user **all four questions in one message** (don't drip them - ADHD-friendly batching):

1. **Goal** - one line. What are you aiming to achieve this sprint?
2. **Done definition** - one line. What does "done" look like? (Be concrete - "feedback sent to James via Teams" not "feedback finished".)
3. **Time-box** - how many minutes? Recommend 25-45 for focused work; 60+ usually means the goal is too big and should be split.
4. **Task type tag** - short slug that groups similar work for estimation history. Examples: `feedback-doc-authoring`, `api-integration-build`, `sql-view-authoring`, `power-bi-redesign`, `inbox-triage`.

**Show recent estimation history for the tag** (if any exists). Glob the sessions folder for files matching `*-{task_type}-*.md` (the leading hyphen anchors so the tag must be a full filename component, not a substring of a slug). Read frontmatter for `time_box_min` vs `actual_min`; show last 3-5 as a table. This primes a realistic time-box. If no history, say so in one line ("No prior `{task_type}` sprints logged - estimate is a guess; we'll improve it as data accumulates.") - don't belabour it.

**Partial answers OK**: if the user answers only 1-2 of the 4 start questions, do NOT re-prompt. Fill missing fields with `(not specified)` and proceed. The point is to start, not to interrogate. Capture in frontmatter as-is. Estimation history queries still work as long as `task_type` is present, so if everything else is missing but the tag landed, that's enough. If `task_type` is missing, infer one from the goal text and confirm in a single line ("tagging this as `{inferred}` - shout if wrong"); do not block on it.

After the user answers, write the session file. Filename: `YYYY-MM-DD-HHMM-{task-type}-{slug}.md` where `{slug}` is 3-5 words from the goal, lowercase, hyphenated.

Frontmatter:

```yaml
---
status: active
started: YYYY-MM-DDTHH:MM:SS+10:00  # local time, Sydney/Melbourne; never mix with UTC
time_box_min: N
task_type: {tag}
goal: {one-line goal}
done_definition: {one-line done}
---
```

(Earlier drafts carried a `mid_check_at` field. Dropped - the wakeup is the source of truth, the field was unused after start.)

Body starts with:

```markdown
# Sprint {YYYY-MM-DD HH:MM} - {task_type}

## Goal
{goal}

## Done definition
{done_definition}

## Plan / scope at start
_(snapshot what user knows now - any todos, sub-tasks, files involved. Capture in user's own words. This is the baseline for scope-creep detection at mid-check.)_

## Mid-point check-in
_(written when mid-check fires)_

## Retro
_(written when finish fires)_

## Follow-ups / deferred
_(captured here when mid-check or retro surfaces deferred scope, parked decisions, "ask Marcus" items, etc - so they survive the sprint instead of getting prose-buried in the check-in narrative)_
```

**Warm-up budget** - explicitly tell the user: "the first ~5-10 min is warm-up to rebuild the mental model. Don't fight it. The time-box accounts for it." Cold-start cost is real; pretending it's free is a false start.

**Kill distractions before the go** - remind the user, in a single two-line nudge (not a checklist to tick off), to:
- a) Set a time-based Do Not Disturb status in MS Teams for the time-box duration (profile > status > duration).
- b) Turn on Windows Focus for the time-box length (Win+N > Focus, or Settings > System > Focus > Start focus session).

Match both durations to the time-box so they auto-clear when the sprint ends - otherwise they stay on past the box.

_(Reminder only for now. Could be automated later - Windows Focus and Teams DND can both be triggered from the command line, so the start step could fire them via Bash. Deferred because Teams presence needs Graph API auth and Windows Focus has no clean official CLI.)_

**Schedule the mid-check** via `ScheduleWakeup` with `delaySeconds = round(time_box_min * 60 * 0.5)` and a reason like `"Mid-point check-in for {task_type} sprint"` and prompt that re-invokes this skill in `mid` mode (literal: `/productivity-sprint mid`).

End the start step with a single-line "go" and stop. Do not keep talking.

## Step 3 - mid-point check-in

Triggered by ScheduleWakeup wakeup OR `/productivity-sprint mid`.

Find the active session file. Ask **three** tight questions:

1. **Where are you?** Which step, what's done so far?
2. **Anything blocking** - tooling, ambiguity, indecision?
3. **Scope-creep** - is the work bigger now than the start snapshot? If yes, is it (a) extend time-box, (b) defer the new bit, or (c) accept the overrun?

After user answers, append to the session file under "## Mid-point check-in":

```markdown
## Mid-point check-in (HH:MM, {N} min in)

**Where:** {answer}
**Blockers:** {answer}
**Scope creep:** {answer + decision if applicable}

**Recommendation:** {one line - encourage / cut scope / extend / push to follow-up}
```

If the user reports scope creep AND chose "extend", update the frontmatter `time_box_min` and reschedule the finish wakeup. If they chose "defer", **append the deferred items to the "Follow-ups / deferred" section of the session file** (one bullet per item, with one-line context so future-David knows what it meant). Do not just leave them in the check-in prose. If they chose "accept overrun", just note it.

Also push any "ask {person}" or "open question" items raised in the blockers answer into the same Follow-ups / deferred section.

**Schedule the finish wakeup** via `ScheduleWakeup` with `delaySeconds` set to the remaining time (`time_box_min * 60 - elapsed_seconds`). Reason: `"Finish-ping for {task_type} sprint"`. Prompt: `/productivity-sprint end`.

End with a one-liner: "Keep going - {N} min remaining" and stop.

## Step 4 - finish retro

Triggered by ScheduleWakeup wakeup OR `/productivity-sprint end`.

Find the active session file. Get current time via `date -Iseconds` (Bash). Compute `actual_min = floor((now - started_seconds) / 60)`.

**Stop-time correction (bidirectional)**: the wakeup time is rarely the actual stop time. Two patterns are common:

- *Late*: wakeup fires, but the user stepped away from the desk and only sees it minutes later (very ADHD-typical).
- *Early*: user stopped working before the wakeup (e.g. finished early, got pulled into a meeting, hit a blocker and parked it).

Either way, ask once:

> "Wakeup fired at HH:MM. Was that roughly when you stopped? Or did you keep working / stop earlier? Tell me the actual stop time if different."

Use the user-corrected time for `actual_min`. If they say "now is fine", use the wakeup time. **Timezone note**: keep all times in local (`+10:00` Sydney/Melbourne for David); don't mix UTC and local in the math or `actual_min` will lie by hours.

Ask **four** questions:

1. **What got done?** (factual, in user's own words)
2. **What threw you off?** (cold-start cost, scope creep, tooling, distraction, ambiguity)
3. **Tag confirm** - is `{task_type}` still the right tag, or rename?
4. **How do you feel?** (flow / drained / over-cooked / good)

**Anti-self-blame guard rail**: if the user's answer to question 2 moralises ("same pattern I always hit", "I'm useless at this", "should have known better"), do NOT validate or amplify. Reflect it back as data, neutrally:

> "Noted - logging that as an indecision-pattern signal for the tag history. Useful for next time."

Do not editorialise further. Do not therapy-mode. The skill's job is to capture signals, not to process them.

Compute the time data:

| Field | Value |
|---|---|
| Estimate | `{time_box_min}` min |
| Actual | `{actual_min}` min |
| Ratio | `{actual_min / time_box_min:.2f}x` |

After user answers, update the session file:

- Frontmatter: `status: completed`, add `finished: YYYY-MM-DDTHH:MM:SS`, `actual_min: N`
- Body under "## Retro":

```markdown
## Retro (HH:MM, {actual_min} min total)

**What got done:** {answer}
**What threw off:** {answer}
**Tag:** {confirmed or new}
**Feeling:** {answer}

| Estimate | Actual | Ratio |
|---:|---:|---:|
| {time_box_min} min | {actual_min} min | {ratio}x |
```

Show the user a short summary. **Order depends on feeling** (drained users want the nudge first, not last):

**If feeling is `drained` / `over-cooked`** - lead with the nudge:
1. **Take a break before any next sprint.** No exceptions.
2. Sprint complete.
3. Time data (estimate / actual / ratio).
4. The "what threw off" answer (their words) - the high-value signal.
5. Path to the session file.

**If feeling is `flow` / `good`** - data first, nudge last:
1. Sprint complete.
2. Time data (estimate / actual / ratio).
3. The "what threw off" answer.
4. Path to the session file.
5. **Ride the momentum** if another sprint is queued; otherwise rest while the win is fresh.

**Do not auto-start another sprint.** Always require an explicit `/productivity-sprint start` from the user.

## Step 4b - abort

Triggered by `/productivity-sprint abort`. ADHD users who bail mid-sprint deserve a clean exit, not a zombie active session and a guilt spiral.

Find the active session file. Compute `actual_min` (same logic as Step 4). Ask **one** question only:

> "Aborting the sprint - one line on why? (Stuck, distracted, scope wrong, lost interest, called away - whatever's true.)"

Update the session file:

- Frontmatter: `status: aborted`, `finished: YYYY-MM-DDTHH:MM:SS`, `actual_min: N`
- Append to body:

```markdown
## Aborted (HH:MM, {actual_min} min in)

**Why aborted:** {answer}
```

Show **two lines** and stop:

1. "Logged as aborted. No retro - that's fine."
2. "Path: {session file}"

Do not retro. Do not editorialise. Do not suggest restarting. The user gets to bail without paying a coaching tax.

## Step 5 - today / week rollup views

For `today`: glob `sessions/{today_date}-*.md` and render a table. **Include all statuses** (active, completed, aborted) - aborted sprints are valid signal:

```
| Time | Task type | Goal | Estimate | Actual | Ratio | Status |
```

For `week`: compute the ISO week's date range (Mon-Sun), glob `sessions/{date}-*.md` for each date, render same table grouped by day. At the bottom, summary stats: total sprints (broken down by status), total time, average ratio per task_type (excluding aborted from the ratio calc), list of "threw off" tags as a cloud (count words in the "What threw off" answers across the week).

## Migration helper (one-off)

If args is `migrate-from-repo`: scan the user's current working directory and known repo paths (provided in `~/.claude/projects/.../memory/`) for any `productivity-coach-*` or `2026-05-06-productivity-coach-skill.md` files. Move them to the OneDrive sessions folder, log what moved, leave a stub at the original location pointing at OneDrive.

## ADHD-aware design notes (for Claude executing this skill)

- **Batch questions**: ask all 3-4 questions in one message, accept answers in any format. Drip-feeding questions creates context-switch friction.
- **Plain language always**: no jargon, no acronyms. The user is often mid-flow and cognitively loaded.
- **Don't moralise on overruns**: report the data, don't editorialise. Overrun ≠ failure. Sent ≠ on-time.
- **Defer perfectionism**: if the user says "just write it", do not ask for more detail. Capture what's there and move on.
- **Recognise scope creep as a separate signal from estimation error**: if a sprint overruns because the user (or you, the assistant) added work mid-flight, the time-box wasn't wrong - the scope grew. The mid-check captures this distinction.
- **Cold-start cost is real and unbudgeted by default**: the first 5-10 min after a context switch are warm-up, not productive. Time-box should account for this; do not pretend it's free.

## v0 limitations (will be iterated)

- No "sub-agent for wording / motivation when stuck" - that's v1.
- No automatic time-blindness watchdog ("you said 30 min, you're at 90 min, breathe") - v1.
- No drift detection across sessions ("3 doc-authoring sprints in a row ran 1.5x+ - your default should be 45 not 30") - v1, requires history accumulation.
- No proposed time-box from history - v1, after enough data points (~5+ per task_type).
- Today/week rollups are generated on demand from session files - no separate rollup files. Iterate later if performance becomes a concern (unlikely for personal-scale data).
- Migration helper is naive - manually verify before deleting from old locations.
