---
name: task-hygiene
description: Audit task folders for file role violations -- tasks in the readme, narrative in task files, missing files, stale temps. Read-only scan with summary report.
disable-model-invocation: true
allowed-tools: Glob, Read, Bash
---

Audit task folders for file hygiene violations. This is a read-only check -- do not modify any files.

## Arguments

The user may provide a path after `/task-hygiene`. If provided, scan that path. Otherwise default to `tasks/` in the current working directory.

## Step 1: Find task folders

Use Glob to find all `tasks/*/` folders (or the provided path). Exclude any folder starting with `_` (template folders like `_context-template`).

Collect the list of folder names to audit.

## Step 2: Audit each folder

For each task folder, read all `.md` files present and check the rules below. Track issues in two categories: VIOLATION (must fix) and WARNING (review).

### Rule 1: the orientation file must not contain checkbox items

Read `readme.md` (or `context.md` in older folders) if it exists. If any line matches `- [ ]` or `- [x]` (case-insensitive for the x), flag as VIOLATION:
> `{folder}/readme.md`: Contains checkbox task items -- these belong in task.md/tasks.md

### Rule 2: task.md / tasks.md must not contain narrative sections

Read `task.md` or `tasks.md` if either exists. If the file contains any of these heading patterns (case-insensitive), flag as VIOLATION:
- `## What I was doing`
- `## What's next` (when used as a narrative section heading, not a task group)
- `## Decisions made`
- `## Key files`
- `## Open questions`

> `{folder}/tasks.md`: Contains narrative section "{heading}" -- this belongs in readme.md

### Rule 3: STATUS.md should be concise

Read `STATUS.md` if it exists. For each section (text between `##` headings), count lines that are NOT blank, NOT table rows (starting with `|`), and NOT headings. If any section has more than 5 such prose lines, flag as WARNING:
> `{folder}/STATUS.md`: Section "{heading}" has {n} lines of prose -- STATUS.md should be tables and brief summaries only

### Rule 4: Check for tmp/ contents

Use Glob to check for any files in `{folder}/tmp/`. If files exist, flag as WARNING:
> `{folder}/tmp/`: Contains {n} file(s) -- review whether these are still needed

### Rule 5: Missing task file

If the folder contains neither `task.md` nor `tasks.md`, flag as WARNING:
> `{folder}`: No task.md or tasks.md found -- every active task folder should have one

### Rule 6: Run the deterministic structure linter

The `task-tidy` skill bundles `task_md_lint.py`, the executable form of the task-doc structure rules (`~/.claude/skills/task-tidy/task-docs.md`). Run it read-only over the same target so this audit catches what the heading greps above miss -- stacked PICKUP blocks, undated `[x]` clusters, un-triaged `## Inbox from` dumps, pasted output / wide tables, `>>` author notes, `### Done` archive blocks, and readme.md carrying live state:

```bash
python "$HOME/.claude/skills/task-tidy/task_md_lint.py" --all --check
```

For a single provided path, use `--file {path}/task.md` and `--file {path}/readme.md` instead. Fold each linter finding into the report: a `[VIOLATION]` line is a VIOLATION, a `[WARNING]` line is a WARNING, attributed to the file the linter names. Do not re-implement its checks here -- it is the single source of truth, so if a rule needs changing, change the script.

## Step 3: Determine folder status

For each folder:
- **VIOLATION** if any Rule 1, 2, or 6 VIOLATION issues found
- **WARNING** if any Rule 3, 4, 5, or 6 WARNING issues found (but no violations)
- **CLEAN** if no issues

## Step 4: Output the report

Print the report in this exact format:

```
## Task Folder Hygiene Report
Date: {YYYY-MM-DD}

| Folder | Status | Issues |
|--------|--------|--------|
| {folder-name} | {CLEAN/WARNING/VIOLATION} | {brief description or "None"} |

### Violations (must fix)
- `{folder/file.md}`: {description}

### Warnings (review)
- `{folder/file.md}`: {description}
```

If there are no violations, replace the Violations section with: `No violations found.`
If there are no warnings, replace the Warnings section with: `No warnings found.`

## Rules

- **Read-only** -- do not modify, move, or delete any files
- Use Glob and Read for all file inspection
- Use Bash only if needed for date comparisons on tmp files -- do not use `2>/dev/null` or `${}` variable substitution in Bash commands
- Process folders in alphabetical order for consistent output
- If the target path does not exist or contains no task folders, say so and stop
