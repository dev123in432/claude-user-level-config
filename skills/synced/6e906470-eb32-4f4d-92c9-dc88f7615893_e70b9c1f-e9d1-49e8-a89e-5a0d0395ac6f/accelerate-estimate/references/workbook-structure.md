# Estimation Workbook Structure

## JSON Config Schemas

### Sprint-Based (Fixed Price)
```json
{
  "projectName": "STOE Digital Platform",
  "clientName": "Translink / TMR",
  "estimateVersion": "V1",
  "estimateDate": "2025-11-15",
  "preparedBy": "James Diekman",
  "model": "sprint",
  "financialYear": "FY26",
  "discount": 0,
  "flatContingency": null,
  "gst": 0.10,
  "sprintLength": 10,
  "phases": [
    {"name": "Solution Design", "sprints": ["S1", "S2"], "startDate": "2025-12-08", "endDate": "2026-01-16"}
  ],
  "sprints": [
    {"id": "S1", "name": "Sprint 1 (08 Dec - 19 Dec)", "startDate": "2025-12-08", "endDate": "2025-12-19"}
  ],
  "tasks": [
    {"sprint": "S1", "objective": "...", "function": "Project Manager", "rateBand": "Principal", "solutionArea": "Project Management", "allocation": 0.4}
  ],
  "paymentMilestones": [
    {"name": "Commencement", "percentage": 0.05, "dueDate": "2025-12-08", "criteria": "Signed contract"}
  ]
}
```

### Days-Per-Phase (Fixed Price)
```json
{
  "model": "phase",
  "phases": [
    {"name": "Discovery", "startDate": "2026-01-06", "endDate": "2026-01-31"}
  ],
  "tasks": [
    {"phase": "Discovery", "objective": "...", "function": "Solution Architect", "rateBand": "Principal", "solutionArea": "Setup and Design", "days": 15}
  ],
  "paymentMilestones": [...]
}
```

### Time & Materials
```json
{
  "model": "t&m",
  "budgetCap": 150000,
  "budgetCapInclGST": false,
  "invoiceFrequency": "monthly",
  "phases": [
    {"name": "Discovery", "startDate": "2026-03-02", "endDate": "2026-03-27"}
  ],
  "tasks": [
    {"phase": "Discovery", "objective": "...", "function": "Solution Architect", "rateBand": "Principal", "solutionArea": "Setup and Design", "days": 10}
  ]
}
```
Key differences from phase model:
- `budgetCap`: indicative budget (ex or inc GST)
- `budgetCapInclGST`: whether cap includes GST
- `invoiceFrequency`: typically "monthly"
- No `paymentMilestones` (invoiced on actuals)
- No `flatContingency` (always 0%)

### Managed Services
```json
{
  "model": "managed_services",
  "startDate": "2026-07-01",
  "contractMonths": 24,
  "annualUplift": 0.03,
  "monthlyAllocations": [
    {"function": "Power Platform Developer", "rateBand": "Senior", "daysPerMonth": 4},
    {"function": "Solution Architect", "rateBand": "Principal", "daysPerMonth": 1},
    {"function": "Support Analyst", "rateBand": "Junior", "daysPerMonth": 3}
  ]
}
```
Key differences:
- No phases, sprints, or tasks
- `monthlyAllocations` instead of tasks
- `contractMonths` and `annualUplift` for multi-year projection

## Output Sheets by Model

| Sheet              | Sprint | Phase | T&M | Managed Svc |
|--------------------|--------|-------|-----|-------------|
| Config             | ✓      | ✓     | ✓   | ✓           |
| Estimate           | ✓      | ✓     | ✓   | —           |
| Monthly Allocation | —      | —     | —   | ✓           |
| Resource Summary   | ✓      | ✓     | ✓   | —           |
| Weekly View        | ✓      | ✓     | ✓   | ✓           |
| Forecast Export    | ✓      | ✓     | ✓   | ✓           |
| Payment Milestones | ✓      | ✓     | —   | —           |

## Forecast Export Format (Universal)

All models output the same forecast format for aggregation:

| Column           | Description                    |
|------------------|--------------------------------|
| Project          | Project name                   |
| Client           | Client name                    |
| Version          | Estimate version               |
| Model            | Sprint/Phase/T&M/Managed Svc   |
| Function         | Role function                  |
| Rate Band        | Principal/Senior/Associate/Junior |
| Week Commencing  | ISO date (YYYY-MM-DD)          |
| Estimated Days   | Days allocated that week       |
| Daily Rate       | Rate for that role             |
| Estimated Cost   | Days × Rate                    |

## Branding

- Navy header rows: #19263C with white text
- Teal accent for totals: #6BE1B8
- Conditional formatting (weekly view): Green < 2.5d, Amber 2.5-4d, Red > 4d
- Font: Arial 10pt body, Arial 11pt Bold headers, Arial 14pt Bold title
- Currency: $#,##0 | Percentage: 0% | Decimal: 0.0

## Formula Audit

The workbook is formula-driven. Inputs (editable values) drive everything
downstream via formulas. Edit a Daily Rate, Days, Contingency %, GST or
Discount and totals recalculate on open.

### Config
- **Inputs:** Project metadata, GST %, Discount %, Rate Card Daily Rates,
  Contingency % per Solution Area
- **Derived:** Hourly Rate = `=B<row>/8`

### Estimate
- **Inputs:** Phase/Sprint/Objective text, Function, Rate Band, Solution Area,
  Days (or Allocation for sprint model)
- **Derived:**
  - `Daily Rate` = `VLOOKUP(<RateBand>, Config rate card, 2, FALSE)`
  - `Estimate` = `<Days> * <Daily Rate>`
  - `Contingency %` = `IFERROR(VLOOKUP(<SolutionArea>, Config contingency table, 2, FALSE), 0.15)`
    (or flat value when `flatContingency` is set in config)
  - `Estimate Inc. Contingency` = `<Estimate> * (1 + <Contingency %>)`
  - TOTAL row: `SUM` of each column
  - Discount row: `-<Estimate TOTAL> * <Config Discount>`
  - Subtotal After Discount: `<TOTAL> + <Discount>` (Discount is negative)
  - GST row: `<basis> * <Config GST>`
  - Total Inc. GST row: `<basis> * (1 + <Config GST>)`

### Monthly Allocation (managed services)
- **Inputs:** Function, Rate Band, Days / Month, Annual Uplift (in Config)
- **Derived:**
  - Daily Rate = `VLOOKUP` into rate card
  - Per-month cell = `<Days/Month> * <Daily Rate> * <upliftFactor>`
  - Total Days = `<Days/Month> * <months>`
  - Total Cost = `SUM` of month range
  - GST / Total Inc. GST = formulas referencing Config GST
  - Annual Summary: `SUMPRODUCT` of Days/Month and Daily Rate ranges,
    multiplied by months in year

### Resource Summary
- **Inputs:** Function name, Rate Band (sort order is fixed at build time)
- **Derived:**
  - Daily Rate = `VLOOKUP`
  - Total Days = `SUMIFS(Estimate!Days, Estimate!Function, <fn>)`
  - Estimate = `SUMIFS(Estimate!Estimate, Estimate!Function, <fn>)`
  - Estimate Inc. Contingency = `SUMIFS(Estimate!EstCont, Estimate!Function, <fn>)`
  - % of Total = `<this row Est Inc Cont> / <Estimate TOTAL Inc Cont>`
  - TOTAL row: `SUM`
  - Summary by Solution Area: same pattern with `SUMIFS` on Solution Area column

### Weekly View
- **Inputs (effectively):** per-week, per-function allocation values are
  derived from working-day math against phase / sprint date ranges and are
  written as values, not formulas. Treat them as inputs if you want to override
  a specific week.
- **Hidden row 3:** per-function Daily Rate via `VLOOKUP` into Config rate card
  (hidden so it does not clutter the view, but lives in the file so
  `SUMPRODUCT` can reference it).
- **Derived:**
  - Row Total Days = `SUM(<C..lastFnCol><row>)`
  - Row Total Cost = `SUMPRODUCT(<C..lastFnCol><row>, <C..lastFnCol>$3)`
  - Column totals = `SUM` of week range
  - Grand Total Days and Total Cost = `SUM`

### Forecast Export
- **Inputs:** Project, Client, Version, Model (header metadata), Function,
  Rate Band, Week Commencing, Estimated Days (rounded value)
- **Derived:**
  - Daily Rate = `VLOOKUP(<RateBand>, Config rate card, 2, FALSE)`
  - Estimated Cost = `<Estimated Days> * <Daily Rate>`

### Payment Milestones
- **Inputs:** #, Milestone name, % of Total, Due Date, Acceptance Criteria
- **Derived:**
  - Amount Ex GST = `<Estimate fee basis cell> * <% of Total>`
    (fee basis = Estimate sheet's Inc Contingency total, or post-discount
    subtotal if discount > 0)
  - Amount Inc GST = `<Ex GST cell> * (1 + <Config GST>)`
  - TOTAL row: `SUM` of the column
