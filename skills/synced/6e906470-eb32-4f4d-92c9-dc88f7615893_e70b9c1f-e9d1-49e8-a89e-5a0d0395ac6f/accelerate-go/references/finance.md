# ③ Finance / reporting

Time-and-charges views and finance exports. The `*_time_and_charges` tools write **CSV/XLSX straight to
disk without using LLM tokens** — fast for large pulls. They return the full path. Default location:
**Downloads** (Chat mode) or the working directory (CoWork mode). **Read + self export proven on Live
2026-08-11.**

> **Role scoping (as designed).** Self-scoped reads work for everyone (`resource_time_and_charges` defaults
> to the signed-in user). All-resource / other-person queries and `resource_search` are **manager
> capabilities** available to elevated GO roles. On a standard role those return a permission scope (seen
> 2026-08-11: `resource_search` → "Forbidden") — the skill catches it and works with the user's own data.

## Tools

| Tool | Purpose | Hint |
|---|---|---|
| `project_browse` | Browse customers/projects (OPEN/CLOSED/ALL) | ReadOnly |
| `project_search` | Find a project by name/customer/code | ReadOnly |
| `project_time_and_charges` | Estimate status + actuals + multi-project CSV/XLSX export | ReadOnly |
| `resource_time_and_charges` | A resource's T&C with leave + date filters (CSV/XLSX) | ReadOnly |
| `resource_time_and_charges_finance_export` | Enriched finance export (hours, ancestry, invoice refs) → Downloads | ReadOnly |

## Flow

1. **Scope** — which project(s) or resource(s), which date range, and the output the user wants
   (inline summary vs a spreadsheet they'll open).
2. **Export** — prefer `format: xlsx` (or csv) for large pulls so it lands on disk without burning tokens;
   use inline detail only for small windows.
3. **Report** — give the filename + full path, and a short summary of what's in it.

For estimate status, `project_time_and_charges` returns NO ESTIMATE / IN ESTIMATE / OVER ESTIMATE per
project.

## Output shapes

- `resource_time_and_charges(startDate, endDate)` → summary with **Worked / Chargeable / Non-chargeable**
  hours, **Revenue**, **Leave**, and entry count. The chargeable/non-chargeable split feeds the
  billable-% picture directly.
- `project_time_and_charges(projectID)` → **Revenue**, entry count, and estimate status
  (NO ESTIMATE / IN ESTIMATE / OVER ESTIMATE). `format: estimates` gives a compact one-liner; `detail` a
  per-entry view.
- `resource_time_and_charges(…, format: "xlsx")` → writes `TimeWorked_[name]_[range].xlsx` to Downloads.
  Prefer `xlsx`/`csv` for files — do NOT build the file yourself from `detail`.

`resource_time_and_charges_finance_export` — all-resource finance export, a two-sheet workbook
(TimeAndCharges + Projects) to Downloads; a manager/finance capability for elevated GO roles.
`project_browse` proven (customer-grouped, status filter, paginates). TODO: document worked examples of the
`filterTimeSlotStatus` / `projectStatus` filters.
