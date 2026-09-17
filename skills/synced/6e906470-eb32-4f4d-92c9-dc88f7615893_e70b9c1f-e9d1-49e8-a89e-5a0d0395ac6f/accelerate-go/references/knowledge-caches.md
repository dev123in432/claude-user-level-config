# Knowledge caches

Files inside the preferences folder. GO is the source of truth for *what's logged*; these hold *knowledge
that helps future runs*. (Adapted from O33.)

```
<preferences-folder>/
├── patterns.md              # job → typical work; description stems; refreshed weekly
├── projects.md              # Job # ↔ projectID crib sheet (e.g. Job 1001234 ↔ projectID 5678)
├── preferences.md           # durable user choices (date format, week length, conventions)
├── resolved-ambiguities.md  # meeting-type → job learnings
├── holidays.md              # locale + public holidays (see holidays.md)
└── recent-submissions.md    # last ~14 days of submissions + rejections + policy decisions
```

- **patterns.md** — distil from `resource_time_and_charges(<4 weeks>, format: detail)` weekly (first run of
  a new Monday, or on request). Capture typical work per major job, description stems, chargeable vs
  internal mix.
- **projects.md** — append new Job # ↔ projectID ↔ customer ↔ billing-type mappings as `project_search` /
  `favourite_list` reveal them.
- **recent-submissions.md** — each row: `timeSlotID`, date, job, hours, one-line description. Track
  Rejected + user-Deleted items (don't re-propose) and policy decisions (apply without re-asking). Prune
  > ~14 days each run.

**Don't persist:** copies of the timesheet, daily rollups, dayview snapshots. Every run re-pulls fresh.
