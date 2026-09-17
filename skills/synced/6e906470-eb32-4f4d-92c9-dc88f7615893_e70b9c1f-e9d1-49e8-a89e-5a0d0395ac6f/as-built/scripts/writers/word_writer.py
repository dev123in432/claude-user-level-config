"""
Populates the Accelerate As-Built Word template with Power Platform solution data.

Strategy:
  - Text replacement: scan every w:t element for [placeholder] tokens and replace in-place.
    This handles the cover-page SDT, headers/footers, and all body paragraphs.
  - Table population: find tables by locating the heading immediately above them, then
    replace the template data row(s) with real content.
  - Appendix injection: add new subsections after the Appendix heading for Power Platform
    components not covered by the base template (flows, tables, env vars, etc.).
"""

from __future__ import annotations

import copy
import re
import shutil
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree

from parsers.customizations import SolutionComponents
from parsers.solution import SolutionData

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ── Text replacement ──────────────────────────────────────────────────────────

def _replace_text_in_element(element, replacements: dict[str, str]) -> None:
    """Replace placeholder tokens inside all w:t descendants of *element*."""
    for t_el in element.iter(f"{{{W}}}t"):
        if t_el.text:
            for old, new in replacements.items():
                if old in t_el.text:
                    t_el.text = t_el.text.replace(old, new)
    # Field codes (e.g. COMMENTS "[Solution name]") carry the placeholder as a
    # fallback argument — replace there too, or an F9 field refresh in Word
    # reverts the cover page to the placeholder.
    for instr_el in element.iter(f"{{{W}}}instrText"):
        if instr_el.text:
            for old, new in replacements.items():
                if old in instr_el.text:
                    instr_el.text = instr_el.text.replace(old, new)


def replace_placeholders(doc: Document, replacements: dict[str, str]) -> None:
    """
    Replace tokens throughout the entire document including cover page SDT,
    headers, footers, and body.

    Because Word can split a phrase across multiple w:r runs, we first do a
    run-level pass (catches tokens in a single run) and then a paragraph-level
    pass that stitches runs together for split tokens.
    """
    # Pass 1: raw w:t replacement (covers SDT cover page, headers, footers)
    _replace_text_in_element(doc.element, replacements)

    # Pass 2: paragraph-level stitching for tokens split across runs
    all_paragraphs: list = []
    all_paragraphs.extend(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    for para in all_paragraphs:
        full_text = "".join(r.text for r in para.runs)
        needs_replace = any(old in full_text for old in replacements)
        if not needs_replace:
            continue
        new_text = full_text
        for old, new in replacements.items():
            new_text = new_text.replace(old, new)
        # Re-assign: put everything on first run, clear the rest
        if para.runs:
            para.runs[0].text = new_text
            for run in para.runs[1:]:
                run.text = ""


# ── Table helpers ─────────────────────────────────────────────────────────────

def _para_full_text(para_el) -> str:
    return "".join(t.text or "" for t in para_el.iter(f"{{{W}}}t")).strip()


def _get_body_children(doc: Document) -> list:
    return list(doc.element.body)


def _find_table_after_heading(doc: Document, heading_text: str):
    """
    Return the lxml element for the first table that follows a paragraph whose
    full text equals *heading_text*.  Returns None if not found.
    """
    children = _get_body_children(doc)
    found = False
    for child in children:
        tag = child.tag.split("}")[-1]
        if tag == "p":
            if _para_full_text(child) == heading_text:
                found = True
        elif tag == "tbl" and found:
            return child
        elif tag == "p" and found:
            # Another heading-level paragraph without hitting a table — stop
            pPr = child.find(f"{{{W}}}pPr")
            if pPr is not None:
                pStyle = pPr.find(f"{{{W}}}pStyle")
                if pStyle is not None:
                    style_val = pStyle.get(f"{{{W}}}val", "")
                    if style_val.startswith("Heading"):
                        break
    return None


def _set_cell_text(tc_el, text: str) -> None:
    """Clear a table cell and write plain text into it, preserving run formatting."""
    W_ns = f"{{{W}}}"
    for p_el in tc_el.findall(f"{W_ns}p"):
        for r_el in p_el.findall(f"{W_ns}r"):
            for t_el in r_el.findall(f"{W_ns}t"):
                t_el.text = text
                text = ""  # only write text in the first w:t; blank the rest
            # Remove extra w:t elements after the first
            t_els = r_el.findall(f"{W_ns}t")
            for extra in t_els[1:]:
                r_el.remove(extra)
        # Remove extra w:r elements after the first
        r_els = p_el.findall(f"{W_ns}r")
        for extra in r_els[1:]:
            p_el.remove(extra)


def _populate_table(
    doc: Document,
    heading_text: str,
    rows_data: list[list[str]],
    headers: list[str] | None = None,
) -> bool:
    """
    Find the table after *heading_text* and replace its data rows with *rows_data*.
    The header row (row 0) is preserved unless *headers* is given, in which case
    its cell texts are rewritten; the template data row is used as a style
    template for new rows.

    Returns True if the table was found and populated.
    """
    tbl_el = _find_table_after_heading(doc, heading_text)
    if tbl_el is None:
        return False

    W_ns = f"{{{W}}}"
    all_rows = tbl_el.findall(f"{W_ns}tr")
    if len(all_rows) < 2:
        return False

    header_row = all_rows[0]
    if headers:
        hdr_cells = header_row.findall(f".//{W_ns}tc")
        for i, h in enumerate(headers):
            if i < len(hdr_cells):
                _set_cell_text(hdr_cells[i], h)
    template_row = all_rows[-1]  # use last row as the style template

    # Remove all existing data rows
    for row in all_rows[1:]:
        tbl_el.remove(row)

    if not rows_data:
        # Re-add the template row with "(none)" in first cell
        blank = copy.deepcopy(template_row)
        cells = blank.findall(f".//{W_ns}tc")
        if cells:
            _set_cell_text(cells[0], "(none)")
            for c in cells[1:]:
                _set_cell_text(c, "")
        tbl_el.append(blank)
        return True

    for row_values in rows_data:
        new_row = copy.deepcopy(template_row)
        cells = new_row.findall(f".//{W_ns}tc")
        for i, val in enumerate(row_values):
            if i < len(cells):
                _set_cell_text(cells[i], str(val) if val is not None else "")
        tbl_el.append(new_row)

    return True


# ── Appendix content builders ─────────────────────────────────────────────────

def _make_heading(doc: Document, text: str, level: int = 2):
    """Create and return a new heading paragraph element (not yet appended)."""
    style = f"Heading{level}"
    para = doc.add_paragraph(style=style)
    para.text = text
    return para._p


def _make_para(doc: Document, text: str, style: str = "Normal"):
    para = doc.add_paragraph(style=style)
    para.text = text
    return para._p


def _make_table(doc: Document, headers: list[str], rows: list[list[str]]):
    """Create a table element with styled header row and data rows."""
    n_cols = len(headers)
    tbl = doc.add_table(rows=1, cols=n_cols)
    tbl.style = "Table Grid"
    # Header row
    hdr_row = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.text = h
        # Bold header
        for run in cell.paragraphs[0].runs:
            run.bold = True
    # Data rows
    for row_data in rows:
        row = tbl.add_row()
        for i, val in enumerate(row_data):
            if i < len(row.cells):
                row.cells[i].text = str(val) if val is not None else ""
    return tbl._tbl


def _append_to_body(doc: Document, *elements) -> None:
    """Append lxml elements directly before the final sectPr."""
    body = doc.element.body
    # sectPr is always last
    sect_pr = body.find(f"{{{W}}}sectPr")
    if sect_pr is not None:
        insert_idx = list(body).index(sect_pr)
        for el in elements:
            body.insert(insert_idx, el)
            insert_idx += 1
    else:
        for el in elements:
            body.append(el)


def _append_para(doc: Document, text: str, style: str = "Normal") -> None:
    p = _make_para(doc, text, style)
    _append_to_body(doc, p)


def _append_heading(doc: Document, text: str, level: int = 2) -> None:
    p = _make_heading(doc, text, level)
    _append_to_body(doc, p)


def _append_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    tbl = _make_table(doc, headers, rows)
    _append_to_body(doc, tbl)


def _heading_index(doc: Document, text: str, style_prefix: str = "Heading") -> int | None:
    """
    Return the body index of the first paragraph styled as a heading whose full
    text equals *text*. Style-checked so TOC entries never match.
    """
    body = doc.element.body
    for i, child in enumerate(body):
        if child.tag.split("}")[-1] != "p":
            continue
        pPr = child.find(f"{{{W}}}pPr")
        if pPr is None:
            continue
        pStyle = pPr.find(f"{{{W}}}pStyle")
        if pStyle is None or not pStyle.get(f"{{{W}}}val", "").startswith(style_prefix):
            continue
        if _para_full_text(child) == text:
            return i
    return None


def _insert_before_heading(doc: Document, heading_text: str, elements: list) -> bool:
    """Move *elements* (already in the body) to just before the named heading."""
    idx = _heading_index(doc, heading_text)
    if idx is None:
        return False
    body = doc.element.body
    ref = body[idx]
    for el in elements:
        ref.addprevious(el)
    return True


def _remove_heading_and_table(doc: Document, heading_text: str) -> int | None:
    """
    Remove the named heading paragraph and the first table that follows it.
    Returns the body index where the heading was, or None if not found.
    """
    idx = _heading_index(doc, heading_text)
    if idx is None:
        return None
    body = doc.element.body
    heading_el = body[idx]
    tbl_el = _find_table_after_heading(doc, heading_text)
    body.remove(heading_el)
    if tbl_el is not None:
        body.remove(tbl_el)
    return idx


def _apply_heading_layout(doc: Document) -> None:
    """
    Every top-level section starts on a new page, and subheadings keep with
    their following content so they are never stranded at the bottom of a page.
    """
    try:
        doc.styles["Heading 1"].paragraph_format.page_break_before = True
    except KeyError:
        pass
    for style_name in ("Heading 2", "Heading 3", "Heading 4"):
        try:
            fmt = doc.styles[style_name].paragraph_format
            fmt.keep_with_next = True
        except KeyError:
            pass


# ── Security Roles section ────────────────────────────────────────────────────

def _populate_security_configuration(doc: Document, powerpages=None) -> None:
    """
    Insert portal authentication settings after the 'Security Configuration'
    heading. Derived from the Power Pages Authentication/* site settings in the
    export; credential-like values are masked.
    """
    if powerpages is None:
        return
    auth = powerpages.auth_settings()
    if not auth:
        return

    idx = _heading_index(doc, "Security Configuration")
    if idx is None:
        return

    # Identify the identity provider(s) from OpenIdConnect/OpenAuth setting paths
    providers = sorted({
        name.split("/")[2]
        for name, _ in auth
        if name.startswith(("Authentication/OpenIdConnect/", "Authentication/OpenAuth/"))
        and len(name.split("/")) > 3
    })
    intro = "Portal authentication is configured through the following site settings"
    if providers:
        intro += f" (identity provider(s): {', '.join(providers)})"
    intro += ". Credential values are withheld; retrieve them from the source environment if required."

    elements = [
        _make_para(doc, intro),
        _make_table(
            doc,
            ["Setting", "Value"],
            [[name, value or "—"] for name, value in auth],
        ),
    ]
    body = doc.element.body
    ref = body[idx]
    for el in reversed(elements):
        ref.addnext(el)


def _populate_security_roles(doc: Document, components: SolutionComponents) -> None:
    """
    Insert a summary table of security roles and their descriptions after the
    'Security Roles' heading. The description (authored in the solution)
    outlines what the role grants — detailed per-table permission matrices are
    deliberately not generated.
    """
    if not components.security_roles:
        return

    idx = _heading_index(doc, "Security Roles")
    if idx is None:
        return

    elements = [
        _make_para(doc, "The solution includes the following security roles."),
        _make_table(
            doc,
            ["Security Role", "Description"],
            [[r.name, r.description or "—"] for r in components.security_roles],
        ),
    ]

    body = doc.element.body
    ref = body[idx]
    for el in reversed(elements):
        ref.addnext(el)


# ── Main-body component sections ──────────────────────────────────────────────

def _build_component_sections(
    doc: Document,
    components: SolutionComponents,
    extras: dict | None = None,
    powerpages=None,
    solution=None,
) -> list:
    """
    Build the component reference sections as main-body content (not appendix
    material): Classic Workflows, Integrations, Data Model, Power Pages Portal,
    and Configuration. Returns the built lxml elements in document order; the
    caller inserts them before the Security section.
    """
    extras = extras or {}
    elements: list = []

    def heading(text: str, level: int = 1) -> None:
        elements.append(_make_heading(doc, text, level))

    def para(text: str) -> None:
        elements.append(_make_para(doc, text))

    def table(headers: list[str], rows: list[list[str]]) -> None:
        elements.append(_make_table(doc, headers, rows))

    # ── Classic Workflows & Actions (closes out System Components) ───────
    classic_flows = [f for f in components.flows if f.category != "Cloud Flow"]
    if classic_flows:
        heading("Classic Workflows & Actions", level=2)
        table(
            ["Name", "Type", "Status"],
            [[f.display_name, f.category, "Active" if f.is_enabled else "Inactive"]
             for f in classic_flows],
        )

    # ── Integrations ──────────────────────────────────────────────────────
    integrations: list[dict] = extras.get("integrations", [])
    if integrations:
        heading("Integrations", level=2)
        para("The solution integrates with the following external systems and services.")
        table(
            ["Integration", "Purpose", "Direction", "Authentication"],
            [[i.get("name", ""), i.get("purpose", ""),
              i.get("direction", ""), i.get("auth", "")] for i in integrations],
        )

    # ── Canvas Apps detail ────────────────────────────────────────────────
    if components.canvas_apps:
        heading("Canvas Apps", level=1)
        for app in components.canvas_apps:
            heading(app.display_name, level=2)
            if app.description:
                para(app.description)
            table(["Property", "Value"], [
                ["Screens", ", ".join(app.screens) if app.screens else "—"],
                ["Connectors / Data Sources", ", ".join(app.connectors) if app.connectors else "—"],
            ])

    # ── Data Model ────────────────────────────────────────────────────────
    if components.tables:
        heading("Data Model", level=1)

        table_descriptions: dict[str, str] = extras.get("table_descriptions", {})
        column_descriptions: dict[str, str] = extras.get("column_descriptions", {})

        def table_desc(t) -> str:
            return table_descriptions.get(t.schema_name.lower()) or t.description or ""

        def column_desc(t, c) -> str:
            override = column_descriptions.get(
                f"{t.schema_name.lower()}.{c.schema_name.lower()}"
            )
            return override or c.description

        # Summary table — one row per table
        summary_rows = [
            [t.display_name, table_desc(t) or "—"]
            for t in components.tables
        ]
        table(["Table", "Description"], summary_rows)

        # Data model diagram — the important relationships, drawn rather than
        # tabulated. extras["diagram_tables"] curates which tables appear;
        # default: the publisher's custom tables (excluding BPF tracking
        # tables) plus core standard tables they relate to.
        prefix = ((solution.publisher_prefix if solution else "") or "").lower()
        if prefix and components.relationships:
            display_by_schema = {t.schema_name.lower(): t.display_name for t in components.tables}

            include = [t.lower() for t in extras.get("diagram_tables", [])]
            if not include:
                include = [
                    t.schema_name.lower() for t in components.tables
                    if t.schema_name.lower().startswith(f"{prefix}_")
                    and not any(c.schema_name.lower().startswith("bpf_") for c in t.columns)
                ] + ["account", "contact", "incident"]
            include_set = set(include)

            edge_pairs: dict[tuple[str, str], object] = {}
            try:
                from writers.diagram import DiagramEdge, render_er_diagram
            except ImportError:
                render_er_diagram = None
            if render_er_diagram is not None:
                for rel in components.relationships:
                    a, b = rel.first_entity, rel.second_entity
                    if a not in include_set or b not in include_set or a == b:
                        continue
                    key = tuple(sorted((a, b)))
                    # A 1:N relationship wins over N:N for the same pair
                    if key in edge_pairs and rel.rel_type == "Many-to-Many":
                        continue
                    edge_pairs[key] = DiagramEdge(
                        parent=a, child=b,
                        many_to_many=rel.rel_type == "Many-to-Many",
                    )

                if edge_pairs:
                    import tempfile
                    nodes = {n: display_by_schema.get(n, n) for n in include_set}
                    png_path = Path(tempfile.mkdtemp(prefix="at_erd_")) / "datamodel.png"
                    rendered = render_er_diagram(nodes, list(edge_pairs.values()), png_path)
                    if rendered:
                        heading("Data Model Diagram", level=2)
                        para(
                            "Key relationships between the solution's core "
                            "tables. 1 marks the parent side and N the child "
                            "side of each relationship."
                        )
                        pic_para = doc.add_paragraph()
                        pic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        pic_para.add_run().add_picture(str(rendered), width=Inches(6.4))
                        elements.append(pic_para._p)
                        try:
                            rendered.unlink()
                            rendered.parent.rmdir()
                        except OSError:
                            pass

        # Per-table detail: a brief description of the table above a columns
        # table listing display name, logical name, and purpose of each custom
        # column added. Choice columns list their available values.
        for tbl in components.tables:
            heading(f"{tbl.display_name} ({tbl.schema_name.lower()})", level=2)
            desc = table_desc(tbl)
            if desc:
                para(desc)
            if tbl.columns:
                col_rows = []
                for c in tbl.columns:
                    cdesc = column_desc(tbl, c)
                    if c.options:
                        cdesc = (cdesc + " " if cdesc else "") + \
                                "Values: " + ", ".join(c.options) + "."
                    col_rows.append([c.display_name, c.schema_name.lower(), cdesc])
                table(["Display Name", "Logical Name", "Description"], col_rows)
            else:
                para("No custom columns added to this table.")

    # ── Power Pages Portal ────────────────────────────────────────────────
    if powerpages is not None and powerpages.components:
        heading("Power Pages Portal", level=1)
        grouped = powerpages.by_type()

        para(
            "The structure- and security-relevant components of the portal are "
            "listed below. Default platform components and implementation "
            "detail (site settings, web files, templates, snippets, link sets) "
            "are not documented individually."
        )

        # Inactive or deleted components are excluded, as are default platform
        # component types that carry no solution-specific design (basic forms,
        # web link sets).
        detail_order = [
            ("Web Page", "Partial URL"),
            ("Web Role", ""),
            ("Table Permission", "Table | Scope | Rights"),
            ("Advanced Form", ""),
            ("List", ""),
            ("Cloud Flow", "Detail"),
            ("Server Logic", ""),
        ]
        for type_label, detail_header in detail_order:
            comps = [c for c in grouped.get(type_label, []) if c.is_active]
            if not comps:
                continue
            heading(f"{type_label} ({len(comps)})", level=2)
            has_detail = any(c.detail for c in comps)
            if has_detail and detail_header:
                table(["Name", detail_header], [[c.name, c.detail or "—"] for c in comps])
            else:
                table(["Name"], [[c.name] for c in comps])

    # ── Configuration ─────────────────────────────────────────────────────
    has_config = (components.env_variables or components.connection_references
                  or components.custom_apis or components.plugin_assemblies
                  or components.pcf_controls or components.web_resources)
    if has_config:
        heading("Configuration", level=1)

    if components.env_variables:
        heading("Environment Variables", level=2)
        table(
            ["Display Name", "Logical Name", "Type", "Default Value", "Description"],
            [[ev.display_name, ev.schema_name, ev.data_type or "—",
              ev.default_value or "—", ev.description or "—"]
             for ev in components.env_variables],
        )

    if components.connection_references:
        heading("Connection References", level=2)
        table(
            ["Display Name", "Logical Name", "Connector"],
            [[cr.display_name, cr.logical_name, cr.connector_name or cr.connector_id or "—"]
             for cr in components.connection_references],
        )

    if components.custom_apis:
        heading("Custom APIs", level=2)
        table(
            ["Display Name", "Logical Name", "Binding Type", "Description"],
            [[api.display_name, api.unique_name, api.binding_type or "—", api.description or "—"]
             for api in components.custom_apis],
        )

    if components.plugin_assemblies:
        heading("Plugin Assemblies", level=2)
        for pa in components.plugin_assemblies:
            heading(f"{pa.name} (v{pa.version})" if pa.version else pa.name, level=3)
            if pa.steps:
                table(
                    ["Step Name", "Message", "Entity", "Stage"],
                    [[s.name, s.message or "—", s.entity or "—", s.stage or "—"]
                     for s in pa.steps],
                )
            else:
                para("No registered steps documented.")

    if components.pcf_controls:
        heading("PCF / Custom Controls", level=2)
        table(
            ["Display Name", "Control Name", "Version"],
            [[ctrl.display_name or ctrl.name, ctrl.name, ctrl.version or "—"]
             for ctrl in components.pcf_controls],
        )

    if components.web_resources:
        heading("Web Resources", level=2)
        table(
            ["Display Name", "Logical Name", "Type"],
            [[wr.display_name, wr.name, wr.type_label]
             for wr in components.web_resources],
        )

    # ── Deployment & ALM ──────────────────────────────────────────────────
    heading("Deployment & ALM", level=1)

    heading("Environment Strategy", level=2)
    para(
        "[To be completed: describe the environment topology (Development, "
        "UAT, Production), how changes flow between them, and who owns each "
        "environment.]"
    )

    dependencies = (solution.dependencies if solution else []) or []
    if dependencies:
        heading("Prerequisite Solutions", level=2)
        para(
            "The following solutions must be present in the target environment "
            "before this solution can be imported."
        )
        dep_rows = []
        for dep in dependencies:
            m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", dep)
            dep_rows.append([m.group(1), m.group(2)] if m else [dep, "—"])
        table(["Solution", "Minimum Version"], dep_rows)

    heading("Deployment Steps", level=2)
    para(
        "[To be completed: solution import order, deployment settings file, "
        "and any manual steps required during deployment.]"
    )

    heading("Post-Deployment Configuration", level=2)
    para(
        "[To be completed: environment variable values to set per environment "
        "(see Configuration > Environment Variables), connection references to "
        "authorise, portal provisioning steps, and smoke tests.]"
    )

    return elements


# ── Main entry point ──────────────────────────────────────────────────────────

def _inject_after_heading(doc: Document, heading_text: str, paragraphs: list[str]) -> None:
    """Insert plain paragraphs immediately after the first paragraph matching *heading_text*."""
    body = doc.element.body
    children = list(body)
    for i, child in enumerate(children):
        if child.tag.split("}")[-1] == "p" and _para_full_text(child) == heading_text:
            # Insert after this element
            insert_at = i + 1
            ref = children[insert_at] if insert_at < len(children) else None
            for text in reversed(paragraphs):
                p = OxmlElement("w:p")
                r = OxmlElement("w:r")
                t = OxmlElement("w:t")
                t.text = text
                r.append(t)
                p.append(r)
                if ref is not None:
                    body.insert(list(body).index(ref), p)
                else:
                    body.append(p)
            return


def generate_document(
    template_path: Path,
    output_path: Path,
    solution: SolutionData,
    components: SolutionComponents,
    org_name: str = "",
    author_name: str = "",
    extras: dict | None = None,
    powerpages=None,
) -> Path:
    """
    Generate an As-Built Word document from *template_path* and write it to
    *output_path*.  Returns the output path.

    *extras* is the dict returned by interactive.run_interactive_session() and may
    contain: org_name, author_name, solution_overview, doc_purpose, flow_descriptions.
    """
    extras = extras or {}
    shutil.copy2(template_path, output_path)
    doc = Document(str(output_path))

    today = date.today().strftime("%d %B %Y")
    org = extras.get("org_name") or org_name or solution.publisher_name or "[Organisation name]"
    sol = solution.display_name or solution.unique_name or "[Solution name]"
    author = extras.get("author_name") or author_name or "Accelerate Technology"

    # ── Text replacements ─────────────────────────────────────────────────
    replacements = {
        "[Organisation name]": org,
        "[Company name]": org,
        "[Solution name]": sol,
        "Author Name": author,
        "Date": today,
    }
    replace_placeholders(doc, replacements)

    # Document metadata (also feeds Word property fields on refresh)
    doc.core_properties.title = f"{sol} As Built Document"
    doc.core_properties.comments = sol
    doc.core_properties.author = author

    # ── System Overview free-text ─────────────────────────────────────────
    overview_paras = []
    if extras.get("solution_overview"):
        overview_paras.append(extras["solution_overview"])
    if extras.get("doc_purpose"):
        overview_paras.append(f"Document purpose: {extras['doc_purpose']}")
    _inject_after_heading(doc, "System Overview", overview_paras)

    # ── Solution Details (inserted before 'Development Accounts') ─────────
    details_elements = [
        _make_heading(doc, "Solution Details", level=2),
        _make_table(doc, ["Property", "Value"], [
            ["Solution Name", sol],
            ["Unique Name", solution.unique_name],
            ["Version", solution.version],
            ["Publisher", solution.publisher_name],
            ["Publisher Prefix", solution.publisher_prefix],
            ["Type", "Managed" if solution.is_managed else "Unmanaged"],
        ]),
    ]
    if not _insert_before_heading(doc, "Development Accounts", details_elements):
        _append_to_body(doc, *details_elements)

    # ── System Components (Section 4) ─────────────────────────────────────
    # Client-facing convention: one Applications table (the deployed apps with
    # their purposes), and one Environment URLs table — the URL is the only
    # thing that differs between environments, so nothing else is repeated.
    app_purposes: dict[str, str] = extras.get("app_purposes", {})

    def application_rows() -> list[list[str]]:
        rows = []
        if powerpages is not None and powerpages.components:
            portal_name = extras.get("portal_name") or f"{sol} Portal"
            rows.append([
                portal_name,
                "Power Pages Site",
                app_purposes.get("portal", "Public-facing engagement portal."),
            ])
        for app in components.model_apps:
            rows.append([
                app.display_name,
                "Model-Driven App",
                app_purposes.get(app.unique_name, app.description or ""),
            ])
        for app in components.canvas_apps:
            rows.append([
                app.display_name,
                "Canvas App",
                app_purposes.get(app.unique_name, app.description or ""),
            ])
        return rows or [["(see solution for components)", "", ""]]

    app_rows = application_rows()

    # Remove the three per-environment sections and replace them with
    # Applications + Environment URLs at the same position.
    insert_idx = _remove_heading_and_table(doc, "Development Environment")
    _remove_heading_and_table(doc, "UAT Environment")
    _remove_heading_and_table(doc, "Production Environment")

    env_elements = [
        _make_heading(doc, "Applications", level=2),
        _make_table(doc, ["Name", "Application Type", "Purpose"], app_rows),
        _make_heading(doc, "Environment URLs", level=2),
        _make_para(
            doc,
            "The applications above are identical across environments; only "
            "their URLs differ.",
        ),
        _make_table(
            doc,
            ["Application", "Development", "UAT", "Production"],
            [[r[0], "", "", ""] for r in app_rows],
        ),
    ]
    body = doc.element.body
    if insert_idx is not None and insert_idx < len(body):
        ref = body[insert_idx]
        for el in env_elements:
            ref.addprevious(el)
    else:
        _append_to_body(doc, *env_elements)

    # ── Key Workflows table (Section 4.4) ─────────────────────────────────
    # Curated, plain-English view. extras["key_workflows"] is a list of
    # {name, function, trigger, purpose}; the full flow inventory is in the
    # appendix. Falls back to all cloud flows (without GUIDs) if not curated.
    key_workflows: list[dict] = extras.get("key_workflows", [])
    if key_workflows:
        kw_rows = [
            [k.get("name", ""), k.get("function", ""),
             k.get("trigger", ""), k.get("purpose", "")]
            for k in key_workflows
        ]
    else:
        kw_rows = [
            [f.display_name, "Cloud Flow",
             f.trigger_connector or f.trigger_type or "", ""]
            for f in components.flows
            if f.category == "Cloud Flow"
        ]
    _populate_table(
        doc,
        "Key workflows",
        kw_rows or [["(no cloud flows)", "", "", ""]],
        headers=["Workflow", "Function", "Trigger", "Purpose"],
    )


    # ── Security (Section 5) ──────────────────────────────────────────────
    _populate_security_configuration(doc, powerpages)
    _populate_security_roles(doc, components)

    # ── Component reference sections (main body, before Security) ────────
    section_elements = _build_component_sections(doc, components, extras, powerpages, solution)
    if section_elements and not _insert_before_heading(doc, "Security", section_elements):
        _append_to_body(doc, *section_elements)

    # ── Layout ────────────────────────────────────────────────────────────
    _apply_heading_layout(doc)

    doc.save(str(output_path))
    return output_path
