# Description standards

## The rule

Call `timeslot_description_standards()` **every run**, before the first write — no exceptions, never
cached, never a remembered summary. The rules can change and they govern text that lands on client
invoices. Use the returned text as the rulebook to validate every chargeable-project description before
showing it in the confirm table.

## What the live standards enforce (as of 2026-08-11 — the live call is authoritative)

- Present-tense verbs ("Analyse", "Develop", "Meet", "Review"); never "Worked on…", "Started…", "Continued…".
- Full first + last names for every person.
- No banned words: assist → liaise, fix → resolve, write → develop, talk/discuss → meet/review,
  bug → issue, admin → administration.
- British/Australian spelling (analyse, liaise, organisation). Sentence case, ends with a full stop.
- Don't include the client's company name (already on the invoice).
- Strict validation for chargeable types **T** (T&M), **F** (Fixed Price), **P** (Prepaid). Relaxed for
  **I** (Internal) and **N** (Never Bill) — clear and professional, but don't flag minor style issues.

## AT overlay (TODO — decide before release)

Olympic invited us to override/augment their standards with our own. Decide whether AT adds an overlay
(e.g. an ADO ticket reference requirement, a house description pattern). If yes, capture it here and apply
it **on top of** the live standards, never instead of them. Until decided, use the live standards as-is.

## Copying approved text

When replicating an already-approved entry (e.g. a fixed-price "…- See monthly summary." line), keep it
verbatim — it's the accepted per-job pattern. Don't re-run the style checker against it and "improve" it.
