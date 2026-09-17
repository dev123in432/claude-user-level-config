---
name: accelerate-go
description: Install and operate the GO Mini MCP for Accelerate Tech, the company timesheeting,
  leave, and project financials system. Use for setup (set up GO, install the GO MCP, connect
  to GO) and everyday GO tasks - log my time, update or catch up my timesheet, copy last week,
  book leave, check my leave, export my time and charges, finance report, team timesheets, or
  tidy up my GO favourites. Runs on Claude Code and Claude Desktop. Not for creating a GO project
  record or team allocation notifications (those are separate delivery skills).
metadata:
  status: beta
  scope: organisational
  clients: [claude-code, claude-desktop]
---

# accelerate-go

The company-wide skill for **GO** (Olympic Go — Accelerate Tech's timesheeting, leave, day-rate
and project-tracking system). It is the guided installer for the **GO Mini MCP** and the operating
manual for all **19** of its tools. Runs as delegated user actions: everything happens **as the
signed-in person**, and tool availability mirrors that person's GO permissions.

> **Evidence + full design:** `Helper Files & Templates/GO_MCP.md` and
> `Helper Files & Templates/GO_MCP_design/accelerate-go-skill-design.html`. Read `GO_MCP.md` before
> extending this skill — it holds the proven install invocation, the tool surface, and the auth gotcha.

> **STATUS (2026-08-11) — proven on BOTH clients.** Claude Code and Claude Desktop: skill loads + triggers
> by intent, guided install, first-connect Entra auth, and the self-scoped modules all work on Live —
> install, timesheet read/write (copy-week), favourites, leave (full round-trip), finance/reporting (read +
> disk export), and the M365 evidence remap (calendar/mail/Teams). **Team/impersonation is a manager
> capability** — it works for GO roles that carry the permission; on standard roles it's correctly scoped
> out (that's GO's RBAC, not a gap). Pre-release polish is TODO-marked in
> `references/` (grep `TODO`): AT description overlay, per-state holidays, macOS install steps,
> billing-model-adaptive drafting. `status: beta` until impersonation is proven, polish is done, and the
> plugin is packaged for the marketplace.

> **Tool validation matrix:** every one of the 19 tools' tested behaviour, params, and gates is recorded in
> [`references/tool-validation.md`](references/tool-validation.md) (15/19 proven self-scoped; 4 elevated-role).

## Availability depends on the person's GO role (tell the user)

The skill reaches all 19 tools, but **what any individual can actually do is gated by their GO role — same
as the GO app.** The MCP runs as the signed-in person. Standard/self-scoped users get their own
timesheets, leave, favourites and finance; **team/impersonation and cross-person views need an elevated
(approver/admin) GO role.** When a call returns Forbidden (e.g. `resource_search` on a Basic role), say so
plainly — it's a GO permission, not a skill fault — and fall back to self-scoped data. This is stated for
end users in `README.md`; keep that note accurate. Sorting who has which GO role is a rollout step.

## When to use

- **Setup / onboarding:** the person doesn't have GO connected yet, or says "set up / install / connect
  GO". Run the guided install → [`references/install.md`](references/install.md).
- **Daily timesheet:** "log my time", "catch up my timesheet", "copy last week onto this week".
- **Leave:** balances, list, preview against holidays, submit, cancel → [`references/leave.md`](references/leave.md).
- **Finance / reporting:** time-and-charges and finance exports (CSV/XLSX to disk) →
  [`references/finance.md`](references/finance.md).
- **Team / manager:** view or act on another person's timesheet (permission-gated) →
  [`references/impersonation.md`](references/impersonation.md).
- **Favourites:** tidy up saved templates → [`references/favourites.md`](references/favourites.md).

## When NOT to use

- Creating the GO **project** record at project kickoff → `accelerate-go-create-project`.
- Notifying a team their allocation is live → `accelerate-go-timesheet-notify`.
- Anything in the GO **web UI** directly — this skill drives the MCP, not the browser.

## Required MCPs

- **go-mini-mcp** — the 19 GO tools. Registered by the install flow (Code) or the `.mcpb` (Desktop).
  If it isn't connected, run [`references/install.md`](references/install.md) first.
- **claude.ai Microsoft 365 connector** — the evidence source for drafting timesheets (calendar, mail,
  Teams). See [`references/evidence.md`](references/evidence.md). Not needed for install, leave, finance,
  or favourites — only for evidence-led timesheet drafting.

Both are usually deferred — load via `ToolSearch` before first use.

## Invariant rules (always)

- **GO is the single source of truth.** Never mirror the timesheet locally — re-pull
  `timeslot_dayview` each run and diff against it (activity-diff, not a time-cursor).
- **Hours are multiples of 0.25**, rounded **up** (0.1h → 0.25h). System-enforced.
- **Description standards come from the live `timeslot_description_standards` call every run** — never
  cached. Descriptions appear on client invoices. See [`references/description-standards.md`](references/description-standards.md).
- **8h/day (40h Mon–Fri) is the default target** (confirmed from GO: leave "Weekly hours 40h", 8h/day
  entries). Flag shortfalls; **never pad** to reach it. Override per user in `preferences.md`.
- **Confirm before any write.** Show the full proposed change and get an explicit click-confirm via
  `AskUserQuestion` before `timeslot_upsert`, `leave_submit`, `favourite_manage`, or any delete/cancel.
- **Dates: DD/MM for humans, ISO only inside tool args.** All AT staff are AUS (some NZ) — never US
  (MM/DD). ISO (`2026-08-11`) only in tool-call arguments.
- **Delegated + permission-aware.** Tools resolve as the signed-in person; if a tool isn't available it's
  a GO-permission limit — degrade gracefully, tell the user, don't crash.
- **Impersonation is the highest blast radius** — never without a clear, session-authorised purpose.

## AT defaults

- Locale default **Australia** (state to be confirmed per user via preflight); timezone from the user's
  M365 profile. NZ staff supported — confirm once and persist.
- Working week **40h Mon–Fri (8h/day)** unless the user overrides in `preferences.md`.
- British/Australian English in descriptions (GO's standards enforce this too).

## Workflow — routing

Route on intent, then follow the named reference.

1. **GO not connected / "set up GO"** → [`references/install.md`](references/install.md) (guided install +
   first-connect + verify). This is step ⓪ — the skill IS the installer once it's on the machine.
2. **Timesheet drafting** ("log my time", "copy last week") → preflight →
   [`references/preflight.md`](references/preflight.md), pull evidence →
   [`references/evidence.md`](references/evidence.md), diff vs `timeslot_dayview`, map jobs →
   [`references/job-mapping.md`](references/job-mapping.md), confirm + submit →
   [`references/submission.md`](references/submission.md).
3. **Leave** → [`references/leave.md`](references/leave.md). **`leave_balance` is empty here by design** —
   GO isn't the balance system of record; AT tracks accruals in a separate HR system and GO holds only
   leave *requests*. For "my balance / leave left", say balances live in the HR system and show `leave_list`
   (the accurate booked-leave record). Never present the 0h "01/01/0001" sentinel as real or say "no leave".
4. **Finance / reporting** → [`references/finance.md`](references/finance.md).
5. **Team / impersonation** → [`references/impersonation.md`](references/impersonation.md).
6. **Favourites** → [`references/favourites.md`](references/favourites.md).

Timezone handling ([`references/timezones.md`](references/timezones.md)), holidays
([`references/holidays.md`](references/holidays.md)), the knowledge folder
([`references/preferences-folder.md`](references/preferences-folder.md),
[`references/knowledge-caches.md`](references/knowledge-caches.md)) support the above.

## Error handling

| Scenario | Response |
|---|---|
| GO tools not present | Run the install flow (`references/install.md`); they load after a restart. |
| First connect fails `AADSTS50011` | The env's Entra app reg is missing `http://localhost`. See install.md — needs an Entra admin. |
| Browser sign-in times out (90s) | The auth tab opened — complete sign-in + MFA, then retry the call. |
| A tool returns a permission error | GO-permission limit for this person. Tell them; suggest the next option (e.g. finance export vs impersonation). |
| M365 call unavailable | Evidence step degrades — draft from GO patterns + ask the user; note the gap. |

## Quality checklist

- [ ] Re-pulled `timeslot_dayview` this run (no cached sheet).
- [ ] Fetched live `timeslot_description_standards` and validated every chargeable description.
- [ ] All hours are 0.25 multiples.
- [ ] Showed the full proposed change and got an explicit click-confirm before writing.
- [ ] Read-after-write: re-read the day/record to confirm it landed.
- [ ] Any destructive/impersonation action had explicit, purpose-scoped confirmation.
