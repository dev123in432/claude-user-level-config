---
name: accelerate-slides
description: Generate Accelerate Tech branded PowerPoint slide decks using the official 2026 dark template. Use this skill whenever the user asks to create a deck, slides, presentation, pitch deck, client deck, internal deck, or .pptx for Accelerate Tech. Also trigger on phrases like "build me slides for [client]", "knock up a deck", "put together a presentation", "Accelerate deck", "branded slides", or any request that references the 2026 dark template, the Figtree-branded deck, or the Accelerate Tech colour palette. Always use this skill for any Accelerate Tech presentation work — including quick informal requests like "spin up a deck on Power Platform governance" — to ensure brand, font, and colour consistency.
---

# Accelerate Tech Slides

Generate on-brand Accelerate Tech presentations using the official **Accelerate Tech PPT template - 2026 Dark** template (`assets/template.pptx`).

The template handles fonts and colours for you: Figtree is set as the default font in the theme and embedded in the file with all four weights, so slides render correctly even on machines without Figtree installed. **Don't override the font in slide XML — let it inherit from the theme.**

This skill builds on the public `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`. Use that skill's scripts (`unpack.py`, `add_slide.py`, `clean.py`, `pack.py`, `thumbnail.py`, `extract-text`) for the underlying mechanics.

## Workflow

### Step 1: Gather the brief

Before generating, confirm:

| Field | Notes |
|-------|-------|
| Audience | Client name (if external), or internal team |
| Purpose | Pitch, project kickoff, status update, training, all-hands, etc. |
| Slide count target | If unspecified, default to 8–12 slides for a pitch, 5–8 for an update |
| Key sections | Cover, agenda, content sections, Q&A/close |

If the user gives a topic only ("make me a deck on our managed services offering"), proceed with sensible defaults — don't over-question.

### Step 2: Stage the template

```bash
cp <SKILL_DIR>/assets/template.pptx /home/claude/template.pptx
python /mnt/skills/public/pptx/scripts/office/unpack.py /home/claude/template.pptx /home/claude/unpacked/
python /mnt/skills/public/pptx/scripts/thumbnail.py /home/claude/template.pptx
extract-text /home/claude/template.pptx
```

Replace `<SKILL_DIR>` with the path to this skill's directory.

The template ships with **22 slide layouts** and **34 example slides** demonstrating each layout in use. Duplicate and edit example slides rather than building from layout placeholders alone — the example slides have the correct typography and spacing pre-baked.

**Use existing layouts as your starting point. Adjust them within the rules below.** The template's layouts and example slides are starting points, not fixed forms — but the leeway is bounded. Doing any of the things listed below is preferred over composing the same slide from scratch on a fully blank layout.

What you may do:

- **Adjust the height of the body placeholder.** It may be made taller or shorter than the layout default, to free space for a grid, callout strip, or stat below it. The body's top edge must not move closer to the title placeholder — only the bottom edge moves.
- **Overlay text boxes and rectangles on a layout that only has a title** (e.g. Title only - Navy, Title only - Dark). These layouts exist precisely so the area below the title can be composed for the page.
- **Duplicate an example slide and edit its text** — for covers, section dividers, Q&A, and Thank-you, this is the right path.

What you may not do:

- **Touch the title (header) placeholder.** It is uniform across all slides — same position, same size, same typography. Do not resize it, move it, restyle it, or replace it with your own textbox. If you find yourself wanting a "smaller title" or "title slightly to the left," stop — the title is fixed.
- **Move the body placeholder's top edge upward** (toward the title). The vertical gap between title and body is part of the template's design language; preserve it.
- **Replace examples that already exist.** The cover (slides 1–3), section dividers (slides 15, 21, 25), Q&A (slide 33), and Thank-you (slide 34) have specific worked examples. Use them. Do not author parallel versions on a blank layout — there is no aesthetic or technical reason to, and it introduces unnecessary risk.

**Do not replace examples that already exist.** Some content beats already have a specific example slide and you should use it: the cover (slides 1–3), section dividers (slides 15, 21, 25), Q&A (slide 33), and Thank-you (slide 34). For these, duplicate the example, edit text, and ship. Do not author a parallel version on a blank layout — there is no aesthetic or technical reason to, and it introduces unnecessary risk.

**For body content, the title-bearing layouts (Title and Content, Title only - Navy, Title only - Dark) are usually the right base.** They keep the title placeholder typography and the layout's design language, and leave you the rest of the canvas to compose on. The multi-callout example slides (9, 10, 11, 12) are also valid starting points but are often less flexible — adjusting a Title and Content slide is frequently the lighter-touch path. Pick whichever base layout gives you the smallest gap between what's there and what you need.

**Order is not fixed.** The example slides are a library, not a script. Pick whichever fits each content beat and arrange them in whatever order serves the narrative.

**Truly blank layouts (Gradient Blank, Blank Navy) are for content shapes the title-bearing layouts genuinely can't carry.** This is the legitimate exception — a 5-column comparison when the largest grid would force unreadable text on a Title and Content slide; a hero stat the title-bearing layouts don't accommodate; a horizontal N-node flow diagram. Compose on the blanks when the title-bearing options have been considered and don't work.

Before composing on a fully blank layout, write a one-line justification in your plan: *"5-column comparison; Title and Content placeholder height won't fit five readable columns."* If the justification reduces to "I think a custom version would look better," stop — adjust an existing layout instead.

**When you do compose on a blank, the rules in the "Blank-canvas compatibility" section under Brand rules are mandatory.** PowerPoint Mac is stricter than python-pptx and LibreOffice about geometry validation; programmatic shape authoring (via raw XML or python-pptx APIs) does not get the same auto-validation that the PowerPoint UI provides. The May 2026 ODPP session shipped seven sequential corrupted decks because shapes that LibreOffice rendered correctly contained adjustment values that PowerPoint Mac rejected on open.

### Step 3: Choose layouts

**Match content shape, not topic.** Layout choice is driven by the *structure* of what you're putting on the slide — how many parallel items, how dense the prose, whether it's a statement vs a deep-dive. Topic doesn't drive the call.

**Quick map for common proposal shapes.** Default to these before consulting the longer table below:

| Source content shape | Template example slide |
|---|---|
| Cover with title + subtitle + attribution | slide 3 (Cover - no photo) or slide 1 (Cover with photo) |
| Section intro with 3 numbered constraints / pillars / phases | slide 9 |
| 4-callout grid (features, work streams, pros/cons) | slide 11 or slide 12 |
| 6-callout grid (capabilities, optimisations) | slide 10 |
| 8 items | Two slides of slide 11 (4 each), not one cramped slide |
| Pillar / section divider | slide 15, 21, or 25 |
| Q&A | slide 33 |
| Thank you | slide 34 |

If the content shape isn't in the table, consult the full layout list below before considering a blank canvas.

#### Content shape → layout

| Content shape | Layouts that fit |
|---|---|
| Single declarative statement / hero idea | layout10 (Title only — dark), layout11 (Title only — photo), layout13 (Agenda with photo) |
| 2 parallel items | layout7 (Diagonal), layout8 (Contrast columns), layout14 with 2-callout source |
| 3 parallel items | layout14 with 3-callout source, layout17 with 3 of 6 boxes filled |
| 4 parallel items | layout14 with 4-callout source |
| 5–6 parallel items | layout17 (6 callouts), full fill |
| 3–6 short bullets in a content placeholder | layout4 (Graphic element + content), layout14 with 3-bullet source |
| Long-form paragraph (4+ sentences) | layout12 (Title only graphic) or layout13 (Agenda with photo) |
| Multi-stage framework deep-dive (one slide per stage, multiple slides) | layout21 (Gradient blank) used **consistently across the whole section** so the slides feel continuous |
| Comparison / before-and-after | layout7 (Diagonal) or layout8 (Contrast columns) |
| Diagram-led visual | layout21 (Gradient blank) or layout22 (Blank navy) with manual placement |

**Match-callout-count rule.** If content has *n* parallel items, the source slide must have *n* callouts. Never force 4 items into a 2-callout layout — pick a different source. If no source fits, build from a blank layout.

#### Cover & section

| Layout file | Name | Background | When to use |
|---|---|---|---|
| `slideLayout1.xml` | Cover with photo | Navy | Title slide for client decks with a hero image; also the default Thank-you closer |
| `slideLayout2.xml` | Cover - no photo | Navy | Title slide for internal/text-only decks |
| `slideLayout3.xml` | Project cover | Navy | Project kickoff or named-engagement title |
| `slideLayout5.xml` | Section Divider | Black (`141E1E`) | Between major narrative phases of long decks |
| `slideLayout13.xml` | Agenda with photo | Navy | Agenda page near the start; also "moment" slides (success, pivotal pathway choices) where the photo gives the slide presence |

#### Title-only / transitional

| Layout | Name | Background | When to use |
|---|---|---|---|
| `slideLayout9.xml` | Title Only - Navy | Navy | Section transition, low-content emphasis |
| `slideLayout10.xml` | Title only - dark | Black (`141E1E`) | High-impact statement slide; opening "purpose" or manifesto slides |
| `slideLayout11.xml` | Title only - Photo | Black w/ photo | Quote, hero stat, or photo-led statement |
| `slideLayout12.xml` | Title Only - graphic | Black w/ graphic | Full-bleed graphic moment |
| `slideLayout20.xml` | Q&A | Gradient | Q&A slide near the end |

#### Content layouts (most slides)

| Layout | Name | Background | When to use |
|---|---|---|---|
| `slideLayout14.xml` | Title and Content | Navy | Default for body slides — bullets, paragraphs, mixed content |
| `slideLayout15.xml` | 1_Title and Content | Navy | Variant of 14; use to vary rhythm in long decks |
| `slideLayout16.xml` | Title and Content - Gradient | Gradient | Same as 14 but on the brand gradient |
| `slideLayout17.xml` | Content and 6 callout box | Navy | Six features/benefits/principles as boxes; also works as 3-of-6 sparse fill with a body intro paragraph |
| `slideLayout18.xml` | Content and 4 callout box | Navy | Four features/benefits/principles |
| `slideLayout4.xml` | Graphic element - content | Navy | Title + content with a brand graphic accent |
| `slideLayout7.xml` | Diagonal content slide | Navy | "Before / after" or "old / new" — note the layout has an embedded photo, strip when repurposing |
| `slideLayout8.xml` | Contrast columns | Accent2 (deep navy) | Two-column comparison |
| `slideLayout19.xml` | Meet the team | Gradient | Team intro |
| `slideLayout6.xml` | Demo link slide | Gradient | Live demo or external link callout |
| `slideLayout21.xml` | Gradient Blank | Gradient | Architecture deep-dive sections (use consistently across the whole section), hero stats, quotes |
| `slideLayout22.xml` | Blank - Navy | Navy | Blank canvas — only when no other layout fits |

### Step 4: Build the deck

Follow the public pptx skill's editing workflow (`/mnt/skills/public/pptx/editing.md`):

1. **Decide slide order** before touching XML. Write a numbered plan mapping each slide to a layout file. Sanity-check it against the rules in **Visual rhythm and pacing** and **Section structure** below.
2. **Duplicate example slides** (slides 1–34) using `add_slide.py` rather than starting from layout placeholders.
3. **Delete unused example slides** from `<p:sldIdLst>` in `presentation.xml`.
4. **Edit content** in each `slide{N}.xml`. For light edits, the Edit tool works. For programmatic edits across many shapes (typical for callout-grid slides), use `<SKILL_DIR>/scripts/apply_edits.py` — a JSON-driven editor that finds shapes by `<p:cNvPr id="N">`, replaces paragraph text while preserving formatting, and lets you force `sz="2000"` consistently across body runs (see the **Common pitfalls** section — this is the cleanest way to avoid the inconsistent-size problem). Run `python apply_edits.py --list-shapes <slide.xml>` first to discover shape ids and current text. When replacing text bodies, **preserve explicit `sz=` attributes** on body runs — don't strip them, or text will reflow at the master default (28pt) instead of the textbox-intended size.
5. **Run `clean.py`** to remove orphaned files.
6. **Pack with `--original`** so the embedded fonts and theme are preserved:

```bash
python /mnt/skills/public/pptx/scripts/clean.py /home/claude/unpacked/
python /mnt/skills/public/pptx/scripts/office/pack.py /home/claude/unpacked/ \
  /mnt/user-data/outputs/deck.pptx --original /home/claude/template.pptx
```

### Step 5: QA

Run the visual QA loop from the public pptx skill (convert to images via `soffice` + `pdftoppm`, inspect with subagent). Check the brand rules below.

LibreOffice renders PowerPoint inaccurately for some shapes — particularly text wrapping and shape positioning on layouts with embedded graphics. Visual QA is for catching obvious overflow and missing content; minor positioning quirks may be LibreOffice artefacts and should be flagged for the user to verify in PowerPoint, not silently "fixed".

**QA artefacts stay in the sandbox.** Never write QA renders (PNG, PDF, intermediate `.pptx` versions) to the user's workspace folder or any connected drive. All thumbnails and slide PNGs live in `/tmp` or the sandbox scratchpad. Only the final `.pptx` is delivered to the workspace. Files written to the user's folder by the sandbox can't easily be deleted by them later.

### Step 6: Deliver

Use `present_files` to share the .pptx. Keep the summary brief.

### Step 7: If the user reports the file is corrupted

Do not iterate by reflex. Bisect first.

1. Confirm the **template itself** opens cleanly for the user. If yes, the corruption is in the modifications, not the template.
2. Build three throwaway test files and ask the user which open and which fail:
   - `test-A`: a binary copy of the template, zero modifications.
   - `test-B`: opened with python-pptx, saved unchanged.
   - `test-C`: B plus one blank slide added with one textbox.
3. Each result narrows the cause. Continue bisecting from there — half the slides, then a quarter, then specific slide builders. Stop producing "fix" versions until the bisection has identified a single failing operation.

**Do not produce v2, v3, v4 by guesswork.** Sequential general transformations (round-trip through python-pptx, resave through LibreOffice, slide-numbering tweaks) waste the user's time and rarely fix the actual cause. The May 2026 ODPP session shipped seven sequential corrupted decks this way before bisection identified a `corner=0` ROUNDED_RECTANGLE as the trigger.

---

## Brand rules

### Blank-canvas compatibility (mandatory when composing on layout21/22)

If you are authoring shapes programmatically (raw OOXML, python-pptx, or any other library) — whether on a blank layout, a title-bearing layout, or as adjustments to an existing example — be aware that PowerPoint Mac is materially stricter about shape XML structure than python-pptx and LibreOffice are. PowerPoint's UI emits a complete shape definition when a user draws a shape: a `<p:style>` block with all four refs (lnRef, fillRef, effectRef, fontRef), a populated `<a:ln>` element, an `<a:effectLst/>` element, full `<a:bodyPr>` attributes, and a non-empty `<p:txBody>` with paragraph properties. Python-pptx in default usage emits a minimal skeleton that omits most of these. PowerPoint Mac may flag a file with structurally minimal shapes as corrupted on open, even though python-pptx round-trips and LibreOffice renders it.

The rules below are the specific patterns that have rejected files in this skill's history. Treat them as a starting checklist, not as an exhaustive list — if your file is being flagged and none of the items below match, the deeper cause is likely missing structural XML around the shapes themselves.

- **Avoid `MSO_SHAPE.ROUNDED_RECTANGLE` with `corner = 0` (or `<a:gd name="adj" fmla="val 0"/>`).** Both python-pptx and LibreOffice accept it; PowerPoint Mac may not, particularly when the surrounding shape XML is also minimal. For a thin accent line or hairline divider, use `MSO_SHAPE.RECTANGLE` instead — it avoids the question entirely.
- **Do not author rounded-rectangle `avLst` adjustments below `val 1000`.** PowerPoint Mac is strict about minimum values; below ~1000 it treats the geometry as malformed.
- **Do not strip placeholders from a layout you intend to use.** If a layout has placeholders (e.g. Section Divider has two BODY placeholders), either fill them or pick a different layout. Removing placeholders via `sp.getparent().remove(sp)` leaves the slide in a state PowerPoint Mac sometimes rejects.
- **Do not LibreOffice-resave a python-pptx output to "fix" it.** LibreOffice rewrites font names, image formats, and authors metadata in ways that don't fix the underlying issue and add noise.
- **Validate before delivery** — see the Pre-delivery checklist's grep check.

### Backgrounds: change them properly, never fake them with rectangles

If a slide needs a different background colour from the layout default — **change the actual background**. Do not place a full-slide-sized coloured rectangle behind the content as a fake background. This breaks layout placeholders, interferes with editing in PowerPoint, and produces stacking-order bugs.

**To set or override a slide's background**, add a `<p:bg>` element as the first child of `<p:cSld>` in `slide{N}.xml`, before `<p:spTree>`:

```xml
<p:cSld>
  <p:bg>
    <p:bgPr>
      <a:solidFill>
        <a:schemeClr val="bg2"/>   <!-- brand navy -->
      </a:solidFill>
      <a:effectLst/>
    </p:bgPr>
  </p:bg>
  <p:spTree>
    ...
  </p:spTree>
</p:cSld>
```

Brand gradient (used by layouts 16, 19, 20, 21):

```xml
<p:bg>
  <p:bgPr>
    <a:gradFill>
      <a:gsLst>
        <a:gs pos="5000"><a:schemeClr val="bg2"/></a:gs>
        <a:gs pos="100000"><a:schemeClr val="accent3"/></a:gs>
      </a:gsLst>
      <a:lin ang="2700000" scaled="0"/>
    </a:gradFill>
    <a:effectLst/>
  </p:bgPr>
</p:bg>
```

**Most slides should not have a per-slide background override** — let the layout's background show through. If you don't add a `<p:bg>`, the slide picks up the layout's background, which is what you want 95% of the time.

**Never** simulate a background by adding a `<p:sp>` shape sized to the full slide (12192000 × 6858000 EMU) at the bottom of `<p:spTree>`. If you find yourself doing this, stop and use `<p:bg>` instead.

### Theme colours

The Accelerate 2026 colour scheme:

| Theme slot | Hex | Name |
|---|---|---|
| `dk1` | `000000` | Black |
| `lt1` | `FFFFFF` | White |
| `dk2` | `1A2B46` | **Brand navy** (default slide background) |
| `lt2` | `E6E6E6` | Light grey |
| `accent1` | `1D69F3` | **Brand blue** |
| `accent2` | `243A5E` | Deep navy |
| `accent3` | `34858C` | Teal |
| `accent4` | `DAFDBA` | Pale green |
| `accent5` | `6BE1B8` | Mint |
| `accent6` | `ABF8FF` | Pale cyan |

**Use `<a:schemeClr val="accent1"/>` rather than hard-coded hex** wherever possible. Don't introduce off-palette colours — no reds, oranges, yellows, or purples unless the user explicitly asks for a palette extension.

### Slide dimensions

16:9 widescreen: 12192000 × 6858000 EMU (13.33" × 7.5"). Don't resize.

### Typography

**Always set explicit `sz=` on body runs.** Do not strip the size and rely on inheritance — the master `bodyStyle` defaults to 28pt at level 1, which is too large for the callout boxes the template uses. Stripping `sz=` will produce text bigger than the textbox is sized for. The original example slides clamp body text to 20pt explicitly for exactly this reason; preserve those overrides when editing.

| Element | Size | XML |
|---|---|---|
| Cover title | 54–60pt | `sz="5400"`–`sz="6000"` |
| Slide title (manually positioned shape) | 44pt | `sz="4400"` |
| Slide title in a layout-managed placeholder | inherit | (omit `sz=` — layout owns the title style) |
| ALL CAPS section opener title (layout21) | 44pt | `sz="4400"` |
| Q&A hero title | 48pt | `sz="4800"` |
| Inline section heading within body | 24pt | `sz="2400"` |
| Body text (default) | 20pt | `sz="2000"` |
| Body text (dense paragraphs, 3+ sentences) | 16pt | `sz="1600"` |
| Body text (very dense or caption-style) | 14pt | `sz="1400"` |
| Sub-text / annotations | 11–12pt | `sz="1100"`–`sz="1200"` |
| Big stat callout | 60–96pt | `sz="6000"`–`sz="9600"` |

**Never go below 14pt on body text.** If content won't fit at 14pt, split across two slides instead.

**Title formatting:**

- Mixed case for normal slide titles ("What we Heard"), not Title Case.
- Title Case only where the title reads as a proper name ("Pathway 1: Proof of Concept").
- En-dash (`–`) for separators inside titles ("Meaning – Semantic layer"), not em-dash.
- ALL CAPS only when signalling "section opener" on layout21.

### No AI-slop visual tells

- **No accent lines under titles.** The template doesn't use them.
- **No full-width header or footer bars** beyond what the master provides.
- **No "Confidential" watermarks** unless the user asks.
- **No gradient text.** Brand gradient backgrounds are fine; gradient text is not.
- **No emoji as visual elements** unless the user asks.
- **No clip-art-style icons** — match the icon style already in the template.
- **No drop shadows on text.**

### Pictures

- Pictures are part of the **visual language** for layouts 1, 13, and 19 — keep them when using those layouts.
- Pictures on body-content layouts (the callout grids in slides 9–10 sources, the diagonal layout7) are **decorative and fight text** when content density is moderate-to-high. Strip them when repurposing those source slides for content-heavy slides.
- Don't repurpose source slides with heavy embedded graphics (e.g. the Blueprint/Build/Adopt grids in template slides 17–18). Build from a blank layout instead.
- If a layout has an image placeholder and the user hasn't provided one, supply a sensible placeholder image or switch to a layout without one. Never ship a deck with literal "click to add picture" prompt text.

---

## Visual rhythm and pacing

- **Don't put more than three consecutive slides on the same layout *and* the same visual rhythm** (e.g. three 4-callout grids in a row). Mix in title-only, contrast, gradient, or section-divider layouts to break up the cadence.
- When a multi-step framework appears (3+ stages or principles), expect to **revisit it across multiple slides from different angles** — what each stage does, who owns each, how each maps to delivery. Use different layouts when revisiting (horizontal grid vs vertical numbered list, or callout grid vs gradient deep-dive) so the audience doesn't feel they've seen the slide already.
- **Numbers in a sequence are graphic elements, not text inside headings.** Use separate ovals or circles holding the numerals (1, 2, 3, 4) rather than writing "1. Meaning" in the heading text. Numerals as graphics make sequence read at a glance.
- After a dense technical section (4+ deep-dive slides), the next slide should pull back to a single synthesis statement. Don't end a section on the last detail slide.

## Section structure

- Decks of **12+ slides need section dividers** (layout5) between narrative phases. The divider exists as a visual beat — its content can be minimal.
- Sections that go deep (4+ slides on one topic) get a three-part structure:
  1. **Section opener** — previews the structure. Typical pattern: ALL CAPS title on layout21 + short intro line + horizontal preview row of small labelled rectangles for the elements to come.
  2. **Deep-dive slides** — one per element, all on the same layout for visual cohesion.
  3. **Synthesis slide** — pulls the section back to a single statement before moving on.
- **Multi-slide deep-dives belong on layout21** (Gradient Blank) for visual unity. Don't scatter different layouts across a connected section.
- Most decks need a **closing pair**: Q&A (layout20) and Thank you (layout1). Include unless the user has explicitly told you the deck has a different ending.

## Copy density

Anchor copy length to the layout type. **If content doesn't fit the budget, split across two slides — never shrink text to compensate.**

| Layout type | Per-element budget |
|---|---|
| Callout box (any count) | Heading 1–3 words + description ≤12 words |
| 6-callout sparse fill (3–4 of 6 used) | Heading 1–3 words + description ≤15 words |
| Statement / body-paragraph slide | 4–6 short sentences (will fit at 16pt) |
| Architecture deep-dive on layout21 | 1 intro paragraph at 20pt + multi-level bulleted breakdown |
| Section opener (layout21 with preview row) | CAPS title + 1 short intro line + horizontal preview row of small labels |

---

## File paths

| Asset | Path |
|---|---|
| Working template | `<SKILL_DIR>/assets/template.pptx` |
| Helper editor (JSON-driven) | `<SKILL_DIR>/scripts/apply_edits.py` |
| pptx mechanics skill | `/mnt/skills/public/pptx/SKILL.md` |
| Editing guide | `/mnt/skills/public/pptx/editing.md` |
| Output location | `/mnt/user-data/outputs/<filename>.pptx` |

## Common pitfalls

These are the recurring mistakes from prior runs. Each one cost an iteration when missed; check them before shipping.

### 1. Title placeholders inherit the source slide's width, not the layout's

The example slides have title placeholders sized to the *example text*. If the source title was "HEADER" (slide 9), the placeholder is ~4.6 inches wide. A 4-word title like "Why this matters now" then wraps awkwardly to two lines. Slides duplicated from sources with longer example titles (slide 12: "HEADING HERE", slide 26: "Proven Experience") have wider placeholders (~11.5") that absorb longer titles fine.

**Fix:** Before shipping, compare your new title length to the source's example text length. If your title is materially longer, widen the title placeholder `<a:xfrm><a:ext cx="..."/></a:xfrm>` — the standard Title and Content layout uses `cx="11018520"` (≈11.5"). The `apply_edits.py` script supports `xfrm` overrides for this exact reason.

### 2. Body run `sz=` attributes are inconsistent across callout boxes within the same source slide

Slide 12's four callout boxes don't all have `sz="2000"` set explicitly — some inherit from the layout's body style. When a programmatic edit preserves the first-run `rPr` per paragraph, the inherited boxes render at a different size than the explicit ones (typically 18pt vs 20pt mixed across the four boxes).

**Fix:** When editing callout bodies via `apply_edits.py` (or any programmatic editor), force `sz="2000"` on every body run, regardless of what the source had. With `apply_edits.py`, set `"sz": 2000` on every paragraph change.

### 3. Source slides with embedded photos/logos pair captions to specific images

Template slide 26 (Proven Experience) has four logo images already in place (BECA, Toll, etc.) with captions ("First MSM in ANZ", "Delivered multi-country reporting", "Regulated scale" ×2) that match those specific logos. Overwriting the captions with different client names creates a logo/caption mismatch the user will need to fix in PowerPoint.

**Fix:** For slides with embedded image content (slide 26 specifically, but any slide where the source has real photos rather than placeholders), keep the original captions. Tell the user in the delivery summary that the logos paired with the original captions are placeholders they'll swap.

### 4. For/against ("where this fits") slides need 2 columns, not 4 mixed callouts

Trying to fit 2 IS-FOR and 2 NOT-FOR points into the standard 4-callout grid produces visual confusion — the four boxes in a row read as one undifferentiated group, even with varied headings. The audience can't tell at a glance which side of the argument each box is on.

**Fix:** When the content is binary (for/against, before/after, IS/IS-NOT), don't use a 4-callout grid even if the box count happens to fit. Use `slideLayout8` (Contrast columns) or take a 4-callout source slide, delete two boxes, and widen the remaining two so each spans half the slide. Each column gets a heading + 3–5 short bullets.

### 5. Use proper bullet formatting, never inline "• " characters

Prefixing list items with a literal "• " character renders as text — it breaks PowerPoint's bullets/numbering tools, loses the hanging indent (wrapped lines run back under the bullet), and can't be restyled at the master level if brand bullet style changes later.

**Fix:** Apply bullets via paragraph properties: `<a:pPr marL="..." indent="..."><a:buChar char="•"/></a:pPr>` (or `<a:buAutoNum type="arabicPeriod"/>` for numbered lists). The agenda example slide (template slide 4) is a good reference — it uses `<a:buAutoNum>` cleanly. Clone an existing bulleted paragraph from the template rather than constructing the bullet XML from scratch, so you inherit the designer's spacing/indent values.

## Pre-delivery checklist

1. No off-palette `<a:srgbClr>` colours introduced.
2. No full-slide rectangles in `<p:spTree>` masquerading as backgrounds.
3. **Every body text run has an explicit `sz=`** (default `sz="2000"`). No stripped-size body runs relying on inheritance.
4. **Layout matches content shape** (callout count = parallel item count; body-paragraph slides on statement layouts; deep-dives on layout21).
5. **Layout variety**: no more than three consecutive slides on the same layout *and* same visual rhythm.
6. If the deck has 12+ slides or a multi-stage section, **at least one section divider** (layout5) is present.
7. Multi-stage deep-dive sections sit on **layout21 consistently** — not scattered across different layouts.
8. **Closing pair** (Q&A layout20 + Thank you layout1) included unless explicitly excluded.
9. **Sequence numerals are graphic elements** (separate ovals/circles), not numbers prefixed inside heading text.
10. No leftover placeholder text in the rendered text (`lorem`, `ipsum`, `xxx`, `[insert`, "click to add picture", "Section name:", etc.).
11. Visual QA pass on the rendered images. LibreOffice quirks flagged for user verification, not silently "fixed".
12. Packed with `--original /home/claude/template.pptx` so the embedded Figtree fonts and theme survive.
13. Output opens cleanly: `python -c "from pptx import Presentation; Presentation('/path/to/output.pptx')"` should not raise. If it raises a content-type error mentioning `presentationml.template.main+xml`, the deck will be flagged as corrupt by PowerPoint and `[Content_Types].xml` needs the presentation content type set to `presentationml.presentation.main+xml`.
14. **PowerPoint Mac compatibility grep.** If any slides were composed on a blank canvas, run this check on the packed output:

    ```bash
    python -c "
    import zipfile, re
    p = '/path/to/output.pptx'
    bad = []
    with zipfile.ZipFile(p) as z:
        for name in z.namelist():
            if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                xml = z.read(name).decode('utf-8')
                if 'roundRect' in xml and re.search(r'name="adj"\s+fmla="val\s*0"', xml):
                    bad.append(name)
    if bad: print('CORRUPTION RISK:', bad)
    else:   print('OK')
    "
    ```

    If this prints `CORRUPTION RISK`, fix the offending slide (replace the offending `MSO_SHAPE.ROUNDED_RECTANGLE` with a plain `MSO_SHAPE.RECTANGLE`) before delivering. Do not ship a deck that has any corruption-risk shape, even if it opens in LibreOffice.
