"""Parses solution.xml to extract solution-level metadata."""

from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass
class SolutionData:
    unique_name: str = ""
    display_name: str = ""
    version: str = ""
    is_managed: bool = False
    publisher_name: str = ""
    publisher_unique_name: str = ""
    publisher_prefix: str = ""
    # Base solutions that must exist in the target environment before import,
    # as "Name (version)" strings derived from the export's dependency list.
    dependencies: list[str] = field(default_factory=list)


def _localized(element: ET.Element, lang: str = "1033") -> str:
    """Return the description for the given language code, falling back to first found."""
    names = element.findall(f"LocalizedNames/LocalizedName")
    for n in names:
        if n.get("languagecode") == lang:
            return n.get("description", "")
    # fallback: first entry
    if names:
        return names[0].get("description", "")
    return ""


def parse_solution_xml(xml_path: Path) -> SolutionData:
    if not xml_path.exists():
        raise FileNotFoundError(f"solution.xml not found at {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    manifest = root.find("SolutionManifest")
    if manifest is None:
        manifest = root  # some exports wrap differently

    data = SolutionData()
    data.unique_name = (manifest.findtext("UniqueName") or "").strip()
    data.display_name = _localized(manifest) or data.unique_name
    data.version = (manifest.findtext("Version") or "").strip()
    data.is_managed = (manifest.findtext("Managed") or "0").strip() == "1"

    pub = manifest.find("Publisher")
    if pub is not None:
        data.publisher_unique_name = (pub.findtext("UniqueName") or "").strip()
        data.publisher_name = _localized(pub) or data.publisher_unique_name
        data.publisher_prefix = (pub.findtext("CustomizationPrefix") or "").strip()

    # Required base solutions ("Active" is the unmanaged layer, not a solution)
    deps: set[str] = set()
    for req in root.findall(".//MissingDependency/Required"):
        sol_name = (req.get("solution") or "").strip()
        if sol_name and sol_name != "Active":
            deps.add(sol_name)
    data.dependencies = sorted(deps)

    return data
