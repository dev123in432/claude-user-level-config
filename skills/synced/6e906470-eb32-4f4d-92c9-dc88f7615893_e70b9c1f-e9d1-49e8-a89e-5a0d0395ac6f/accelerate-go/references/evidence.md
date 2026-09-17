# Pull evidence (timesheet drafting) — M365 (claude.ai connector)

For each day in scope, pull the **whole day's** evidence in parallel, then diff against a fresh
`timeslot_dayview`. Candidate additions = observed but not logged. **Proven on Live 2026-08-11** against
the claude.ai Microsoft 365 connector.

## Confirmed tool mappings (claude.ai M365 connector)

| Need | Tool | Notes |
|---|---|---|
| Identity + locale seed | `get_me` | `{id, displayName, mail, userPrincipalName, jobTitle}` |
| Calendar for the day | `outlook_calendar_search(query:"*", afterDateTime, beforeDateTime, limit:25)` | events: subject, organizer, attendees, `start`/`end` `{dateTime, timeZone}`, location, `showAs`, `isCancelled`, `isAllDay`, `summary`. Full body via `read_resource(uri)`. |
| Sent + inbound mail | `outlook_email_search(folderName:"Sent Items"\|"Inbox", afterDateTime, beforeDateTime, limit)` | metadata; full body via `read_resource(uri)`. `sender`/`recipient` filters exist. With `folderName`, use `query` OR date filters, not both. |
| Teams activity | `chat_message_search(query, afterDateTime, beforeDateTime)` for content; `teams_list_chats` to enumerate chats | see caveats below |

(Was the O33 Graph-style `get-current-user` / `get-calendar-view` / `list-mail-folder-messages` /
`list-chats` — remap complete.)

## Critical findings (2026-08-11)

- **Timezone: calendar times come in the event's `timeZone` (often UTC), NOT the user's local.** Proven:
  an event `23:30 UTC on 11 Aug` is `09:30 local on 12 Aug` for an AEST user — it belongs to the **next
  local day**. Always convert with `zoneinfo` before attributing a day ([`timezones.md`](timezones.md)).
  (e.g. a Sydney-based user = `Australia/Sydney`, AEST UTC+10, no DST in August).
- **`showAs`** — skip `oof` and personal blocks (e.g. "School Pickup" was `oof`) and `isCancelled` events.
- **`teams_list_chats.lastUpdatedDateTime` is rename/membership time, NOT last-message time.** Don't use it
  to judge "active today" — use `chat_message_search` with `afterDateTime`/`beforeDateTime`. Note its scan
  is best-effort (up to 50 chats × 50 messages); it prepends a note when results are partial.
- **Billing-model adaptivity (important).** Some people (e.g. flat **Fixed Price** consulting) log a single
  8h/day block with a standing description ("…- See monthly summary."), not one entry per meeting. For them
  the flow should **confirm the flat block is present**, not itemise the day. Evidence-led itemisation is
  for **T&M / multi-project** people who split a day across jobs. Detect the pattern from the person's
  recent entries / project types and adapt — don't force itemisation on a flat fixed-price day.

## What each source tells you

- **Calendar** — meetings (duration → hours, round up to 0.25). Skip cancelled / personal / OOF.
- **Sent mail** — outgoing coordination, follow-ups, reviews.
- **Inbound mail** — what pulled the person into work; often real work with no sent reply.
- **Teams** — issue resolution, substantial responses, ad-hoc help without a calendar entry.

## Diff + draft

- Diff candidates against `timeslot_dayview`. Check `recent-submissions.md` — don't re-propose rejected or
  user-deleted items. If the person logs a flat daily block, the diff is "is the block there?" not a list.
- Map each candidate to a job → [`job-mapping.md`](job-mapping.md). Mark `[OK]` / `[?]`; batch the `[?]`
  via `AskUserQuestion`. A 30+ min block with nothing in calendar/mail/chat → ask the user directly.

## Large responses

If a tool writes a file path instead of inline content, parse it with Python and condense. Cache under
`o33-go-user-preferences/_cache/<YYYY-MM-DD>/`, disposable. (Works on Desktop + local Code; not claude.ai
web.)
