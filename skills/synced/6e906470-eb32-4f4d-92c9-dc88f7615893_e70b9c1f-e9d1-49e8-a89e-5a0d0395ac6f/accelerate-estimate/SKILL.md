---
name: accelerate-estimate
description: Generate professional project estimation workbooks for Accelerate Tech engagements. Supports sprint-based, days-per-phase, time & materials, and managed services models. Use this skill whenever the user asks to create a project estimate, cost an engagement, build a resource plan, price a quote, or generate a budget. Also trigger when they mention rate cards, roles, contingency, estimation models, or provide an RFP/scope for costing.
---

# Accelerate Tech — Project Estimation Skill

## Purpose
Generate consistent, professional project estimation workbooks for Accelerate Tech engagements. Supports four models: sprint-based, days-per-phase, time & materials, and managed services. Outputs a branded Excel workbook with weekly resource view and forecast export for resource planning.

## Trigger Rules
Activate this skill when the user:
- Asks to create, build, or generate a project estimate
- Provides project scope, requirements, or RFP content for costing
- Asks to estimate effort, days, or cost for an engagement
- References "estimation", "costing", "pricing", "resource plan", "quote", or "budget"
- Provides an existing estimate to reformat or restructure
- Asks about Accelerate's rate card, roles, or standard contingency
- Asks to create a managed services pricing proposal
- Asks to estimate a T&M budget

Do NOT activate for:
- SOW generation (use accelerate-sow skill, feed estimate outputs into it)
- Invoice or billing queries
- Timesheet or actuals tracking

## Workflow — Guided Questionnaire

Claude follows this structured intake flow to build an estimate. If the user has already provided context (e.g. an RFP document, email, meeting notes), extract as much as possible first and pre-fill answers — only ask what's missing. Present choices clearly in conversation and let the user respond naturally.

The goal is to collect ALL required inputs before generating any config or workbook. Do not start building until the user has confirmed the estimate summary.

### Round 1: Project Basics

Collect these in ONE turn:

**Q1 (open-ended):** "What's the project name and client?"
- If already provided in context, confirm rather than re-ask

**Q2:** "What commercial model?"
- Options: Fixed Price, Time & Materials, Managed Services, or "Not sure — help me decide"
- If "Not sure", ask about project duration, budget flexibility, and delivery approach to recommend

**Q3:** "What's the primary solution area?"
- Options: Power Platform (Apps, Automate, Pages), Microsoft Fabric / Data & Analytics, Sustainability Manager, Copilot Studio / AI, Multi-solution
- This drives which functions to suggest

**Q4 (open-ended):** "What's the scope? Describe what's being built/delivered, or paste the RFP requirements."

### Round 2: Timeline & Scale

**Q5 (open-ended):** "When does the project start, and what's the target end date or duration?"
- If user gives a duration (e.g. "about 6 months"), calculate end date
- If user gives milestones only, derive timeline

**Q6 (fixed price only):** "Estimation model?"
- Options: Sprint-based (2-week sprints, detailed), Days-per-phase (simpler, phase-level)
- Auto-recommend sprint for > $100K or > 3 months; days-per-phase for smaller

**Q7 (T&M only):** "Is there a budget cap?"
- Options: Yes (I'll specify), No cap (pure T&M)
- If yes, follow up: "What's the cap (ex or inc GST)?"

**Q8 (managed services only):** "Contract duration?"
- Options: 12 months, 24 months, 36 months, Custom
- Follow up: "Annual uplift? (default 3% CPI)"

### Round 3: Roles & Effort

Based on the solution area from Q3 and scope from Q4, Claude proposes a team structure:

**Present a table** of suggested functions with default rate bands and ask the user to confirm or adjust. Example:

"Based on the scope, here's my suggested team:"
| Function | Rate Band | Needed? |
|----------|-----------|---------|
| Project Manager | Principal | ✓ |
| Solution Architect | Principal | ✓ |
| Power Platform Developer | Senior | ✓ |
| Integration Specialist | Senior | ? |
| Data Specialist | Senior | ? |
| Tester | Associate | ✓ |

**Q9:** "Which roles do you need? I've pre-selected based on scope."
- Present the table above and ask the user to confirm or adjust

**Q10:** "Complexity level? This affects allocation density."
- Options: Standard, Complex (heavy integrations, data migration, compliance), Simple (low integration, known patterns)

### Round 4: Phase & Allocation Design

**For sprint-based models:**
Claude proposes a sprint plan based on duration and complexity:
- Number of sprints per phase
- Sprint date ranges (auto-calculated from start date, skipping known holidays)
- Resource allocation per sprint per function (using benchmarks from role-catalogue.md)

Present this as a summary table and ask: "Does this look right? Anything to adjust?"

**For days-per-phase models:**
Claude proposes phases with total days per role:
- Phase names and date ranges
- Days per function per phase

**For managed services:**
Claude proposes monthly allocations per function based on the typical allocations table in role-catalogue.md.

### Round 5: Review & Confirm

Present a full summary BEFORE generating the workbook:

```
Project: {name} | Client: {client}
Model: {model} | FY: {fy}
Duration: {start} to {end} ({n} sprints / {n} phases / {n} months)

Team:
  Project Manager (Principal): {total_days}d — ${total}
  Solution Architect (Principal): {total_days}d — ${total}
  ...

Totals:
  Total Days: {n}
  Estimate (ex contingency): ${n}
  Contingency: ${n} ({method})
  Total ex GST: ${n}
  Total inc GST: ${n}
  {Budget cap: ${n} | Remaining: ${n}} (T&M only)
  {Monthly cost: ${n} | Annual: ${n}} (managed services only)
```

**Q_final:** "Generate the workbook?"
- Options: Yes generate it, Adjust allocations first, Change the timeline, Start over

If "Adjust", loop back to Round 4. If "Change timeline", loop back to Round 2.

### Step 6: Generate

Only after user confirms:

1. Build JSON config from collected inputs
2. Save config JSON to the current working directory as `estimate-config.json`
3. Run:
```bash
pip install openpyxl -q
python {skill_path}/scripts/build-estimate.py estimate-config.json "{ProjectName}_Estimate_{Version}.xlsx"
```
4. Verify totals match the confirmed summary
5. Present the output file path to the user

### Quick Mode

If the user provides comprehensive context upfront (e.g. a detailed RFP with timeline, scope, team, and budget), Claude can skip the questionnaire rounds and go straight to Round 5 (Review & Confirm) with a pre-built summary. Always present the summary for confirmation before generating.

## Model-Specific Notes

### Sprint-Based
- Allocation 0.4 = 4 days per 2-week sprint
- PM always present at minimum 0.2 across all phases
- Solution Architect front-loads in design
- Developers peak during build, testers lag by ~1 sprint

### Days-Per-Phase
- Simpler structure, total days per role per phase
- Good for small fixed-price or advisory engagements

### Time & Materials
- Contingency is always 0%
- Budget cap shown with remaining budget (red if overrun)
- No payment milestones — invoiced monthly on actuals
- Resource summary by function only (no solution area breakdown)

### Managed Services
- Monthly Allocation sheet replaces Estimate and Resource Summary
- Annual Summary shows year-over-year cost with uplift
- Weekly view shows steady-state allocation (flat line)
- Unused days do not roll over unless contractually agreed

## Model Selection Guide

When the user is unsure which model to use, walk through this decision tree:

```
Is this ongoing support (no defined end)?
  YES → managed_services
  NO ↓

Does the client want to pay on actuals (flexibility)?
  YES → t&m
  NO ↓ (fixed price)

Is the project > $100K or > 3 months?
  YES → sprint
  NO → phase
```

Additional signals:
- Government RFP with milestone payments → sprint (they expect detailed sprint plans)
- Advisory / assessment / workshop → phase
- "We just need X days of your time" → t&m
- "Monthly retainer for BAU support" → managed_services
- Client says "not to exceed" → t&m with budget cap

## Forecast Export (Universal)
All models produce the same Forecast Export format:
`Project | Client | Version | Model | Function | Rate Band | Week Commencing | Estimated Days | Daily Rate | Estimated Cost`

This enables aggregation across all active projects to see total demand by role by week, regardless of commercial model. Stack multiple forecast exports to identify hiring triggers.

## Integration with SOW Generator
1. Run this estimation skill first
2. Use Resource Summary totals for the SOW price table
3. Use phase breakdown for SOW deliverables
4. Use payment milestones for SOW payment schedule
