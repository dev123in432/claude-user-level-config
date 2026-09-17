# Preflight (before any timesheet drafting)

Four things happen before drafting, every run. If any fail, stop. (Adapted from O33.)

## 1. Locate the preferences folder + load preferences

See [`preferences-folder.md`](preferences-folder.md). If missing, offer to create it. Always read
`preferences.md` first — it holds durable overrides that must apply before drafting: date format (default
DD/MM), working-week baseline (default 37.5h), description conventions, extra inbox folders, admin
roll-up rules. Missing values → use defaults; don't re-ask each run.

## 2. Confirm the M365 connector is reachable

Do a lightweight identity/profile call on the claude.ai Microsoft 365 connector (see
[`evidence.md`](evidence.md) — TODO: exact call). If it fails auth, tell the user to re-auth the M365
connector before anything else; every evidence call depends on it.

## 3. Fetch live description standards — no exceptions

`timeslot_description_standards()` every run (see [`description-standards.md`](description-standards.md)).
Never reuse a cached copy or an earlier-in-session response. If it fails, stop.

## 4. Resolve locale

Read [`holidays.md`](holidays.md) for a cached country + region + IANA timezone. If not cached: derive a
best guess from the M365 profile (country/state/city/office), confirm once via `AskUserQuestion`
(**default Australia** for AT; NZ supported), branch to the state/anniversary region, and persist.

Only proceed to drafting once all four return clean.
