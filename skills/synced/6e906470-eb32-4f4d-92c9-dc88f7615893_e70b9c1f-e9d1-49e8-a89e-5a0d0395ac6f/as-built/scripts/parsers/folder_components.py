"""
Parses folder-based components from a Power Platform solution export.

Managed (and some unmanaged) exports store several component types as
per-component folders rather than entries in customizations.xml:

  environmentvariabledefinitions/<schema>/environmentvariabledefinition.xml
  customapis/<name>/customapi.xml
  powerpagecomponents/<guid>/powerpagecomponent.xml

This module supplements SolutionComponents with those, and reports any
remaining root-level folders it does not understand so the caller can flag
them for manual documentation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET

from parsers.customizations import (
    SolutionComponents,
    EnvironmentVariable,
    CustomAPI,
)


# ── Power Pages ───────────────────────────────────────────────────────────────

# Official powerpagecomponenttype labels — see the Dataverse powerpagecomponent
# table reference on Microsoft Learn.
POWERPAGES_COMPONENT_TYPES: dict[str, str] = {
    "1": "Publishing State",
    "2": "Web Page",
    "3": "Web File",
    "4": "Web Link Set",
    "5": "Web Link",
    "6": "Page Template",
    "7": "Content Snippet",
    "8": "Web Template",
    "9": "Site Setting",
    "10": "Web Page Access Control Rule",
    "11": "Web Role",
    "12": "Website Access",
    "13": "Site Marker",
    "15": "Basic Form",
    "16": "Basic Form Metadata",
    "17": "List",
    "18": "Table Permission",
    "19": "Advanced Form",
    "20": "Advanced Form Step",
    "21": "Advanced Form Metadata",
    "24": "Poll Placement",
    "26": "Ad Placement",
    "27": "Bot Consumer",
    "28": "Column Permission Profile",
    "29": "Column Permission",
    "30": "Redirect",
    "31": "Publishing State Transition Rule",
    "32": "Shortcut",
    "33": "Cloud Flow",
    "34": "UX Component",
    "35": "Server Logic",
}


@dataclass
class PowerPagesComponent:
    name: str
    type_code: str
    type_label: str
    is_active: bool = True
    detail: str = ""  # type-specific extra info (e.g. partial URL, table + rights)


@dataclass
class PowerPagesSite:
    components: list[PowerPagesComponent] = field(default_factory=list)

    def by_type(self) -> dict[str, list[PowerPagesComponent]]:
        grouped: dict[str, list[PowerPagesComponent]] = {}
        for c in self.components:
            grouped.setdefault(c.type_label, []).append(c)
        return grouped

    def auth_settings(self) -> list[tuple[str, str]]:
        """
        Active, configured Authentication/* site settings as (name, value),
        values masked when the setting name looks credential-like. Settings
        with no value (stub providers Power Pages creates by default) are
        excluded — only actual configuration is documented.
        """
        rows = []
        for c in self.components:
            if c.type_code != "9" or not c.is_active:
                continue
            if not c.name.startswith("Authentication/"):
                continue
            value = c.detail or ""
            if not value:
                continue
            last_segment = c.name.rsplit("/", 1)[-1]
            if re.search(r"(secret|password|token|key)$", last_segment, re.IGNORECASE):
                value = "•••• (secret — value withheld from documentation)"
            rows.append((c.name, value))
        return sorted(rows)


# ── Secret masking ────────────────────────────────────────────────────────────

_SECRET_NAME_RE = re.compile(
    r"(password|secret|apikey|api[_-]?key|token|credential|connectionstring)",
    re.IGNORECASE,
)


def _mask_if_secret(schema_name: str, value: str, secret_store: str = "0") -> str:
    """Never print credential-like values into documentation."""
    if not value:
        return value
    if secret_store.strip() not in ("", "0") or _SECRET_NAME_RE.search(schema_name):
        return "•••• (secret — value withheld from documentation)"
    return value


# ── Environment variable definitions ─────────────────────────────────────────

_ENV_TYPE_LABELS = {
    "100000000": "Text",
    "100000001": "Number",
    "100000002": "Boolean",
    "100000003": "JSON",
    "100000004": "Data Source",
    "100000005": "Secret",
}


def parse_env_variable_folders(root: Path, components: SolutionComponents) -> None:
    """Read environmentvariabledefinitions/*/environmentvariabledefinition.xml."""
    base = root / "environmentvariabledefinitions"
    if not base.exists():
        return

    existing = {ev.schema_name.lower() for ev in components.env_variables}

    for def_file in sorted(base.glob("*/environmentvariabledefinition.xml")):
        try:
            el = ET.parse(def_file).getroot()
        except ET.ParseError:
            continue
        schema = (el.get("schemaname") or def_file.parent.name).strip()
        if schema.lower() in existing:
            continue

        display = schema
        dn = el.find("displayname")
        if dn is not None:
            display = dn.get("default") or display

        desc = ""
        d = el.find("description")
        if d is not None:
            desc = d.get("default") or ""

        type_code = (el.findtext("type") or "").strip()
        secret_store = (el.findtext("secretstore") or "0").strip()
        default = (el.findtext("defaultvalue") or "").strip()

        # A current value may ship alongside the definition
        current = ""
        values_file = def_file.parent / "environmentvariablevalues.json"
        if values_file.exists():
            try:
                vals = json.loads(values_file.read_text(encoding="utf-8"))
                entries = vals.get("environmentvariablevalues", vals)
                if isinstance(entries, list) and entries:
                    current = str(entries[0].get("value", ""))
                elif isinstance(entries, dict):
                    current = str(entries.get("value", ""))
            except (json.JSONDecodeError, OSError):
                pass

        value_shown = _mask_if_secret(schema, current or default, secret_store)

        components.env_variables.append(
            EnvironmentVariable(
                schema_name=schema,
                display_name=display,
                data_type=_ENV_TYPE_LABELS.get(type_code, type_code),
                default_value=value_shown,
                description=desc,
            )
        )


# ── Custom APIs ───────────────────────────────────────────────────────────────

def parse_custom_api_folders(root: Path, components: SolutionComponents) -> None:
    """Read customapis/*/customapi.xml."""
    base = root / "customapis"
    if not base.exists():
        return

    existing = {a.unique_name.lower() for a in components.custom_apis}
    binding_labels = {"0": "Global", "1": "Entity", "2": "Entity Collection"}

    for api_file in sorted(base.glob("*/customapi.xml")):
        try:
            el = ET.parse(api_file).getroot()
        except ET.ParseError:
            continue
        unique = (el.get("uniquename") or api_file.parent.name).strip()
        if unique.lower() in existing:
            continue

        display = unique
        dn = el.find("displayname")
        if dn is not None:
            display = dn.get("default") or display

        desc = ""
        d = el.find("description")
        if d is not None:
            desc = (d.get("default") or "").strip()

        binding = (el.findtext("bindingtype") or "").strip()

        components.custom_apis.append(
            CustomAPI(
                unique_name=unique,
                display_name=display.strip(),
                binding_type=binding_labels.get(binding, binding),
                description=desc,
            )
        )


# ── Power Pages components ────────────────────────────────────────────────────

def _powerpages_detail(type_code: str, content: dict) -> str:
    """Extract a short, type-appropriate detail string from the content JSON."""
    if type_code == "2":  # Web Page
        url = content.get("partialurl", "")
        return f"/{url}" if url else ""
    if type_code == "18":  # Table Permission
        table = str(content.get("entitylogicalname") or content.get("entityname") or "")
        rights = [
            r for r in ("read", "create", "write", "delete", "append", "appendto")
            if str(content.get(r, "")).lower() in ("true", "1")
        ]
        scope_labels = {
            "756150000": "Global",
            "756150001": "Contact",
            "756150002": "Account",
            "756150003": "Self",
            "756150004": "Parent",
        }
        scope = str(content.get("scope", "") or "")
        scope = scope_labels.get(scope, scope)
        parts = [p for p in (table, scope, ", ".join(rights)) if p]
        return " | ".join(parts)
    if type_code == "9":  # Site Setting
        val = str(content.get("value", ""))
        return val if len(val) <= 80 else val[:77] + "..."
    if type_code == "33":  # Cloud Flow
        return content.get("flowtriggerurl", "") and "HTTP-triggered flow" or ""
    return ""


def parse_powerpages_folders(root: Path) -> PowerPagesSite:
    """Read powerpagecomponents/*/powerpagecomponent.xml into a PowerPagesSite."""
    site = PowerPagesSite()
    base = root / "powerpagecomponents"
    if not base.exists():
        return site

    for comp_file in sorted(base.glob("*/powerpagecomponent.xml")):
        try:
            el = ET.parse(comp_file).getroot()
        except ET.ParseError:
            continue
        name = (el.findtext("name") or comp_file.parent.name).strip()
        type_code = (el.findtext("powerpagecomponenttype") or "").strip()
        state = (el.findtext("statecode") or "0").strip()

        content: dict = {}
        raw = el.findtext("content") or ""
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    content = parsed
            except json.JSONDecodeError:
                pass

        # Mask secret-looking site settings (e.g. API keys stored as settings)
        detail = _powerpages_detail(type_code, content)
        if type_code == "9":
            detail = _mask_if_secret(name, detail)

        site.components.append(
            PowerPagesComponent(
                name=name,
                type_code=type_code,
                type_label=POWERPAGES_COMPONENT_TYPES.get(
                    type_code, f"Type {type_code}"
                ),
                is_active=state == "0",
                detail=detail,
            )
        )
    return site


# ── Coverage audit ────────────────────────────────────────────────────────────

# Root-level items the pipeline reads (directly or via customizations.xml)
_HANDLED_ROOTS = {
    "solution.xml",
    "customizations.xml",
    "[content_types].xml",
    "canvasapps",
    "workflows",
    "webresources",
    "environmentvariabledefinitions",
    "customapis",
    "powerpagecomponents",
}


def audit_unhandled_folders(root: Path) -> list[tuple[str, int]]:
    """
    Return (folder_name, file_count) for root-level folders the parsers do not
    cover. These should be reviewed and documented manually if significant.
    """
    unhandled: list[tuple[str, int]] = []
    for item in sorted(root.iterdir()):
        if item.name.lower() in _HANDLED_ROOTS:
            continue
        if item.is_dir():
            count = sum(1 for _ in item.rglob("*") if _.is_file())
            unhandled.append((item.name, count))
    return unhandled
