# Confirm, submit, verify (timesheet write)

Verified against Live 2026-08-11 (copied a full week onto the current week).

## 1. Confirm before posting — click-to-submit

Show the full proposed entries as a compact table: date (DD/MM), hours, Job Number + short name, and the
exact description text, plus the running day (and week) total. Then **always** confirm via
`AskUserQuestion` with Submit / Edit / Cancel — never rely on the user typing "submit". Descriptions go on
client invoices.

- On **Edit** / free-text correction: apply it, re-render the table, re-ask. Never skip the re-confirm.
- On **Cancel**: log the rejection to `recent-submissions.md` so items aren't re-proposed.

If copying a prior week, read the source range first with a single
`timeslot_dayview(date, endDate)` (≤7 days) and replicate each entry onto the matching target day.

## 2. Submit via `timeslot_upsert`

One call, `entries` = a JSON array (batch). To **create**: `projectID` + `date` + `workedHrs` +
`description`. To **update**: `timeSlotID` + only the changed fields.

```
timeslot_upsert(entries: [
  {"projectID": 5678, "date": "2026-03-30", "workedHrs": 8,
   "description": "Analyse and resolve the reported issue."}
])
```

- **`projectID` is the projectID from `project_search` / dayview metadata — NOT the Job Number.**
  (e.g. Job 1001234 = projectID 5678 — always pass the projectID, not the Job Number.)
- **Hours**: 0.25 multiples, round **up**. `chargeHrs` / `noChargeHrs` are server-calculated.
- **Charge adjustments** (own entries too): `bookedHrs` above `workedHrs` = uplift, below = write-down;
  `noChargeOverride` > 0 = write-off. Compare `bookedHrs` vs `workedHrs` before uplifting (re-uplift
  compounds).
- **UDEFs** (custom fields like `PBI#`): `udefs: {"PBI#": "50036"}`. Set `skipUdefs: true` to mute the
  UDEF hint when batch-creating.
- New entries land as **Submitted**. Capture each returned `timeSlotID` to `recent-submissions.md`.

## 3. Verify (read-after-write)

Re-read the day/range with `timeslot_dayview` and confirm the totals, entries, and status match what you
posted. Tell the user the day (and week) totals and what changed. Don't save a local copy — GO is the truth.

## Deleting entries — `timeslot_delete` (proven 2026-08-11)

`timeSlotID` (single int or JSON array) + `date` if the day isn't loaded this session. Batch deletes report
each ID individually ("N entry — deleted") — check before telling the user all deleted. **Destructive:
always confirm exactly which entries first**, then re-read the day to verify they're gone. Invalidates the
project estimate cache.

## Description quality

Validate every chargeable (T/F/P) description against the **live** `timeslot_description_standards`
(fetch it in preflight — see [`description-standards.md`](description-standards.md)). When copying an
already-approved entry verbatim (e.g. a fixed-price "see monthly summary" line), keep it as-is rather than
"correcting" an established per-job pattern.
