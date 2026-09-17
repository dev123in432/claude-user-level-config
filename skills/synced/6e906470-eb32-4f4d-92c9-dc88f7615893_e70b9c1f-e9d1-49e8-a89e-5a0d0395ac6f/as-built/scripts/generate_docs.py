#!/usr/bin/env python3
"""
generate_docs.py — Accelerate Technology As-Built Document Generator (skill bundle)

Parses a Power Platform solution (.zip or unpacked folder) and produces a
populated As-Built Word document based on the AT template.

Usage:
    python generate_docs.py --solution path/to/solution.zip --template path/to/template.docx
    python generate_docs.py --solution solution.zip --org "Contoso" --author "Jane Smith"
    python generate_docs.py --solution solution.zip --extras answers.json

The --extras JSON file supports these keys (all optional):
    org_name          str   — organisation name for the cover page
    author_name       str   — document author
    solution_overview str   — paragraph(s) inserted under "System Overview"
    doc_purpose       str   — purpose statement inserted under "System Overview"
    portal_name       str   — display name for the Power Pages site row
    app_purposes      {app unique_name or "portal": purpose} — Applications table
    key_workflows     [{name, function, trigger, purpose}] — Key Workflows section
    integrations      [{name, purpose, direction, auth}] — Integrations section
    table_descriptions  {table schema (lower): description} — Data Model intro text
    column_descriptions {"<table>.<column>" (lower): description} — column purposes
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Allow running from anywhere
sys.path.insert(0, str(Path(__file__).parent))

from parsers.extractor import SolutionExtractor
from parsers.solution import parse_solution_xml
from parsers.customizations import (
    parse_customizations,
    enrich_canvas_apps,
    enrich_flows_from_json,
)
from parsers.folder_components import (
    parse_env_variable_folders,
    parse_custom_api_folders,
    parse_powerpages_folders,
    audit_unhandled_folders,
)
from writers.word_writer import generate_document

SKILL_DIR = Path(__file__).parent.parent
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "Accelerate As Built Document Template.docx"


def build_output_path(solution_name: str, output_arg: str | None) -> Path:
    if output_arg:
        p = Path(output_arg)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    out_dir = Path.cwd() / "output"
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in solution_name).strip()
    return out_dir / f"{safe_name}_AsBuilt_{timestamp}.docx"


def print_summary(solution, components, powerpages, unhandled) -> None:
    sep = "-" * 60
    print(f"\n{sep}")
    print(f"  Solution   : {solution.display_name} ({solution.unique_name})")
    print(f"  Version    : {solution.version}")
    print(f"  Publisher  : {solution.publisher_name}")
    print(f"  Managed    : {'Yes' if solution.is_managed else 'No'}")
    print(sep)
    print(f"  Canvas Apps          : {len(components.canvas_apps)}")
    print(f"  Cloud Flows          : {sum(1 for f in components.flows if f.category == 'Cloud Flow')}")
    print(f"  Classic Workflows    : {sum(1 for f in components.flows if f.category != 'Cloud Flow')}")
    print(f"  Dataverse Tables     : {len(components.tables)}")
    print(f"  Model-Driven Apps    : {len(components.model_apps)}")
    print(f"  Security Roles       : {len(components.security_roles)}")
    print(f"  Environment Variables: {len(components.env_variables)}")
    print(f"  Connection References: {len(components.connection_references)}")
    print(f"  Plugin Assemblies    : {len(components.plugin_assemblies)}")
    print(f"  Custom APIs          : {len(components.custom_apis)}")
    print(f"  PCF Controls         : {len(components.pcf_controls)}")
    if powerpages.components:
        print(f"  Power Pages Components: {len(powerpages.components)}")
        for type_label, comps in sorted(powerpages.by_type().items()):
            print(f"    - {type_label}: {len(comps)}")
    print(sep)
    if unhandled:
        print("  [audit] Root folders NOT parsed (review & document manually):")
        for name, count in unhandled:
            print(f"    - {name}/ ({count} files)")
        print(sep)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an As-Built document from a Power Platform solution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--solution", "-s", required=True, metavar="PATH",
                        help="Path to the exported solution .zip or unpacked solution folder.")
    parser.add_argument("--output", "-o", metavar="FILE",
                        help="Output .docx path (default: ./output/<SolutionName>_AsBuilt_<timestamp>.docx).")
    parser.add_argument("--template", "-t", metavar="FILE",
                        help="Path to the Word template .docx (default: bundled AT template).")
    parser.add_argument("--org", metavar="NAME", default="",
                        help="Organisation name (overrides publisher name from solution).")
    parser.add_argument("--author", metavar="NAME", default="",
                        help="Author name to stamp on the document.")
    parser.add_argument("--extras", metavar="FILE",
                        help="JSON file with enrichment content (see module docstring).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print component summary after parsing.")

    args = parser.parse_args()

    # ── Locate template ───────────────────────────────────────────────────
    template_path = Path(args.template) if args.template else DEFAULT_TEMPLATE
    if not template_path.exists():
        print(f"[error] Template not found: {template_path}", file=sys.stderr)
        return 1

    # ── Load extras ───────────────────────────────────────────────────────
    extras: dict = {}
    if args.extras:
        try:
            extras = json.loads(Path(args.extras).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"[error] Could not read extras file: {e}", file=sys.stderr)
            return 1

    # ── Parse solution ────────────────────────────────────────────────────
    print(f"[info] Loading solution: {args.solution}")
    try:
        with SolutionExtractor(args.solution) as extractor:
            solution = parse_solution_xml(extractor.solution_xml())
            components = parse_customizations(extractor.customizations_xml())

            # Standalone component files (present in most exports)
            enrich_canvas_apps(components, extractor.canvas_apps_dir())
            enrich_flows_from_json(components, extractor.workflows_dir())

            # Folder-based components (managed exports keep these out of
            # customizations.xml)
            parse_env_variable_folders(extractor.root, components)
            parse_custom_api_folders(extractor.root, components)
            powerpages = parse_powerpages_folders(extractor.root)

            unhandled = audit_unhandled_folders(extractor.root)

    except FileNotFoundError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[error] Failed to parse solution: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    if args.verbose:
        print_summary(solution, components, powerpages, unhandled)
    elif unhandled:
        print("[audit] Root folders NOT parsed (review & document manually): "
              + ", ".join(f"{n}/ ({c} files)" for n, c in unhandled))

    # ── Generate document ─────────────────────────────────────────────────
    output_path = build_output_path(solution.display_name or "Solution", args.output)
    print(f"[info] Generating document: {output_path.name}")

    try:
        generate_document(
            template_path=template_path,
            output_path=output_path,
            solution=solution,
            components=components,
            org_name=args.org,
            author_name=args.author,
            extras=extras,
            powerpages=powerpages,
        )
    except Exception as e:
        print(f"[error] Document generation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    print(f"[done] Document saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
