# Mapping activity to jobs

For each candidate addition, decide job (+ projectID), hours, and description. Signal strength for the
job, strongest first. (Adapted from O33.)

1. **Explicit direction in text (strongest).** Scan calendar bodies, sent/inbound mail, and chats for
   "use job 1064487", "bill to project X", "charge this to <name>", "Job#", "PBI 50036". An explicit
   mention overrides every pattern guess — **quote the source line** in the draft so the user can spot a
   misread.
2. **User favourites.** `favourite_list` → `(projectID, job, default description)` the person curated.
   Favour their own favourite text when drafting a description.
3. **4-week pattern.** `patterns.md` summarises the last four weeks of their own entries (job → typical
   work, description stems). Refreshed weekly (see [`knowledge-caches.md`](knowledge-caches.md)).
4. **Colleague cross-reference.** For an ambiguous meeting, check what another attendee billed →
   [`impersonation.md`](impersonation.md) option 1.

**Hours**: 0.25 multiples, round up; default to the meeting's duration. Desk blocks with no meeting → ask.
**Description**: validate against the live standards ([`description-standards.md`](description-standards.md)).
Mark each candidate `[OK]` or `[?]` so the uncertain ones can be batched to the user.
