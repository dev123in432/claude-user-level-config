---
name: as-built
description: Generate an As Built Document (.docx) from a Power Platform solution export using the Accelerate Technology template. Use when the user asks for an "as built" document, asks to document a Power Platform solution, or provides a solution .zip and wants delivery documentation.
---

# As Built Document Generator

Produce a client-ready As Built Document from a Power Platform solution export.
The heavy lifting is done by the bundled Python generator (deterministic parsing
and Word output); your job is to orchestrate it, fill the gaps it cannot know
about, and quality-check the result.

Everything needed is inside this skill folder:

```
as-built/
├── SKILL.md                 ← this process definition
├── scripts/
│   ├── generate_docs.py     ← the generator (run this)
│   ├── requirements.txt     ← python-docx, lxml
│   ├── parsers/             ← solution.xml, customizations.xml, folder-based components
│   └── writers/             ← Word template population
└── assets/
    └── Accelerate As Built Document Template.docx
```

## Process

### 1. Locate inputs

- **Solution file**: a Power Platform solution `.zip` (or unpacked folder). If the
  user attached or mentioned one, use it. If several `.zip` files exist in the
  project, ask which one. Both managed and unmanaged exports work.
- **Template**: the bundled template in `assets/` is the default. If the project
  has its own `template/*.docx` that is newer or the user names one, prefer that
  via `--template`.
- **Dependencies**: if the first run fails with `ModuleNotFoundError`, run
  `pip install -r scripts/requirements.txt`.

### 2. Baseline run (discovery)

Run the generator in verbose mode first, outputting to a temp location:

```
python "<skill>/scripts/generate_docs.py" --solution "<zip>" --verbose --output "<scratchpad>/draft.docx"
```

Read the printed summary carefully. It tells you:

- Solution name, version, publisher, managed/unmanaged.
- Component counts (apps, flows, tables, roles, env vars, Power Pages, …).
- **`[audit]` lines** — root folders in the zip the parsers do not understand.
  These are coverage gaps: inspect them (list a few files, read one) and decide
  whether they warrant a manually authored appendix section or at least a note
  to the user. Never silently ignore an audit line.

Sanity-check counts against the zip itself if anything looks off (e.g. a
`Workflows/` folder with 40 files but 0 flows parsed).

### 3. Gather and draft enrichment

The document follows client-facing As Built conventions. Identity codes are
limited to logical names; never GUIDs. All component reference sections are
main-body sections (Data Model, Power Pages Portal, Configuration,
Deployment & ALM) — the appendix is reserved for supplementary material added
manually. Every top-level section starts on a new page. System components are
listed once, in a single Applications table; per-environment differences are
captured only in an Environment URLs table (the URL is the only thing that
varies).

Further auto-populated content: a Solution Details table (name, version,
publisher, prefix, managed type) under System Overview; prerequisite solutions
(from the export's dependency list) under Deployment & ALM; portal
authentication site settings (identity provider, registration behaviour;
secrets masked) under Security Configuration; a data model diagram and choice
column values in the Data Model; and web resources under Configuration.
Deployment & ALM otherwise contains [To be completed] placeholders — the
export cannot describe environment strategy or deployment process.

The data model diagram is rendered (Pillow) from the solution's relationships:
curate `diagram_tables` in the extras JSON to the core business tables
(~8–12) so it stays readable — never dump every table in. Redundant edges are
removed automatically (transitive reduction), and relationship tables are NOT
generated — the diagram replaces them.

Ask the user (concise, batched — use the question tool where available) for
what the solution file cannot tell you:

1. **Organisation / client name** — default is the publisher name from the
   solution; confirm it (publisher is often the consultancy, not the client).
2. **Author name** for the cover page.
3. **Document purpose** — one sentence, e.g. handover, project closure, support.

Then **draft** the following yourself from the parsed components and show the
user for correction — do not ask them to write from scratch:

4. **Solution overview** — 1–3 paragraphs: what the solution is, what it's
   built on, its main moving parts.
5. **Application purposes** (`app_purposes`) — one line per app/portal for the
   Section 4 environment tables.
6. **Key workflows** (`key_workflows`) — the cloud flows grouped by function
   (approvals, notifications, integrations, portal support, …), each with a
   plain-English purpose. This is the only flow listing in the document, so
   cover every flow unless the user asks to trim.
7. **Integrations** (`integrations`) — infer external systems from environment
   variables, connectors, and flow names; for each: purpose, direction
   (inbound/outbound/bidirectional), and authentication mechanism.
8. **Table descriptions** (`table_descriptions`) — a brief purpose statement
   for every Dataverse table (only a few have authored descriptions in the
   solution file).
9. **Column descriptions** (`column_descriptions`) — purposes for custom
   columns on the custom tables. The generator auto-writes a fallback from the
   column name/type, but those read as filler; draft real ones at least for the
   core business tables.

Write everything to a JSON file in the scratchpad (all keys optional):

```json
{
  "org_name": "...",
  "author_name": "...",
  "doc_purpose": "...",
  "solution_overview": "...",
  "portal_name": "...",
  "app_purposes": {"portal": "...", "<app unique_name>": "..."},
  "key_workflows": [{"name": "...", "function": "...", "trigger": "...", "purpose": "..."}],
  "integrations": [{"name": "...", "purpose": "...", "direction": "...", "auth": "..."}],
  "table_descriptions": {"<table schema lowercase>": "..."},
  "column_descriptions": {"<table>.<column> lowercase": "..."},
  "diagram_tables": ["<core table logical names for the data model diagram>"]
}
```

Security roles need no enrichment — the generator lists each role with the
description authored in the solution, which should outline what the role
grants. Detailed per-table permission matrices are deliberately not generated
(too granular for this document). If a role has no description in the solution,
suggest the user add one in Power Platform rather than drafting it, so the
source stays authoritative.

### 4. Final generation

```
python "<skill>/scripts/generate_docs.py" --solution "<zip>" --extras "<answers.json>" --output "output/<SolutionName>_AsBuilt_V<major.minor>.docx"
```

Save into the project's `output/` folder. Use the solution version for the
document version unless the user says otherwise.

### 5. Verify before delivering

- Re-check the console output for `[audit]` gaps and errors.
- Confirm the file exists and has a plausible size (the template alone is
  ~4.3 MB; the output should be at least that).
- Spot-check content by reading `word/document.xml` inside the docx (it is a
  zip): confirm the organisation name replaced `[Organisation name]`, and that
  appendix sections for the major component types are present.

### 6. Report to the user

Tell the user:

- Where the document was saved.
- A component summary (what was documented automatically).
- **What still needs manual completion** — these sections cannot be derived
  from a solution file and are left as template placeholders:
  contact details, version control table, distribution list, abbreviations,
  environment URLs/tenant IDs, per-environment app URLs, security
  configuration (auth/MFA/conditional access), user management, RACI,
  backup & recovery, support & escalation.
- Any coverage gaps from the audit and what you did about them.

## Behaviours and caveats

- **Secrets are masked.** Environment variable values and site settings whose
  names look credential-like (password, secret, key, token, …) are written as
  "•••• (secret — value withheld from documentation)". Do not undo this; if raw
  values are truly needed the user can add them manually. If you notice other
  plaintext secrets in parsed output, do not copy them into the document or the
  conversation.
- **Managed exports** keep environment variables, custom APIs and Power Pages
  components in per-component folders rather than `customizations.xml`; the
  bundled parsers handle this. Unmanaged exports are also fine.
- **Power Pages solutions** get a main-body "Power Pages Portal" section with
  detail tables only for structure- and security-relevant types: web pages
  with partial URLs, web roles, table permissions with scope and rights,
  advanced forms, lists, cloud flows, server logic. Not documented: counts of
  component types, implementation detail (site settings, web files, templates,
  snippets), default platform components (basic forms, web link sets), and
  inactive/deleted components.
- **Document conventions**: main body = functional description for the client;
  appendix = technical reference. Logical names are the only identity codes
  shown — no GUIDs, no duplicated schema-name columns. Every listed component
  should carry a brief purpose statement.
- **Do not edit the generated docx by hand** for content fixes — fix the extras
  JSON or the parsers and regenerate, so the process stays repeatable.
- If the generator itself needs a change (new component type, template change),
  edit the copies inside this skill's `scripts/` folder — the skill is the
  self-contained, shareable unit.

## Sharing this skill

Copy the whole `as-built/` folder into another machine's or repo's
`.claude/skills/` directory. Requirements: Python 3.10+, then
`pip install -r scripts/requirements.txt` on first use. Nothing else is needed —
the template ships in `assets/`.
