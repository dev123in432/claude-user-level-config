"""
Parses customizations.xml and supplementary component files from a Power Platform solution.

Covers: Entities/Tables, Workflows/Flows, Security Roles, AppModules, CanvasApps,
        EnvironmentVariableDefinitions, ConnectionReferences, PluginAssemblies,
        Controls (PCF), and CustomAPIs.
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class TableColumn:
    schema_name: str
    display_name: str
    data_type: str
    required: bool = False
    description: str = ""
    is_auto_description: bool = False  # True when description was generated, not authored
    options: list[str] = field(default_factory=list)  # choice value labels


@dataclass
class DataverseTable:
    schema_name: str
    display_name: str
    description: str = ""
    is_custom: bool = False
    columns: list[TableColumn] = field(default_factory=list)


@dataclass
class CloudFlow:
    unique_name: str
    display_name: str
    trigger_type: str = ""
    trigger_connector: str = ""
    connectors: list[str] = field(default_factory=list)
    is_enabled: bool = True
    category: str = "Cloud Flow"


@dataclass
class SecurityRole:
    name: str
    role_id: str = ""
    description: str = ""
    # {table schema name (lower): {action: depth label}} — actions are Create,
    # Read, Write, Delete, Append, Append To, Assign, Share
    table_privileges: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass
class ModelDrivenApp:
    unique_name: str
    display_name: str
    description: str = ""
    entities: list[str] = field(default_factory=list)  # schema names of included tables


@dataclass
class CanvasApp:
    unique_name: str
    display_name: str
    description: str = ""
    screens: list[str] = field(default_factory=list)
    connectors: list[str] = field(default_factory=list)


@dataclass
class EnvironmentVariable:
    schema_name: str
    display_name: str
    data_type: str = ""
    default_value: str = ""
    description: str = ""


@dataclass
class ConnectionReference:
    logical_name: str
    display_name: str
    connector_id: str = ""
    connector_name: str = ""


@dataclass
class PluginStep:
    name: str
    message: str = ""
    entity: str = ""
    stage: str = ""


@dataclass
class PluginAssembly:
    name: str
    version: str = ""
    steps: list[PluginStep] = field(default_factory=list)


@dataclass
class CustomAPI:
    unique_name: str
    display_name: str
    binding_type: str = ""
    description: str = ""


@dataclass
class PCFControl:
    name: str
    display_name: str = ""
    version: str = ""


@dataclass
class Relationship:
    name: str            # relationship schema name
    rel_type: str        # "One-to-Many" or "Many-to-Many"
    first_entity: str    # referenced/parent (1-side) or first entity, logical name
    second_entity: str   # referencing/child (N-side) or second entity, logical name


@dataclass
class WebResource:
    name: str
    display_name: str = ""
    type_label: str = ""


@dataclass
class SolutionComponents:
    tables: list[DataverseTable] = field(default_factory=list)
    flows: list[CloudFlow] = field(default_factory=list)
    security_roles: list[SecurityRole] = field(default_factory=list)
    model_apps: list[ModelDrivenApp] = field(default_factory=list)
    canvas_apps: list[CanvasApp] = field(default_factory=list)
    env_variables: list[EnvironmentVariable] = field(default_factory=list)
    connection_references: list[ConnectionReference] = field(default_factory=list)
    plugin_assemblies: list[PluginAssembly] = field(default_factory=list)
    custom_apis: list[CustomAPI] = field(default_factory=list)
    pcf_controls: list[PCFControl] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    web_resources: list[WebResource] = field(default_factory=list)


# ── Field type mapping ────────────────────────────────────────────────────────

_FRIENDLY_TYPES: dict[str, str] = {
    "nvarchar": "Text",
    "string": "Text",
    "nchar": "Text",
    "ntext": "Multi-line Text",
    "memo": "Multi-line Text",
    "richtext": "Rich Text",
    "int": "Whole Number",
    "integer": "Whole Number",
    "bigint": "Whole Number",
    "decimal": "Decimal Number",
    "double": "Decimal Number",
    "float": "Floating Point Number",
    "money": "Currency",
    "boolean": "Yes/No",
    "bit": "Yes/No",
    "datetime": "Date & Time",
    "date": "Date Only",
    "picklist": "Choice",
    "multiselectpicklist": "Multi-select Choice",
    "state": "Status",
    "status": "Status Reason",
    "lookup": "Lookup",
    "owner": "Owner",
    "customer": "Customer",
    "partylist": "Multi-select Lookup",
    "uniqueidentifier": "Unique Identifier",
    "primarykey": "Unique Identifier",
    "file": "File",
    "image": "Image",
    "virtual": "Virtual",
    "managedproperty": "Managed Property",
    "entityname": "Entity Name",
    "calendarrules": "Calendar Rules",
}


def friendly_type(raw_type: str) -> str:
    """Return a user-friendly label for an internal Dataverse column type."""
    return _FRIENDLY_TYPES.get(raw_type.lower(), raw_type.title() if raw_type else "Unknown")


def auto_description(display_name: str, raw_type: str) -> str:
    """Generate a plain-English description when one is not provided in the solution."""
    ft = friendly_type(raw_type)
    type_phrases = {
        "Lookup": f"Links this record to a related {display_name} record.",
        "Choice": f"Selectable option indicating the {display_name}.",
        "Multi-select Choice": f"One or more selectable options for {display_name}.",
        "Yes/No": f"Indicates whether {display_name} is true or false.",
        "Currency": f"Monetary amount representing {display_name}.",
        "Date & Time": f"Date and time value for {display_name}.",
        "Date Only": f"Date value for {display_name}.",
        "Multi-line Text": f"Long-form text field for {display_name}.",
        "Rich Text": f"Formatted rich-text content for {display_name}.",
        "File": f"File attachment for {display_name}.",
        "Image": f"Image associated with {display_name}.",
        "Whole Number": f"Integer value representing {display_name}.",
        "Decimal Number": f"Decimal numeric value for {display_name}.",
        "Currency": f"Currency value for {display_name}.",
        "Status": f"System-managed status of the record.",
        "Status Reason": f"Reason for the current status of the record.",
        "Owner": f"User or team responsible for this record.",
        "Unique Identifier": f"System-generated unique identifier.",
    }
    return type_phrases.get(ft, f"Stores the {display_name} for this record.")


def _is_system_column(attr: ET.Element) -> bool:
    """
    Return True for columns that add no documentation value:
      - Currency base-value columns (_base suffix)
      - Phonetic / yomi columns (_yomi suffix)
      - Primary key columns (type primarykey)
    """
    logical = (attr.findtext("LogicalName") or "").lower()
    raw_type = (attr.findtext("Type") or "").lower()
    if raw_type == "primarykey":
        return True
    if logical.endswith("_base"):
        return True
    if logical.endswith("_yomi"):
        return True
    return False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _text(element: ET.Element | None, tag: str, default: str = "") -> str:
    if element is None:
        return default
    el = element.find(tag)
    return (el.text or default).strip() if el is not None else default


def _localized(element: ET.Element, lang: str = "1033") -> str:
    for n in element.findall(".//LocalizedName"):
        if n.get("languagecode") == lang:
            return n.get("description", "")
    nodes = element.findall(".//LocalizedName")
    return nodes[0].get("description", "") if nodes else ""


def _connector_friendly(connector_id: str) -> str:
    """Extract a friendly connector name from a provider path."""
    if not connector_id:
        return ""
    parts = connector_id.rstrip("/").split("/")
    name = parts[-1] if parts else connector_id
    # strip shared_ prefix common in Power Platform connector IDs
    if name.startswith("shared_"):
        name = name[len("shared_"):]
    return name.replace("-", " ").replace("_", " ").title()


# ── Canvas App parser (.msapp) ────────────────────────────────────────────────

def _parse_msapp(msapp_path: Path) -> CanvasApp:
    """Parse a .msapp file (zip) and extract summary information."""
    app = CanvasApp(
        unique_name=msapp_path.stem,
        display_name=msapp_path.stem,
    )
    try:
        with zipfile.ZipFile(msapp_path) as zf:
            names = zf.namelist()

            # App properties
            if "Properties.json" in names:
                with zf.open("Properties.json") as f:
                    props = json.load(f)
                app.display_name = props.get("Name") or props.get("DisplayName") or app.display_name
                app.description = props.get("Description") or ""

            # Screen names from Entropy.json
            if "Entropy.json" in names:
                with zf.open("Entropy.json") as f:
                    entropy = json.load(f)
                app.screens = [
                    s.get("Name", "") for s in entropy.get("Screens", []) if s.get("Name")
                ]

            # Connection/data sources
            if "DataSources.json" in names:
                with zf.open("DataSources.json") as f:
                    ds = json.load(f)
                seen: set[str] = set()
                for source in ds.get("DataSources", []):
                    kind = source.get("Type") or source.get("Kind") or ""
                    name = source.get("Name") or source.get("DataSourceName") or kind
                    if name and name not in seen:
                        seen.add(name)
                        app.connectors.append(name)

            # Fallback: scan Controls/ folder for screen names if Entropy didn't have them
            if not app.screens:
                screen_files = [n for n in names if n.startswith("Controls/") and n.endswith(".json")]
                for sf in screen_files:
                    screen_name = Path(sf).stem
                    if screen_name not in app.screens:
                        app.screens.append(screen_name)

    except Exception:
        pass  # malformed or encrypted .msapp — return what we have
    return app


# ── Flow JSON parser ──────────────────────────────────────────────────────────

def _parse_flow_json(flow_def: dict) -> tuple[str, str, list[str]]:
    """
    Returns (trigger_type, trigger_connector, connectors_list) from a flow definition dict.
    The dict is the inner 'definition' object from the flow JSON file.
    """
    trigger_type = ""
    trigger_connector = ""
    connectors: list[str] = []

    triggers = flow_def.get("triggers", {})
    if not isinstance(triggers, dict):
        triggers = {}
    for tname, tdef in triggers.items():
        if not isinstance(tdef, dict):
            continue
        trigger_type = tdef.get("type", tname)
        inputs = tdef.get("inputs", {})
        if not isinstance(inputs, dict):
            inputs = {}
        host = inputs.get("host", {})
        if not isinstance(host, dict):
            host = {}
        trigger_connector = _connector_friendly(
            host.get("connectionName") or host.get("apiId") or ""
        )
        break  # only one trigger per flow

    actions = flow_def.get("actions", {})
    if not isinstance(actions, dict):
        actions = {}
    seen: set[str] = set()
    for _aname, adef in actions.items():
        if not isinstance(adef, dict):
            continue
        inputs = adef.get("inputs", {})
        if not isinstance(inputs, dict):
            inputs = {}
        host = inputs.get("host", {})
        if not isinstance(host, dict):
            host = {}
        conn = _connector_friendly(
            host.get("connectionName") or host.get("apiId") or ""
        )
        if conn and conn not in seen:
            seen.add(conn)
            connectors.append(conn)

    return trigger_type, trigger_connector, connectors


# ── Main parsers ──────────────────────────────────────────────────────────────

def parse_customizations(xml_path: Path) -> SolutionComponents:
    """Parse customizations.xml and return all discovered components."""
    if not xml_path.exists():
        return SolutionComponents()

    tree = ET.parse(xml_path)
    root = tree.getroot()
    components = SolutionComponents()

    # ── Global option sets (needed to resolve choice column values) ────────
    def _option_labels(container: ET.Element) -> list[str]:
        labels = []
        for opt in container.findall("options/option"):
            for lb in opt.findall("labels/label"):
                if lb.get("languagecode") == "1033":
                    labels.append(lb.get("description", ""))
                    break
        return [l for l in labels if l]

    global_optionsets: dict[str, list[str]] = {}
    for os_el in root.findall(".//optionsets/optionset"):
        os_name = (os_el.get("Name") or "").strip().lower()
        if os_name:
            global_optionsets[os_name] = _option_labels(os_el)

    # ── Entities / Tables ──────────────────────────────────────────────────
    # Columns and display names live inside EntityInfo/entity, not directly
    # under Entity.  Only custom columns (IsCustomField=1) are documented.
    for entity in root.findall(".//Entities/Entity"):
        name_el = entity.find("Name")
        if name_el is None:
            continue
        schema_name = (name_el.text or "").strip()

        # Resolve display name: prefer EntityInfo LocalizedNames, fall back to
        # the LocalizedName attribute on <Name>
        ei_entity = entity.find("EntityInfo/entity")
        display_name = ""
        description = ""
        if ei_entity is not None:
            for ln in ei_entity.findall("LocalizedNames/LocalizedName"):
                if ln.get("languagecode") == "1033":
                    display_name = ln.get("description", "")
                    break
            for d in ei_entity.findall("Descriptions/Description"):
                if d.get("languagecode") == "1033":
                    description = d.get("description", "")
                    break
        display_name = display_name or name_el.get("LocalizedName") or schema_name

        table = DataverseTable(
            schema_name=schema_name,
            display_name=display_name,
            description=description,
            is_custom=True,
        )

        # Attributes are at EntityInfo/entity/attributes/attribute (lowercase)
        attr_parent = ei_entity.findall("attributes/attribute") if ei_entity is not None else []
        for attr in attr_parent:
            # Only document custom columns; skip system-generated ones
            if (attr.findtext("IsCustomField") or "0").strip() != "1":
                continue
            if _is_system_column(attr):
                continue
            col_name = (attr.findtext("LogicalName") or "").strip()
            raw_type = (attr.findtext("Type") or "").strip()
            col_display = ""
            for dn in attr.findall("displaynames/displayname"):
                if dn.get("languagecode") == "1033":
                    col_display = dn.get("description", col_name)
                    break
            col_display = col_display or col_name
            req_level = (attr.findtext("RequiredLevel") or "").strip().lower()
            # Use explicit description if present; otherwise auto-generate one
            desc = ""
            for d in attr.findall("Descriptions/Description"):
                if d.get("languagecode") == "1033":
                    desc = d.get("description", "")
                    break
            is_auto = False
            if not desc:
                desc = auto_description(col_display, raw_type)
                is_auto = True

            # Choice values: inline option set (unmanaged exports) or a
            # reference to a global option set by name (managed exports)
            options: list[str] = []
            if raw_type.lower() in ("picklist", "multiselectpicklist", "state", "status"):
                inline = attr.find("optionset")
                if inline is not None:
                    options = _option_labels(inline)
                if not options:
                    os_ref = (attr.findtext("OptionSetName") or "").strip().lower()
                    options = global_optionsets.get(os_ref, [])

            table.columns.append(
                TableColumn(
                    schema_name=col_name,
                    display_name=col_display,
                    data_type=friendly_type(raw_type),
                    required=req_level in ("required", "systemrequired"),
                    description=desc,
                    is_auto_description=is_auto,
                    options=options,
                )
            )
        components.tables.append(table)

    # ── Workflows / Cloud Flows ────────────────────────────────────────────
    for wf in root.findall(".//Workflows/Workflow"):
        name = (wf.get("Name") or wf.findtext("Name") or "").strip()
        unique_name = (wf.get("WorkflowId") or "").strip("{}")
        category = (wf.findtext("Category") or "").strip()
        cat_label = {
            "0": "Classic Workflow",
            "1": "Dialog",
            "2": "Business Process Flow",
            "3": "Action",
            "4": "Business Rule",
            "5": "Cloud Flow",
            "6": "Modern Flow",
            "7": "Desktop Flow",
        }.get(category, f"Type {category}")

        state = (wf.findtext("StateCode") or "1").strip()
        is_enabled = state == "1"

        flow = CloudFlow(
            unique_name=unique_name,
            display_name=name,
            is_enabled=is_enabled,
            category=cat_label,
        )

        # Try to parse trigger/connector info from embedded JSON
        json_data = wf.findtext("JsonData") or ""
        if json_data and category == "5":
            try:
                outer = json.loads(json_data)
                definition = outer.get("definition") or outer
                t_type, t_conn, conns = _parse_flow_json(definition)
                flow.trigger_type = t_type
                flow.trigger_connector = t_conn
                flow.connectors = conns
            except (json.JSONDecodeError, AttributeError):
                pass

        components.flows.append(flow)

    # ── Security Roles ─────────────────────────────────────────────────────
    # Privilege names follow prv{Action}{SchemaName}; depth levels map to the
    # standard access scopes. Some suffixes differ from the table schema name.
    _PRIV_ACTIONS = ("AppendTo", "Append", "Create", "Read", "Write", "Delete", "Assign", "Share")
    _ACTION_LABELS = {"AppendTo": "Append To"}
    _DEPTH_LABELS = {
        "Basic": "User",
        "Local": "BU",
        "Deep": "Parent/Child",
        "Global": "Org",
    }
    _SUFFIX_ALIASES = {
        "activity": "activitypointer",
        "note": "annotation",
        "emailtemplate": "template",
        "newprocess": "workflow",
        "user": "systemuser",
    }

    for role in root.findall(".//Roles/Role"):
        name = role.get("name") or role.get("Name") or role.findtext("Name") or ""
        role_id = role.get("id") or role.get("roleid") or ""
        if not name:
            continue
        sec_role = SecurityRole(
            name=name.strip(),
            role_id=role_id,
            description=(role.findtext("Description") or "").strip(),
        )
        for priv in role.findall(".//RolePrivileges/RolePrivilege"):
            pname = priv.get("name") or ""
            level = priv.get("level") or ""
            if not pname.startswith("prv"):
                continue
            rest = pname[3:]
            action = next((a for a in _PRIV_ACTIONS if rest.startswith(a)), None)
            if action is None:
                continue  # miscellaneous privilege (not a table CRUD right)
            suffix = rest[len(action):].lower()
            if not suffix:
                continue
            table_key = _SUFFIX_ALIASES.get(suffix, suffix)
            sec_role.table_privileges.setdefault(table_key, {})[
                _ACTION_LABELS.get(action, action)
            ] = _DEPTH_LABELS.get(level, level)
        components.security_roles.append(sec_role)

    # ── App Modules (Model-driven Apps) ────────────────────────────────────
    for app in root.findall(".//AppModules/AppModule"):
        unique = (app.findtext("UniqueName") or "").strip()
        display = _localized(app) or unique
        desc = ""
        for d in app.findall(".//Descriptions/Description"):
            if d.get("languagecode") == "1033":
                desc = d.get("description", "")
                break
        # Capture which tables (type=1) are included in this app
        entities = [
            c.get("schemaName", "").lower()
            for c in app.findall("AppModuleComponents/AppModuleComponent")
            if c.get("type") == "1" and c.get("schemaName")
        ]
        if unique:
            components.model_apps.append(
                ModelDrivenApp(
                    unique_name=unique,
                    display_name=display,
                    description=desc,
                    entities=entities,
                )
            )

    # ── Canvas Apps (metadata in customizations.xml) ───────────────────────
    for ca in root.findall(".//CanvasApps/CanvasApp"):
        unique = (ca.findtext("SchemaName") or ca.get("SchemaName") or "").strip()
        display = (ca.findtext("DisplayName") or ca.get("DisplayName") or unique).strip()
        desc = (ca.findtext("Description") or "").strip()
        if unique:
            components.canvas_apps.append(
                CanvasApp(unique_name=unique, display_name=display, description=desc)
            )

    # ── Environment Variable Definitions ───────────────────────────────────
    for evd in root.findall(".//EnvironmentVariableDefinitions/EnvironmentVariableDefinition"):
        schema = (evd.findtext("SchemaName") or evd.get("SchemaName") or "").strip()
        display = (evd.findtext("DisplayName") or _localized(evd) or schema).strip()
        dtype = (evd.findtext("Type") or evd.findtext("DataType") or "").strip()
        default = (evd.findtext("DefaultValue") or "").strip()
        desc = ""
        for d in evd.findall(".//Descriptions/Description"):
            if d.get("languagecode") == "1033":
                desc = d.get("description", "")
                break
        if schema:
            components.env_variables.append(
                EnvironmentVariable(
                    schema_name=schema,
                    display_name=display,
                    data_type=dtype,
                    default_value=default,
                    description=desc,
                )
            )

    # ── Connection References ──────────────────────────────────────────────
    for cr in root.findall(".//ConnectionReferences/ConnectionReference"):
        logical = (
            cr.get("ConnectionReferenceLogicalName")
            or cr.findtext("ConnectionReferenceLogicalName")
            or ""
        ).strip()
        display = (cr.findtext("DisplayName") or logical).strip()
        connector_id = (cr.findtext("ConnectorId") or "").strip()
        connector_name = _connector_friendly(connector_id)
        if logical:
            components.connection_references.append(
                ConnectionReference(
                    logical_name=logical,
                    display_name=display,
                    connector_id=connector_id,
                    connector_name=connector_name,
                )
            )

    # ── Plugin Assemblies ──────────────────────────────────────────────────
    for pa in root.findall(".//PluginAssemblies/PluginAssembly"):
        pa_name = (pa.findtext("Name") or pa.get("Name") or "").strip()
        version = (pa.findtext("Version") or "").strip()
        assembly = PluginAssembly(name=pa_name, version=version)
        for step in pa.findall(".//Steps/Step"):
            s_name = (step.findtext("Name") or step.get("Name") or "").strip()
            message = (step.findtext("MessageName") or "").strip()
            entity = (step.findtext("PrimaryEntityName") or "").strip()
            stage_code = (step.findtext("Stage") or "").strip()
            stage_label = {"10": "Pre-validation", "20": "Pre-operation", "40": "Post-operation"}.get(
                stage_code, stage_code
            )
            assembly.steps.append(
                PluginStep(name=s_name, message=message, entity=entity, stage=stage_label)
            )
        if pa_name:
            components.plugin_assemblies.append(assembly)

    # ── Custom APIs ────────────────────────────────────────────────────────
    for api in root.findall(".//CustomAPIs/CustomAPI"):
        unique = (api.findtext("UniqueName") or api.get("UniqueName") or "").strip()
        display = (api.findtext("DisplayName") or _localized(api) or unique).strip()
        binding = (api.findtext("BindingType") or "").strip()
        binding_label = {"0": "Global", "1": "Entity", "2": "Entity Collection"}.get(binding, binding)
        desc = ""
        for d in api.findall(".//Descriptions/Description"):
            if d.get("languagecode") == "1033":
                desc = d.get("description", "")
                break
        if unique:
            components.custom_apis.append(
                CustomAPI(
                    unique_name=unique,
                    display_name=display,
                    binding_type=binding_label,
                    description=desc,
                )
            )

    # ── Entity Relationships ───────────────────────────────────────────────
    for rel in root.findall(".//EntityRelationships/EntityRelationship"):
        rel_name = (rel.get("Name") or "").strip()
        rel_type = (rel.findtext("EntityRelationshipType") or "").strip()
        if rel_type == "OneToMany":
            first = (rel.findtext("ReferencedEntityName") or "").strip()
            second = (rel.findtext("ReferencingEntityName") or "").strip()
            label = "One-to-Many"
        elif rel_type == "ManyToMany":
            first = (rel.findtext("FirstEntityName") or "").strip()
            second = (rel.findtext("SecondEntityName") or "").strip()
            label = "Many-to-Many"
        else:
            continue
        if rel_name and first and second:
            components.relationships.append(
                Relationship(
                    name=rel_name,
                    rel_type=label,
                    first_entity=first.lower(),
                    second_entity=second.lower(),
                )
            )

    # ── Web Resources ──────────────────────────────────────────────────────
    _WR_TYPES = {
        "1": "HTML", "2": "CSS", "3": "JavaScript", "4": "XML", "5": "PNG",
        "6": "JPG", "7": "GIF", "8": "Silverlight", "9": "XSL", "10": "ICO",
        "11": "SVG", "12": "RESX",
    }
    for wr in root.findall(".//WebResources/WebResource"):
        wr_name = (wr.findtext("Name") or "").strip()
        if not wr_name:
            continue
        components.web_resources.append(
            WebResource(
                name=wr_name,
                display_name=(wr.findtext("DisplayName") or wr_name).strip(),
                type_label=_WR_TYPES.get((wr.findtext("WebResourceType") or "").strip(), "Other"),
            )
        )

    # ── PCF Controls ───────────────────────────────────────────────────────
    for ctrl in root.findall(".//Controls/Control"):
        name = (ctrl.findtext("Name") or ctrl.get("Name") or "").strip()
        display = (ctrl.findtext("DisplayName") or _localized(ctrl) or name).strip()
        version = (ctrl.findtext("Version") or "").strip()
        if name:
            components.pcf_controls.append(
                PCFControl(name=name, display_name=display, version=version)
            )

    return components


def enrich_canvas_apps(components: SolutionComponents, canvas_apps_dir: Path) -> None:
    """
    Supplement canvas app entries with data from .msapp files if present.
    Matches by schema name (file stem) or display name.
    """
    if not canvas_apps_dir.exists():
        return

    msapp_files = {f.stem.lower(): f for f in canvas_apps_dir.glob("*.msapp")}
    if not msapp_files:
        return

    # Update existing entries
    existing_names = {ca.unique_name.lower() for ca in components.canvas_apps}
    for ca in components.canvas_apps:
        msapp = msapp_files.get(ca.unique_name.lower())
        if msapp:
            parsed = _parse_msapp(msapp)
            ca.display_name = parsed.display_name or ca.display_name
            ca.description = parsed.description or ca.description
            ca.screens = parsed.screens or ca.screens
            ca.connectors = parsed.connectors or ca.connectors

    # Add any .msapp files not already captured
    for stem_lower, msapp_path in msapp_files.items():
        if stem_lower not in existing_names:
            parsed = _parse_msapp(msapp_path)
            components.canvas_apps.append(parsed)


def enrich_flows_from_json(components: SolutionComponents, workflows_dir: Path) -> None:
    """
    Supplement flow entries with trigger/connector data from standalone JSON files
    in the Workflows/ folder (present in newer solution exports).
    """
    if not workflows_dir.exists():
        return

    for json_file in workflows_dir.glob("*.json"):
        if json_file.name.endswith("_manifest.json"):
            continue
        try:
            with open(json_file, encoding="utf-8") as f:
                outer = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        name = outer.get("name") or outer.get("displayName") or json_file.stem
        # Try to match to existing flow entry (GUIDs in filenames vary in case)
        stem_lower = json_file.stem.lower()
        matched = next(
            (fl for fl in components.flows
             if fl.display_name == name
             or (fl.unique_name and fl.unique_name.lower() in stem_lower)),
            None,
        )
        definition = outer.get("definition") or outer.get("properties", {}).get("definition") or outer
        t_type, t_conn, conns = _parse_flow_json(definition)

        if matched:
            if not matched.trigger_type:
                matched.trigger_type = t_type
            if not matched.trigger_connector:
                matched.trigger_connector = t_conn
            if not matched.connectors:
                matched.connectors = conns
        else:
            # New flow not in customizations.xml
            components.flows.append(
                CloudFlow(
                    unique_name=json_file.stem,
                    display_name=name,
                    trigger_type=t_type,
                    trigger_connector=t_conn,
                    connectors=conns,
                    category="Cloud Flow",
                )
            )
