# ② Leave

Check balances, list requests, preview dates against holidays/conflicts, submit and cancel — all as the
signed-in person. **Fully proven on Live 2026-08-11** (read, preview, and a submit→cancel→verify
round-trip: a request created Pending, cancelled, confirmed Cancelled via `leave_list`).

## Tools (params confirmed)

| Tool | Key params | Hint |
|---|---|---|
| `leave_balance` | `showApprovers` (bool) | ReadOnly |
| `leave_list` | `status`, `leaveType`, `fromDate`, `toDate`, `maxResults` | ReadOnly |
| `leave_preview` | `leaveType`, `fromDate`, `toDate` (all required, ISO) | ReadOnly |
| `leave_submit` | `leaveType`, `fromDate`, `toDate` (required) + `notes`, `filePath` (attachment) | Idempotent |
| `leave_cancel` | `leaveRequestId` (int, from `leave_list`) | **Destructive** |

- Leave types (enabled): Annual Leave, Sick Leave, Bereavement Leave, Special Leave, Unpaid Leave,
  Unpaid Sick Leave, Domestic Violence Leave. Pass the **name** to `leaveType`.
- Statuses (for `leave_list` filter): Pending, Approved, Declined, Reversed, Processed, Cancelled,
  PartiallyProcessed.

## Findings to handle

- **`leave_balance` is empty by design on this tenant — GO is NOT the balance system of record.** It
  returns 0h across all types "as at 01/01/0001" (a null-date sentinel). Per AT (confirmed 2026-08-11),
  **leave balances/accruals live in a separate HR/payroll system; GO only holds leave *requests*** (which
  is why `leave_list` is full and accurate). So: for "how much leave do I have left / my balance", tell the
  user GO doesn't hold balances here — those are in the HR system — and show `leave_list` for their booked
  leave. **Never present the 0h sentinel as a real balance, and never say "you have no leave".**
- **Weekly hours = 40h, 8h/day** — this is where the AT default came from. Consistent with the timesheet.
- `showApprovers` returns the approver pool (may contain duplicate names — a display quirk, ignore).

## Flow

1. **Check** — `leave_list` for existing requests (accurate); `leave_balance` for types/approvers (flag if
   balance looks unpopulated).
2. **Preview** — `leave_preview(leaveType, fromDate, toDate)`: day-by-day breakdown, holidays (don't
   consume leave), week-off days, overlaps, total. Reconcile with locale ([`holidays.md`](holidays.md)).
3. **Confirm + submit** — show dates, type, total hours; click-confirm via `AskUserQuestion`; then
   `leave_submit`. Submitting notifies approvers — treat as an outward-facing action.
4. **Cancel** — `leave_cancel(leaveRequestId)` only after an explicit confirm; show what's being cancelled.
5. **Verify** — re-read with `leave_list` and report.

`leave_submit` returns the new request ID (e.g. "#NNN created … Status: Pending"); `leave_cancel` takes
that `leaveRequestId`. Submitting notifies approvers — always click-confirm first. TODO: confirm
attachment (`filePath`) behaviour (e.g. medical certificate) — not yet exercised.
