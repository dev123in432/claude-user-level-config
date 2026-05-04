---
name: hello
description: Session start orientation. Only use when explicitly invoked via /hello -- do not trigger automatically.
allowed-tools: Read, Grep, Glob, Bash, Agent, Write
---

Get me up to speed on where we are. The goal is fast orientation -- not a full readout. Keep the main context lean; use a subagent for the heavy reading.

## Step 1: Detect where we are

Check the current working directory. Two modes:

**Hub mode** -- we're in the claude-assistant repo (`claude-assistant/` in the path).
**Project mode** -- we're in any other repo.

## Step 2: Get git state (quick, do this yourself)

Run these directly (not in a subagent):

```bash
git log --oneline -5
```
```bash
git status --short
```

Hold onto the output for Step 4.

## Step 2.5: Git activity heat map (project mode only)

Skip in hub mode. In project mode run these directly (not in a subagent):

```bash
git log --since="7 days ago" --name-only --pretty=format: \
  | grep -v '^$' \
  | grep -vE '\.pbi/|/visuals/|/pages/|SemanticModel/definition' \
  | sort | uniq -c | sort -rn | head -15
```

```bash
git log --since="7 days ago" --pretty=format:"%h %ad %s" --date=short | head -15
```

If the first command returns fewer than 5 rows, fall back to "last 20 commits" instead:

```bash
git log -20 --name-only --pretty=format: \
  | grep -v '^$' \
  | grep -vE '\.pbi/|/visuals/|/pages/|SemanticModel/definition' \
  | sort | uniq -c | sort -rn | head -15
```

Hold the heat map output for Step 5. You will display it as the "Recent activity" section, applying adaptive roll-up:

- Group rows by parent folder.
- If a parent folder has 3 or fewer files in the heat map, show them individually.
- If a parent folder has more than 3 files, collapse to one line: `path/ - N files (top: a.md, b.md)` showing only the two most-touched filenames.
- If a folder has subfolders that themselves cross the threshold, roll those up at the deeper level too.
- Mark files that also appear in `git status --short` as "(also uncommitted)".
- "Uncommitted only" lists files in `git status` whose path didn't appear in the commit log at all.

## Step 3: Gather context (via subagent)

Spawn a single Explore subagent to do the reading. This keeps the heavy file content out of the main conversation. The subagent should return a short structured summary -- not raw file contents.

Important: the subagent must use only Glob, Read, and Grep tools. Do NOT give it Bash access.

### Hub mode -- tell the subagent:

```
Prompt for the agent:
- You are the orientation agent for the /hello skill.
- Your job: read project files and return a structured summary. Use only Glob, Read, and Grep.
- Read these files and extract:
  1. today.md -- is the date today's date? What's the current focus?
  2. tasks.md -- list Active items (one line each) and Waiting/Blocked items (one line each)
  3. For active projects (do this in order):
     a. Grep tasks/*/context.md for "^status:" and "^priority:" -- build a map of folder to
        status and priority.
     b. If a folder's context.md is missing status or priority in its frontmatter, show
        "not found" for the missing field(s) in the summary so the user can fix it.
     c. For folders with status active or blocked: read context.md AND tasks.md (if present).
        Extract "What I was doing" and "What's next" (or first unchecked item from tasks.md).
        If status is "blocked", put in Blocked/Waiting instead of Project Snapshots.
        Also look for any @due: tags in tasks.md -- if a due date is within 7 days or overdue,
        flag it with the date.
     d. For folders with status pointer: find the "Repo:" line in context.md, read context.md
        and tasks.md from that external path instead.
     e. Skip folders with status backlog, complete, or cancelled entirely.
     f. Sort the Project Snapshots section by priority (1 first, then 2, then 3). Within the
        same priority, items with upcoming/overdue due dates come first.
  4. bugs.md -- list any unresolved bugs (one line each)
- Return the summary as bullet points grouped by: Today's Focus, Active Tasks, Blocked/Waiting, Project Snapshots (one line per project, sorted by priority), Open Bugs.
- For Project Snapshots, prefix each line with [P1], [P2], or [P3]. If a task has a due date within 7 days, append "due YYYY-MM-DD". If overdue, append "OVERDUE YYYY-MM-DD".
- Keep it tight -- 3-5 bullets per section max. One line per bullet. Skip empty sections.
```

### Project mode -- tell the subagent:

```
Prompt for the agent:
- You are the orientation agent for the /hello skill, running in Project mode.
- Your job: figure out where we are and what we're working on. Use only Glob, Read, and Grep.
- Check these local sources (skip any that don't exist):
  0. docs/status/focus.md -- if it exists, read it and extract the Priorities list (everything under "## Priorities") plus the Updated: line. Compare Updated: to today's date; if more than 14 days old, flag as stale.
  1. CLAUDE.md -- project description and session guidelines
  2. tasks/ folder -- list subfolders. **A folder is "done" if it has no `task.md` or `tasks.md` (e.g. they've been renamed to `task.md.done` / `tasks.md.closed`) -- skip those entirely, do not read or report on them.** For active folders, read `task.md` or `tasks.md`, extract status line. One line per task.
  3. context.md or any */context.md -- "What I was doing" and "What's next"
  4. docs/ -- any recent session summaries or status files
  5. STATUS.md, PLAN.md, rebuild-plan.md -- extract current status if present
- Reach back to hub (always do this):
  6. Derive the project name from the repo folder name or CLAUDE.md
  7. Read C:\Users\dinne\repos\dev123in432\claude-assistant\tasks.md -- find any line referencing this project
  8. If a tasks/{project}/ subfolder exists in claude-assistant, read its context.md and tasks.md
- Return bullet points grouped by: This Fortnight's Focus (from focus.md if present, else omit), Project Overview (one line), Current Status, What's Next, Blocked/Waiting.
- For This Fortnight's Focus: list the focus.md Priorities verbatim. Prepend "(stale - last updated YYYY-MM-DD)" if Updated: is over 14 days old. If focus.md does not exist, OMIT this section and instead include a single-line note "no docs/status/focus.md - consider creating one" in your output so the main turn can surface it.
- One line per bullet, 3-5 bullets per section max. Skip empty sections.
```

## Step 4: Write status report (hub mode only)

Only do this in hub mode. Skip entirely in project mode.

Check if `status-report.md` already exists and has today's date in its "Generated:" line. If today's date is already there, skip writing entirely. If the file doesn't exist or the date is from a previous day, write it fresh.

The file should contain:

```markdown
# Status Report
Generated: {YYYY-MM-DD HH:MM}

| # | Project | P | Status | Summary |
|---|---------|---|--------|---------|
| 1 | {folder name} | {priority} | {status} | {one-sentence summary} |
...
```

Rules:
- Only include projects with status active, blocked, or pointer. Skip backlog, complete, and cancelled.
- Sort by priority then status (active → blocked → pointer).
- The summary column is one short sentence -- what the project is or what's happening in it.
- Use the data already gathered by the subagent in Step 3 -- do not re-read files.
- If a project had missing frontmatter (noted in Step 3), show "?" for its priority and status columns.

## Step 5: Present the orientation

Combine the subagent's summary with the git state from Step 2.

### Hub mode template

```
## Where we are
claude-assistant hub

## Status
{bullets from the subagent -- today's focus, active tasks, what's next, blockers}

## Git
{branch, last commit, clean/dirty}

## Suggested next step
{the single most actionable thing based on what you read}
```

### Project mode template

```
## This fortnight's focus
{Priorities verbatim from docs/status/focus.md, prefixed with stale flag if applicable. Omit section if no focus.md and add a one-line nudge to "Suggested next step" instead.}

## Recent activity (last 7 days)
{Heat map output from Step 2.5, with adaptive roll-up applied. Group by parent folder; collapse folders with >3 files to "path/ - N files (top: a, b)". Mark files also in git status as "(also uncommitted)". Add an "Uncommitted only:" line for files in git status that didn't appear in the commit log.}

## Where we are
{project name and one-line description}

## Current status
{what we were doing, what's next, blockers -- from local files and hub reach-back}

## Git
{branch, last commit, clean/dirty}

## Worth a look
{Cross-check focus.md against the heat map. Include a bullet only when something has actually drifted:
 - A focus.md priority has zero matching paths in the 7-day heat map and none in git status (might be stalling or stale).
 - A path with >2 hits in the heat map (or its parent folder) does not appear anywhere in focus.md (might deserve to).
 Skip the section entirely if there's no divergence. Max 2-3 lines.}

## Suggested next step
{the single most actionable thing based on what you read}
```

Keep the whole output under 35 lines. This is a launchpad, not a report. If I want to dig deeper, I'll ask.
