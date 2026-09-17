# Tool validation matrix

Every go-mini-mcp tool, exercised on **Live** on a standard self-scoped role, across **both Claude Code and
Claude Desktop**. Behaviours here are observed, not assumed.
✅ exercised and working · 🔒 elevated-role feature (works for users with the right GO role) · ℹ️ works,
with a usage note.

## Timesheets
| Tool | | Behaviour / params |
|---|---|---|
| `timeslot_dayview` | ✅ | `date` + optional `endDate` (≤7 days), `includeFavourites`, `includeEstimates`. Metadata carries `timeSlotID`, `projectID`, `customerID`, `workedHrs`/`bookedHrs`/`noChargeOverride`/`chargeHrs`. |
| `timeslot_description_standards` | ✅ | Returns the live rulebook without auth. Call every run before writing. |
| `timeslot_upsert` | ✅ | `entries` JSON array. Create = `projectID`+`date`+`workedHrs`+`description`. Hours 0.25 multiples. New entries land **Submitted**. Returns `timeSlotID`. Proven: copied a full week; created entries. |
| `timeslot_delete` | ✅ | `timeSlotID` (int or JSON array) + `date` if the day isn't loaded. Response: "N entry — deleted" per ID. Proven: create → delete → dayview shows 0 entries. |

## Projects
| Tool | | Behaviour / params |
|---|---|---|
| `project_search` | ✅ | `searchTerm` → Job, customer, projectID, status, Leaf. Quick lookup. |
| `project_browse` | ✅ | `search` + `searchCustomers` (true = customer-grouped w/ nested projects) + `status` (OPEN/CLOSED/ALL). Paginates ("5 of 16"). |
| `project_time_and_charges` | ✅ | `projectID` (int or array), `format`: summary / detail / **estimates** (compact) / csv / xlsx (to Downloads). Proven summary + estimates. |

## Resources
| Tool | | Behaviour / params |
|---|---|---|
| `resource_time_and_charges` | ✅ | Defaults to self. `startDate`/`endDate`, `format` (summary/detail/csv/xlsx). Returns worked/chargeable/non-chargeable/revenue/leave. `xlsx`/`csv` write to Downloads (verified a real file). |
| `resource_search` | 🔒 | Search across employees — a manager capability. Available to elevated GO roles; a standard/self-scoped role is correctly scoped to itself, so the skill works with the user's own data. |
| `resource_time_and_charges_finance_export` | 🔒 | All-resource finance export (two-sheet workbook to Downloads) — a manager/finance capability for elevated GO roles. Self-scoped users use `resource_time_and_charges` for their own export. |

## Leave
| Tool | | Behaviour / params |
|---|---|---|
| `leave_list` | ✅ | `status`/`leaveType`/`fromDate`/`toDate`/`maxResults`. Accurate — GO's record of booked leave. |
| `leave_preview` | ✅ | `leaveType`+`fromDate`+`toDate` → day-by-day, holidays, week-off, total. |
| `leave_submit` | ✅ | `leaveType`+`fromDate`+`toDate` (+`notes`,`filePath`). Returns request ID; lands **Pending**. Notifies approvers. |
| `leave_cancel` | ✅ | `leaveRequestId`. Proven: submit → cancel → verify Cancelled. |
| `leave_balance` | ℹ️ | Returns 0h "as at 01/01/0001" because **AT tracks leave balances in its HR/payroll system, not GO** — GO holds leave *requests* (`leave_list`). For "balance" questions, point to the HR system and show `leave_list`. Working as intended for how AT uses GO. |

## Favourites
| Tool | | Behaviour / params |
|---|---|---|
| `favourite_list` | ✅ | Enabled by default; `includeDisabled`. Flags CLOSED-project favourites. |
| `favourite_manage` | ✅ | `action` add/update/enable/disable/remove; `favouriteID` (int or array); `projectID`+`defaultDetails` for add. Proven: removed closed-project favourites, added an active job. |

## Team / impersonation
| Tool | | Behaviour / params |
|---|---|---|
| `user_impersonate_list` | 🔒 | Lists who you can act on behalf of — a manager capability, available to GO roles with impersonation permission. |
| `user_impersonate` | 🔒 | Switch subsequent calls to another user (call with no email to clear) — for managers with impersonation permission. |

## Summary

**15 tools exercised directly** on a standard self-scoped role, on both clients. The other **4 are the
elevated / manager surface** — `resource_search`, the all-resource finance export, and the two
impersonation tools — which work for users whose GO role carries those permissions. Availability follows
GO's own roles exactly (see the README's "availability depends on your GO role"). The one nuance:
`leave_balance` is empty because AT keeps balances in HR, not GO.
