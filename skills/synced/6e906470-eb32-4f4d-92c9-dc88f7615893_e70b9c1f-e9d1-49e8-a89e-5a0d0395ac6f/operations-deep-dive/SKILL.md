---
name: operations-deep-dive
description: >
  Turn an Accelerate operations deep dive / war room into a branded workshop
  summary with a 30/60/90 day plan, clear KPIs, and accountability for the CEO,
  the operations owner, and the team. Produces a confidential Word version and a
  sanitised team Word version by default, and an on-brand readout deck on request.
  Use this skill whenever the user mentions an operations deep dive, ops war room,
  operations review, leadership offsite or planning session, a "deep dive with
  [name]", or asks to turn workshop/meeting notes or a transcript into a 30/60/90
  plan, an accountability plan, a quarterly operations plan, or a war room summary.
  Also trigger on "write up the deep dive", "summarise the ops workshop", "build
  the 30/60/90", or any request to produce KPIs and owners from a delivery/ops
  review. This is a quarterly ritual - reach for this skill even when the user
  only says "do the ops review writeup" without naming the format.
---

# Operations deep dive

Turn the notes from an operations war room into the deliverables that make it
stick: a workshop summary, a 30/60/90 day plan, a KPI scorecard, and clear
accountability. Run quarterly.

The job has two halves. The **content** changes every quarter and is yours to get
right (read the room's notes, structure them well, write clean prose). The
**rendering** is stable and handled by bundled scripts that build branded Word
and PowerPoint from a single content JSON file. Don't rebuild the rendering by
hand - fill the content, run the scripts.

## Before you start

Read `references/structure-and-kpis.md`. It defines the canonical document
structure, the 30/60/90 framing, the accountability layers, the standard
Accelerate operations KPI catalogue, and the confidentiality model. Keeping the
shape consistent quarter to quarter is the point - it makes the documents
comparable over time.

## Step 1 - Read the source

The input is usually raw workshop notes (a file like `Meeting.md.txt`) or a
meeting transcript. Read it fully. Pull out: what's working, what's not (the
gaps), the decisions made, the KPIs raised, the actions, who owns what, and
anything sensitive (pay/role changes, moving a named person, the owner's own
load). Note the people and seats named so you can assign accountability and turn
empty seats into recruitment actions.

If a transcript, mine it the same way - the structure you're filling is identical.

## Step 2 - Ask the per-run questions

These shape the output and change each quarter. Ask them (batch them):

1. **Audience / confidentiality** - who sees this? This decides which Word
   versions to build. Default is both: a `confidential` version for the CEO and
   operations owner (full, with annex) and a `team` version for the direct
   reports and wider leadership (annex removed, sensitive items sanitised). If
   only one audience, build only that one.
2. **Plan start date** - when does the 30/60/90 clock start? A Monday reads best.
   The scripts compute the phase date ranges from this.
3. **Sensitive items** - confirm what goes only in the confidential annex and
   what can be sanitised to role level for the team version.
4. **Deck?** - the default is documents only. Build the readout deck only if they
   want one now (it's quick to add later).

Confirm the operations owner's real title and the CEO's name (check the org chart
if one is supplied - don't guess a title that lands in a document going to the
leadership team).

## Step 3 - Build the content file

Copy `assets/content.template.json` to a working file named
`assets/content.<quarter>.local.json` (the `.local.json` pattern is gitignored,
so a populated file never gets committed) and fill it from the source. The
template is a blank form - replace every `<placeholder>`. The `kpis` block is
pre-filled with the standard Accelerate catalogue; keep the rows the workshop
raised, drop the rest.

A populated content file holds names, pay/role changes and candid notes - treat
it like the confidential document itself. Never commit it; keep it local. If the
author has a real worked example on their machine (`assets/content.example.json`,
also gitignored), use it for reference, but rewrite every field from this
quarter's notes - last quarter's content with new dates is not a writeup.

Apply the **anti-ai-writing** skill to every piece of prose (context paragraph,
theme bodies, win/decision lines, accountability scopes). These documents go to
the leadership team; they must read like a person wrote them, not a model.
Australian English, no em dashes (hyphen with spaces), sentence-case headings.

Key fields:

- `config` - titles, dates, names, the operations owner's title, the org chart
  image path (optional appendix), `output_dir` and `file_stem` for naming.
- `audiences` - `["confidential", "team"]`, or a subset, from the audience answer.
- `wins`, `themes` (title + 2-4 sentence body), `decisions`, `kpis`,
  `accountability` (ceo / owner / team), `phases` (3 phases, each with actions
  carrying `owner` and `done_when`), `ideas`, `annex` (confidential only).
- Mark sensitive plan actions with `"confidential": true`. If there's a
  team-safe rephrasing, add `"team_action": "..."` and it replaces the wording in
  the team version instead of dropping the row (see the template's "embed" phase).

Every plan action needs one owner and one observable "done when". If you can't
say how you'd know it's done, the action is too vague - tighten it.

## Step 4 - Generate the documents

```bash
python scripts/build_docs.py <your-content.json>
```

This writes one `.docx` per audience into `config.output_dir`, named
`{file_stem} (Confidential).docx` and `{file_stem} (Team).docx`. It computes the
phase date ranges from `config.plan_start`, builds the KPI table and the three
plan tables, embeds the org chart if present, and adds the confidential annex to
the confidential version only.

## Step 5 - Build the deck (only if requested)

The deck is a readout companion - terse bullets, not the full prose. Fill the
optional `deck` block in the content file with curated short bullets (the example
shows the shape: `wins`, `themes`, `decisions`, `kpis`, `accountability` as
`{text, level}` items, `phases` with short `bullets`, `ideas`). Keep each bullet
to roughly one line. The deck is always team-safe - never put confidential
content in it.

```bash
python scripts/build_deck.py <your-content.json>
```

This drives the Accelerate 2026 dark template
(`../../1-sales-marketing/presentations/accelerate-slides/assets/template.pptx`)
directly with python-pptx, since there's no Linux pptx sandbox on this machine.
It duplicates the clean cover and section-divider example slides and uses the
'Title and Content' layout for body slides.

## Step 6 - QA before delivering

Render the output to images and actually look at it - this catches text overflow,
placeholder collisions, and contrast issues that structural checks miss:

```bash
python scripts/render_qa.py %TEMP%\odd_qa_<run> <file1.docx> <file2.docx> [deck.pptx]
```

Use a run-specific output folder (e.g. a timestamp suffix) so repeat runs don't
interleave. The script normalises paths, so absolute or relative both work, but
run it from a Windows shell (`%TEMP%` is a cmd/PowerShell variable). Then Read the
PNGs it lists. Check:

- The confidentiality split is real: the team `.docx` has no annex, no pay/role
  items, and the sanitised wording where actions were marked confidential.
- No text overflow or placeholder overlap on the deck (section dividers and the
  cover are the usual suspects).
- Brand and contrast look right (navy background, light text, Figtree).

Keep QA renders in `%TEMP%`, never in the user's OneDrive-synced workspace. If a
stray `WINWORD`/`POWERPNT` process blocks a render with a modal dialog, kill it
and retry.

## Step 7 - Deliver

Only the final `.docx` / `.pptx` files belong in the user's workspace folder.
Summarise what you produced, name the two Word versions and who each is for, and
flag anything you assumed (workshop date, the owner's title) for them to confirm.

## Dependencies

- `python-docx`, `python-pptx` (document/deck generation)
- `pywin32`, `pymupdf` and Microsoft Office (QA rendering only - install with
  `pip install pywin32 pymupdf` if missing)
- The Accelerate 2026 PPT template under the `accelerate-slides` skill (for decks)

## Brand

Navy `1A2B46`, blue `1D69F3`, deep navy `243A5E`, teal `34858C`, mint `6BE1B8`,
font Figtree. Sentence-case headings, Australian English, no em dashes.
