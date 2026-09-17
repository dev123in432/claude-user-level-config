---
name: accelerate-goal-setting
description: >
  Runs the Accelerate Tech quarterly goal-setting interview and generates a
  branded FASSD goal submission document (.docx). Use this skill whenever a
  department head (or the CEO) wants to develop, test, or document a quarterly
  goal. Triggers on phrases like "set a quarterly goal", "I want to submit a
  goal", "help me write a Q goal", "FASSD goal", "quarterly planning",
  "goal for next quarter", "develop my Q goals", or any mention of submitting
  goals for a quarter. Always use this skill — do not attempt to run the FASSD
  interview from memory without it.
---

# Accelerate Tech — Quarterly Goal Setting Skill

This skill conducts a structured interview with the user, rigorously tests
their goal idea against the FASSD framework, and generates a branded Word
document goal submission form ready for CEO review.

---

## Workflow Overview

1. **Establish context** — department, head name, and quarter
2. **Capture the raw goal idea** — in the user's own words, unrefined
3. **FASSD deep-dive** — one criterion at a time, with probing follow-ups
4. **Scoring & readiness check** — surface any weaknesses, offer a revision pass
5. **Output** — run `scripts/generate_goal.js` and present the .docx

Do not skip or compress steps. The value of this skill is in the rigour of
the interview — rushed interviews produce weak goals that get returned at
review.

---

## Step 1 — Establish Context

Before anything else, collect:

- **Department name** (e.g. Growth & Sales, Delivery, Solutions, Local Government)
- **Department head's name and role**
- **Quarter** (e.g. Q2 FY26, Q3 2026)
- **Quarter date range** (e.g. 1 April – 30 June 2026)

If any of these are missing, ask before proceeding. Do not assume.

---

## Step 2 — Capture the Raw Goal Idea

Ask the user to describe their goal idea in their own words. Do not suggest
framing yet. Let them speak freely — the interview will sharpen it.

Ask:
> "Tell me about the goal you have in mind. Don't worry about wording it
> perfectly — just describe the outcome you're trying to achieve this quarter."

Listen for:
- Is it an **outcome** or an **activity**? (e.g. "run workshops" vs "convert prospects")
- Is there an implicit **metric** or is it vague?
- Does it **reference a specific deliverable** or is it directional?

Do not challenge the framing yet — just note what you're hearing. You will
surface this during the FASSD interview.

---

## Step 3 — FASSD Interview

Work through each criterion **one at a time**. Do not present all five at once.

For each criterion, follow this pattern:
1. Explain the criterion briefly (one sentence)
2. Ask the primary question
3. Listen for a complete answer — if the answer is thin or evasive, probe with a follow-up
4. Record the rating (Yes / Partial / No) and the justification note
5. Move to the next criterion

---

### F — Feasible: Can it be achieved with available resources?

**Primary question:**
> "Walk me through the resources this goal needs — budget, tools, people,
> and time. Are all of those in place right now, or are any of them things
> you'd need to secure?"

**Probe if the answer is vague:**
> "Is there anything in that list that isn't confirmed yet? If so, what's
> the plan to close that gap before the quarter starts?"

**Probe if they say everything is fine:**
> "What's the tightest constraint — the thing most likely to slow this down
> even if everything else is in place?"

Rate as:
- **Yes** — all resources confirmed or pre-committed
- **Partial** — one significant gap exists with a credible plan to close it
- **No** — material uncertainty with no clear plan

---

### A — Achievable: Is it within your capability and control?

**Primary question:**
> "Does your team have the skills and authority to execute this entirely?
> Or does it depend on other teams, external parties, or decisions above
> your level?"

**Probe if dependencies exist:**
> "Who else needs to do something for this goal to succeed — and how
> confident are you they will?"

**Probe if they claim full control:**
> "What's the single biggest risk to execution that sits outside your
> direct control?"

Rate as:
- **Yes** — team owns execution end-to-end
- **Partial** — meaningful dependency exists but is managed and tracked
- **No** — critical path runs through an external party with no committed agreement

---

### S1 — Suitable: Aligned with Accelerate's values and strategic direction?

**Primary question:**
> "How does this goal connect to Accelerate's 2026 priorities — Data & AI,
> Fabric, Microsoft solutions growth, or government and enterprise market
> expansion? Where does it fit?"

**Probe if the link is loose:**
> "If you had to explain to a client why we're investing in this rather
> than something else, what would you say?"

**Probe if the link seems strong:**
> "Are there any ways this goal could create tension or conflict with what
> other departments are trying to achieve this quarter?"

Rate as:
- **Yes** — clear, direct alignment to stated 2026 priorities
- **Partial** — indirect alignment or requires justification
- **No** — outside our current strategic focus with no compelling case

---

### S2 — Sustainable: Can it be maintained once achieved?

**Primary question:**
> "When the quarter ends and this goal is done — who owns it from that point,
> and what does maintaining it look like in practice?"

**Probe if they haven't thought about it:**
> "Is there a risk that the progress made this quarter gets lost because
> there's no plan to keep it going? What would prevent that?"

**Probe if they have a plan:**
> "Does that BAU plan require additional headcount, budget, or tooling that
> isn't currently committed?"

Rate as:
- **Yes** — named owner, clear BAU transition, no new resources needed
- **Partial** — plan exists but requires a resource not yet committed
- **No** — no plan for what happens after the quarter

---

### D — Specific: Is it clear, measurable, and unambiguous?

**Primary question:**
> "How will you and I both know, on the last day of the quarter, whether
> this goal was achieved or not? What's the specific number, deliverable,
> or milestone that signals done?"

**Probe if the answer is still vague:**
> "If I asked you to put a number on it — a count, a date, a revenue figure,
> a completion state — what would that be?"

**Probe if the metric seems arbitrary:**
> "How did you arrive at that target? Is it based on historical data,
> pipeline, capacity, or is it a stretch?"

Rate as:
- **Yes** — concrete, unambiguous success condition with a defined metric
- **Partial** — directionally clear but missing a specific number or milestone
- **No** — cannot be objectively assessed at quarter end

---

## Step 4 — Scoring & Readiness Check

After all five criteria, calculate the readiness score:
- Yes = 1.0 point
- Partial = 0.5 points
- No = 0 points
- **Total out of 5.0**

Present the score and the readiness label:

| Score | Label | What to tell the user |
|-------|-------|----------------------|
| 4.5 – 5.0 | Strong | Ready to generate the submission doc |
| 3.5 – 4.4 | Ready | One revision pass recommended before generating |
| 2.5 – 3.4 | Review | Flag the weak criteria — offer to rework before generating |
| < 2.5 | Weak | Do not generate. Work back through the weak criteria first |

**For any Partial score**, summarise the gap and ask:
> "You scored Partial on [criterion]. Do you want to strengthen that before
> we generate the document, or are you comfortable submitting with the note
> as-is?"

**For any No score**, do not generate the document. Explain the issue and
offer to rework that criterion before proceeding.

### Goal title refinement

Before generating, confirm the goal title. The title must be:
- A single outcome sentence (not an activity)
- Specific enough that a stranger could understand what success looks like
- Under 15 words

If the original idea was activity-framed, offer a reframed version:
> "Based on what you've told me, would you like me to suggest a tighter
> outcome-focused title before we generate the doc?"

---

## Step 5 — Generate the Document

Once the interview is complete and the score is Ready or above, run:

```bash
node skills/accelerate-goal-setting/scripts/generate_goal.js \
  --dept    "[Department Name]" \
  --head    "[Head Name]" \
  --role    "[Head Role]" \
  --quarter "[Quarter Label]"  \
  --dates   "[Date Range]" \
  --title   "[Goal Title]" \
  --desc    "[Goal Description]" \
  --f       "[yes|partial|no]" \
  --f-note  "[Feasible justification]" \
  --a       "[yes|partial|no]" \
  --a-note  "[Achievable justification]" \
  --s1      "[yes|partial|no]" \
  --s1-note "[Suitable justification]" \
  --s2      "[yes|partial|no]" \
  --s2-note "[Sustainable justification]" \
  --d       "[yes|partial|no]" \
  --d-note  "[Specific justification]" \
  --context "[Additional context / risks / dependencies]" \
  --score   "[X.X]" \
  --output  "/mnt/user-data/outputs/[dept-head-name]-Q[N]-goal.docx"
```

Replace all bracketed values with what was collected during the interview.
Do not fabricate or infer values that weren't explicitly stated — if
something is missing, ask before generating.

---

## Quality Rules

- Never skip a FASSD criterion
- Never accept a one-word answer — always probe for substance
- Never generate a document for a goal scoring below 3.5 without first
  offering a revision pass
- Never reframe the user's goal without their explicit agreement
- Partial scores must include a justification note — do not leave them blank
- The goal title must be an outcome, not an activity
- If the user seems to be rushing or gives thin answers, slow them down:
  > "This criterion matters — a weak answer here is likely to come back as
  > a revision request from the CEO. Let's make sure we've got this right."
