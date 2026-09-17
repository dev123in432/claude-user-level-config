# Structure, KPIs and framing

This is the canonical shape of an Accelerate operations deep dive output. Keep it
consistent quarter to quarter so the documents are comparable over time.

## Document structure (both Word versions)

1. **Purpose and context** - what the war room was, who ran it, when, and what the document covers.
2. **What's working well** - the wins worth protecting, as a grouped list.
3. **What needs to change** - the gaps, grouped into themes (usually 4-6). Each theme is a short heading plus 2-4 sentences of plain prose. Don't bullet every gap; let the prose carry it.
4. **Decisions made** - the calls settled in the room, as a list. These are not up for re-litigation.
5. **Operating KPIs** - the scorecard table: KPI, target, owner, cadence, source.
6. **Accountability model** - three layers: the CEO, the operations owner, and the team (by role, named where the seat is filled).
7. **The 30 / 60 / 90 plan** - three phase tables (Action / Owner / Done when).
8. **Ideas to pursue** - things that sit alongside the plan rather than inside it.
9. **Appendix: team structure** - the org chart, if supplied.
10. **Confidential annex** - confidential version only. Pay/role changes, sensitive resourcing, the owner's own load.

## The 30 / 60 / 90 plan

Anchor the plan to a start date (a Monday reads best). The three phases are fixed:

- **Days 0-30: define and decide** - agree the standards, write the roles, stand up the systems. Foundations.
- **Days 31-60: embed** - operationalise the decisions. Cadence running, data flowing.
- **Days 61-90: optimise and hold** - measure, prove it on a live case, lock it into business as usual.

The build script computes the date ranges from the start date, so you only supply the start. Every action gets one owner and one observable "done when" - if you can't say how you'd know it's done, the action is too vague.

## Accountability

Three layers, always:

- **CEO** - the calls only the CEO can make: policy, contracts, remuneration, resourcing. Holds the operations owner to the KPIs.
- **Operations owner** - owns the operating system end to end: ratifies roles, runs the scorecard, builds the cadence.
- **The team** - assign by role (Practice Leads, Tech Leads, PMO, Project Managers), and name the individual where the seat is filled. Turn empty seats into recruitment actions in the plan rather than leaving them blank.

## Standard Accelerate operations KPI catalogue

Anchor on what surfaced in the room, then fill gaps from this catalogue. Each KPI needs a target, an owner, and a cadence - a number with no owner is noise.

| KPI | Typical target | Owner | Cadence | Source |
|---|---|---|---|---|
| Forecast utilisation | 75-100% | Practice Leads | Weekly | Resource Guru |
| Actual utilisation | 75-100% | Practice Leads | Weekly / monthly | D365 timesheets |
| Project probability (actual) | 55% or above | Project Managers | Monthly, per project | D365 Projects |
| Projects over or forecast over budget | Every at-risk project flagged with a recovery plan; none unmanaged | Project Managers | Weekly | D365 Projects |
| Timesheet compliance | 100% entered daily | Everyone; Practice Leads enforce | Weekly | D365 timesheets |
| Pre-sales time captured | 100% logged with a description | Practice Leads | Weekly | D365 timesheets |
| Estimate vs actual variance | Within 10% either way at sprint close | Tech Leads and PMs | Per sprint | DevOps + D365 |
| D365 Projects and milestone currency | 100% of active projects current | PMO | Weekly | D365 Projects |
| DevOps board currency | Updated daily | Tech Leads | Weekly | Azure DevOps |
| Requirements ratified against contract | 100% after workshops | Practice Leads and PMs | Per project | Project record |
| Performance reviews completed | 100% of direct reports each cycle | Operations owner and Practice Leads | Quarterly | HR |

Don't ship every row by reflex. Use the ones the workshop actually raised plus the few hygiene metrics that make the plan measurable.

## Confidentiality model

A deep dive almost always surfaces things that should not go to the whole leadership group: individual pay and role changes, candid performance notes, moving a named person off engagements, the operations owner's own meeting load. Handle these by producing two versions:

- **Confidential** - for the CEO and the operations owner. Everything, including the annex.
- **Team** - for the direct reports and any wider leadership recipients. The annex is removed, confidential plan actions are dropped, and anything people-specific is sanitised to role level (for example, "reduce the owner's meeting load" becomes "delegate the recurring delivery forums to the leads", which is a genuine team-facing action rather than a redaction).

In the content file, mark sensitive plan actions with `"confidential": true`. If a sanitised team-facing version exists, put it in `"team_action"` and it will replace the confidential wording in the team version instead of dropping the row.

A readout **deck never carries confidential content** - it is always built from the team-safe view.
