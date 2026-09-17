---
name: word-doc
description: >
  Generate a branded Word document (.docx) using a client or company template as the
  style donor. Inherits fonts, heading colors, table styles, and page setup from a
  donor .docx so output matches the client's brand. Use whenever the user asks to
  create a Word document, generate a .docx, export to Word, or produce a client-ready
  document.
---

# Branded Word Document Generator

Generate a Word document (.docx) using a brand template as the style donor (fonts, heading colors, table styles).

## When to Use

When the user asks to create a Word document, generate a .docx, export to Word, or produce a client-ready document.

## Template Source

Use any recent branded `.docx` file in the project as the style-donor template. Loading it preserves the client's brand (fonts, heading colors, table styles, page setup).

Ask the user for the template path if not obvious from the project. Common patterns:
- Client-supplied template kept in the project root
- A previous deliverable like a user guide or design doc

## Template Specifications

The skill inherits whatever the donor template defines. Typical attributes to preserve:

### Fonts
- **Headings**: brand font, bold, brand primary color
  - H1: 18pt
  - H2: 14pt
  - H3: 12pt
  - H4: 10pt
- **Body**: brand font, 10pt, black
- **Table header**: brand font, 9pt, white text on brand-primary background
- **Table body**: brand font, 9pt

### Page Setup
- A4 (11906 x 16838 twips) — or Letter, match the template
- Margins: 2cm all sides (1134 twips)
- No headers/footers in the template by default (add if needed)

### Common Styles
- `Heading1` through `Heading9`
- `Normal` (body text)
- `List Paragraph` (indented bullets)
- `Table Grid` (standard table)
- Plus any client-custom table styles defined in the donor

### Table Pattern
- Header row: brand-primary background, white bold text
- Data rows: default styling, 9pt brand font
- Use `Table Grid` style as base, then apply brand shading to header cells via XML

### Document Structure
1. Cover page (title, subtitle, version, centered)
2. Page break
3. Content sections with H1/H2/H3 hierarchy
4. Tables for structured data
5. Bullet lists for enumerations
6. Page breaks between major sections

## Implementation Pattern

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

# CONFIG — adjust per project
TEMPLATE = r"path/to/Brand Template.docx"
BRAND_PRIMARY = RGBColor(0x1D, 0x2F, 0x4E)  # e.g., navy
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BRAND_FONT = "Figtree"  # or whatever the template uses

# Load template to inherit styles, then clear content
doc = Document(TEMPLATE)
for p in doc.paragraphs:
    p._element.getparent().remove(p._element)
for t in doc.tables:
    t._element.getparent().remove(t._element)

# Add heading with correct font
def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = BRAND_PRIMARY
        run.font.name = BRAND_FONT
    return h

# Add body paragraph
def add_para(text, bold=False):
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.name = BRAND_FONT
        run.font.size = Pt(10)
        if bold:
            run.bold = True
    return p

# Add bullet point
def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style="List Paragraph")
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        run.font.name = BRAND_FONT
        run.font.size = Pt(10)
    run = p.add_run(text if not bold_prefix else text)
    run.font.name = BRAND_FONT
    run.font.size = Pt(10)
    return p

# Add table with brand-primary header
def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.name = BRAND_FONT
        run.font.size = Pt(9)
        run.font.color.rgb = WHITE
        fill = "{:02X}{:02X}{:02X}".format(BRAND_PRIMARY[0], BRAND_PRIMARY[1], BRAND_PRIMARY[2])
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill}"/>')
        cell._element.get_or_add_tcPr().append(shading)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.name = BRAND_FONT
            run.font.size = Pt(9)
    return table
```

## Dependencies

- `python-docx` (`pip install python-docx`)
- A donor template `.docx` must exist somewhere accessible to the script

## Naming Convention

Output files: `{Client} {Topic} - {Subtitle}.docx`
(e.g., `{Client} MSM - Scope vs Delivered Analysis.docx`)

## Tips

- Always load the template first and clear content — this preserves the client's defined styles, margins, and headers/footers
- When in doubt about a brand color, sample it from an existing client logo or doc
- For long documents, paginate with `doc.add_page_break()` between major sections
