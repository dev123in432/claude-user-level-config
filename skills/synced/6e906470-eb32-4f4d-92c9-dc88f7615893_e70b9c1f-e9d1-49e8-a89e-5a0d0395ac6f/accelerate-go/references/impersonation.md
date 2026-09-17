# ④ Team / impersonation

View or act on another person's GO data — for managers cross-referencing a meeting's job, running team
compliance, or logging on behalf of someone. **Highest blast radius in the skill**, so it carries the
strongest guardrails. A **manager capability**: it works for users whose GO role carries impersonation /
cross-resource permission, mirroring exactly what they can do in GO itself.

> **Role-gated, as designed.** These tools require the appropriate GO permission. On a standard
> self-scoped role the calls return a permission error (seen 2026-08-11: `resource_search` → "Forbidden";
> `user_impersonate_list` → "Attempted to perform an unauthorized operation … you may not have
> impersonation permissions") — the skill catches that, explains it's a GO role scope (not a failure), and
> works with the user's own data. For users with the right role, the flows below run normally.

## Guardrails (non-negotiable)

- **Never impersonate without a clear, session-authorised purpose the user has stated.** Confirm the
  purpose and the target person before switching.
- Surface **who** you are acting as, and confirm again before any **write** while impersonating.
- Prefer the lightest option that answers the question (read a resource's T&C, or export) over sustained
  impersonation.

## Three ways to reach another person's data

| Option | Tool(s) | Use when |
|---|---|---|
| 1. Direct read | `resource_search` → `resource_time_and_charges` (single resource, `format: detail`) | one-off meeting-to-job lookup or a few days |
| 2. Export | `resource_time_and_charges` / `resource_time_and_charges_finance_export` (`format: xlsx`) | bulk data, a spreadsheet, or a large window |
| 3. Impersonation | `user_impersonate_list` → `user_impersonate` | sustained work as one person (their dayview, favourites, entries together) |

After `user_impersonate(email)`, subsequent go-mini-mcp calls (`timeslot_dayview`, `favourite_list`,
`resource_time_and_charges`) return the impersonated person's data. **Clear impersonation by calling
`user_impersonate` with no email** — always return to yourself when done. A natural manager flow to build
out: team compliance (who hasn't submitted for the previous working day, reconciled against
leave/holidays).
