# As Built Document Generator — Claude Skill

A self-contained Claude Code skill that generates a client-ready **As Built
Document** (.docx) from a Power Platform solution export, using the Accelerate
Technology template.

Ask Claude for an "as built document" (or invoke `/as-built`) with a solution
`.zip` in your project, and it runs the whole process: parse the solution,
ask you a few questions, draft the narrative content for your review, generate
the document, and verify the output.

---

## Why SKILL.md is accompanied by scripts and assets

A skill is more than a prompt. `SKILL.md` tells Claude **what process to
follow**, but this skill deliberately splits the work between Claude and
bundled Python code, and both halves ship together:

| Part | Role | Why it exists |
|---|---|---|
| `SKILL.md` | The process definition Claude follows | Orchestration, judgement, drafting, verification — the things that need a model |
| `scripts/` | Deterministic parsing + Word generation | Repeatability — the things that must NOT need a model |
| `assets/` | The AT Word template | So the skill works on a machine that has nothing else |

The reasoning behind the split:

- **Determinism where it matters.** Parsing a solution zip and populating a
  Word template must produce the same output every run. If Claude wrote the
  document token-by-token, tables, formatting, and coverage would drift between
  runs and consume enormous context on large solutions (a solution export can
  contain hundreds of components). The Python pipeline guarantees the
  mechanical 90% is identical every time.
- **Judgement where it matters.** The solution file cannot tell you what the
  system is *for*. Claude drafts the overview, workflow purposes, integration
  register, and table/column descriptions, gets them corrected by the author,
  and feeds them into the generator through a reviewable JSON file
  (`--extras`). Nothing narrative is buried in code; nothing mechanical is
  left to chance.
- **Portability.** Because the parsers, writer, and template live inside the
  skill folder, copying this one folder to another machine or repo is a
  complete install. There is no dependency on the host project's code.

If the two halves were separated — the SKILL.md in one place, the scripts in a
project repo — the skill would silently break the first time someone copied it
without the other half. Keeping them in one folder makes the folder itself the
unit of sharing.

## Folder structure

```
as-built/
├── SKILL.md                 ← process definition Claude follows (start here)
├── README.md                ← this file
├── scripts/
│   ├── generate_docs.py     ← CLI entry point (python generate_docs.py --help)
│   ├── requirements.txt     ← python-docx, lxml, Pillow
│   ├── parsers/
│   │   ├── extractor.py         ← unzips / normalises the solution input
│   │   ├── solution.py          ← solution.xml: metadata + dependencies
│   │   ├── customizations.py    ← tables, columns, choices, flows, roles,
│   │   │                          relationships, web resources, …
│   │   └── folder_components.py ← managed-export folders: environment
│   │                              variables, custom APIs, Power Pages
│   └── writers/
│       ├── word_writer.py   ← populates the template, builds all sections
│       └── diagram.py       ← renders the data model diagram (PNG, Pillow)
└── assets/
    └── Accelerate As Built Document Template.docx
```

## Installation

1. Copy the whole `as-built/` folder into `.claude/skills/` (project-level) or
   `~/.claude/skills/` (personal).
2. Install Python 3.10+ if not present.
3. `pip install -r scripts/requirements.txt`

That's everything. The template is bundled; a project-local `template/*.docx`
can override it via `--template`.

## What gets generated

The generator populates the AT template into a full main-body document:
cover page and metadata, Solution Details, Applications and Environment URLs,
Key Workflows, Classic Workflows, Integrations, Data Model (diagram, per-table
sections with choice values), Power Pages Portal (pages, web roles, table
permissions), Configuration (environment variables, custom APIs, web
resources), Deployment & ALM (prerequisite solutions + placeholders), and
Security (portal authentication settings, security roles).

Sections that cannot be derived from a solution export (contacts, RACI,
environment URLs, backup/support arrangements) remain as template placeholders
for manual completion. `SKILL.md` lists the full conventions.

Secrets are always masked: environment variable values and site settings with
credential-like names are written as "value withheld from documentation".

## Running the generator manually (without Claude)

```
python scripts/generate_docs.py --solution "MySolution.zip" --verbose
python scripts/generate_docs.py --solution "MySolution.zip" --extras answers.json --output "output/MyDoc.docx"
```

`--verbose` prints the component summary and a coverage audit of any zip
folders the parsers don't understand. The `--extras` JSON schema is documented
in the `generate_docs.py` docstring and in `SKILL.md` — without it you get a
structurally complete document with generic narrative.

## Maintaining the skill

- **This folder is the canonical copy.** Fix bugs and add component types
  here, not in copies elsewhere.
- New Power Platform component type showing up in the audit output? Extend
  `parsers/folder_components.py` (folder-based) or `parsers/customizations.py`
  (customizations.xml-based), then add a section in
  `writers/word_writer.py`.
- Template changed? Replace the file in `assets/` — the writer finds tables by
  the heading text above them, so keep the template's heading names stable
  (e.g. "Development Accounts", "Key workflows", "Security Roles").
