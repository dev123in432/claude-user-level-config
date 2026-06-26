---
name: md-to-docx
description: Convert Markdown into a branded Microsoft Word .docx using a reference/template .docx. Applies the template's styles, brands tables, strips heading auto-numbering, sets page margins, and builds and fills a cover page. Use when turning Markdown documents or deliverables into formatted Word files, producing a Word version of a markdown report, applying a corporate Word template to markdown, or regenerating Word docs each time the markdown changes.
---

# md-to-docx

Turn Markdown into a polished, on-brand Word `.docx` deterministically, so you can
re-export every time the source changes instead of pasting and re-styling by hand.

The engine is **Pandoc** (`--reference-doc`) plus small, surgical `.docx` post-edits for
the things Pandoc alone gets wrong (table styling, heading numbering, margins, cover page).

## Requirements

- `pandoc` on PATH (`pandoc --version`).
- `pip install python-docx docxcompose`

## Usage

```
python ~/.claude/skills/md-to-docx/md2docx.py FILES... -r REFERENCE.docx [options]
```

Options:

| Flag | Effect |
|------|--------|
| `-r, --reference` | Reference `.docx`: source of styles, margins, headers/footers, and the cover page design. **Required.** |
| `-o, --outdir` | Output directory (default: current dir). One `.docx` per input, same basename. |
| `--table-style ID` | Repoint Pandoc's generic `Table` style to a branded table style (e.g. `ListTable4-Accent1`). The style must already exist in the reference. |
| `--no-heading-numbers` | Strip auto-numbering from Heading 1-9 (keeps outline levels, so the nav pane/TOC still work). Use when your Markdown headings already carry manual numbers. |
| `--margins TWIPS` | Set page margins. `720` = 0.5in (Word "Narrow"). |
| `--cover` | Prepend a cover page built from the reference's first page. |
| `--title / --subtitle / --author / --date` | Fill the cover placeholders. `--title` defaults to each file's first `# ` heading. |
| `--placeholders` | The cover placeholder texts to match, in order `title,subtitle,author,date` (default `Document Title,Document Subtitle,Author Name,Date`). |

### Worked example (the AccelerateTech template)

```
python ~/.claude/skills/md-to-docx/md2docx.py 0*.md \
  -r "AccelerateTech  Basic Word Template - Cover.docx" \
  --table-style ListTable4-Accent1 \
  --no-heading-numbers --margins 720 \
  --cover --subtitle "Milestone 1" --author "Accelerate" --date "June 2026" \
  -o out
```

Each file's cover Title comes from its `# H1`; Subtitle/Author/Date are shared.

## The one trick you must know: table column widths

Pandoc sets Word column widths from the **relative number of dashes** in each Markdown
table separator cell. Even dashes = equal columns (a wide text column gets starved). To
fix it, weight the separator dashes (alignment colons are preserved):

```
| Element | What it is                                | Demand | Disposition |
|---------|-------------------------------------------|--------|-------------|
```

This lives in the Markdown source, so the layout travels with the document and the script
stays generic. Numeric columns: keep them short; text columns: give them lots of dashes.

**Threshold gotcha:** Pandoc only honours these relative widths when the whole separator row
is longer than its `--columns` width (default 72 characters). A small table whose separator is
under ~72 chars comes out with equal columns regardless of your dash ratios. Fix: pad the
dashes so the entire separator row exceeds ~72 characters (keeping the same ratios).

## Gotchas and why the post-edits exist

- **Reference doc carries styles, margins, headers/footers, and page setup, but NOT its body
  content.** So `--cover` rebuilds the cover by copying the reference and stripping its body
  paragraphs/tables, keeping the cover's drawings/content-controls and section. Then it fills
  the placeholder text inside the cover text boxes (matching whole-paragraph text, so it works
  even when a placeholder is split across runs, as Word often does with "Document Subtitle").
- **Heading double-numbering:** if the template's Heading styles auto-number AND your Markdown
  headings have manual numbers (e.g. `## 7. ...`), Word shows "1.7  7. ...". `--no-heading-numbers`
  removes the auto layer and keeps your manual numbers. It strips numbering from the styles but
  leaves outline levels, so headings still appear in the navigation pane and any TOC.
- **Tables come out unbranded** because Pandoc tags every table with a style literally named
  `Table`. `--table-style` repoints them to the template's real table style. Find its id with:
  `unzip -p REFERENCE.docx word/styles.xml | grep -o 'w:styleId="[^"]*"'`.
- **Close the .docx in Word before re-running** or the file is locked and the write fails.

## How it works (per file)

1. `pandoc FILE -o body.docx --reference-doc=<prepared reference>` (reference has heading
   numbering stripped and margins set, if requested).
2. Repoint `<w:tblStyle w:val="Table">` to the branded table style.
3. If `--cover`: copy the cover (reference with body stripped), fill Title/Subtitle/Author/Date,
   and prepend it to the body with `docxcompose` (with a page break between).
