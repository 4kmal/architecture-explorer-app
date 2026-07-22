#!/usr/bin/env python3
"""Regression checks for native BM/EN editing across every registered diagram."""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_ATTRIBUTES = {
    "label",
    "value",
    "labelEn",
    "labelMs",
    "simpleLabelEn",
    "simpleLabelMs",
    "codeLabelEn",
    "codeLabelMs",
}
VOLATILE_ATTRIBUTES = {"modified", "etag", "agent"}
EXPECTED_DIAGRAMS = 55
EXPECTED_SOURCES = 54
EXPECTED_STRUCTURE = "660ac482980ffa6282fc22ba58c6f527991d017e027353e5193773368948ea5a"
REVIEWED_MAP_FLOWCHART = ROOT / "assets" / "editor" / "flowchart-user-explore-3d-map.drawio"
POLISHED_MODULE_HIERARCHY = ROOT / "assets" / "editor" / "module-hierarchy.drawio"
ORIGINAL_MODULE_HIERARCHY = ROOT / "assets" / "editor" / "module-hierarchy-original.drawio"
ORIGINAL_MODULE_STRUCTURE = "d82873ab76b5b401502e8d7f54fa1c660aa0e63f648dc593f84415f669748291"
DESIGN_SOURCES = {
    ROOT / "assets" / "editor" / "architecture-layered.drawio",
    ROOT / "assets" / "editor" / "architecture-layered-original.drawio",
    POLISHED_MODULE_HIERARCHY,
    ORIGINAL_MODULE_HIERARCHY,
}
TECHNICAL_DESIGN_LABELS = {
    "PetaKerja",
    "src/main.ts src/MyPetaApp.ts",
    "templates.ts styles.css",
    "MapLibre GL JS",
    "POIManager SearchManager CategoryManager",
    "JobFinderManager",
    "InsightsManager",
    "ChatbotManager",
    "supa-api.ts grep-api.ts api.ts",
    "OpenDataAPI",
    "authenticatedFetch",
    "server/app.ts",
    "GET /api/jobs/supa",
    "POST /api/search-jobs",
    "POST /api/assistant/chat",
    "Supabase PostgreSQL PostGIS",
    "public.scraped_jobs public.job_listings",
    "api.data.gov.my",
    "Better Auth",
    "InsightsManager OpenDataAPI",
}


def structural_node(element: ET.Element) -> dict[str, object]:
    return {
        "tag": element.tag,
        "attrs": sorted(
            (name, value)
            for name, value in element.attrib.items()
            if name not in TRANSLATION_ATTRIBUTES | VOLATILE_ATTRIBUTES
        ),
        "children": [structural_node(child) for child in element],
    }


def page_structure_hash(pages: list[tuple[str, ET.Element]]) -> str:
    payload = [
        {"identity": identity, "tree": structural_node(page)}
        for identity, page in sorted(pages, key=lambda item: item[0])
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def visible_elements(page: ET.Element) -> list[tuple[ET.Element, str]]:
    wrappers = page.findall(".//object")
    wrapped_cell_ids = {
        cell.get("id", "")
        for wrapper in wrappers
        for cell in [wrapper.find("mxCell")]
        if cell is not None
    }
    elements = [(wrapper, "label") for wrapper in wrappers]
    elements.extend(
        (cell, "value")
        for cell in page.findall(".//mxCell")
        if cell.get("id", "") not in wrapped_cell_ids
    )
    return [(element, attribute) for element, attribute in elements if element.get(attribute)]


def clean_label(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def assert_polished_module_hierarchy(errors: list[str]) -> None:
    page = ET.parse(POLISHED_MODULE_HIERARCHY).getroot().find("diagram")
    if page is None:
        errors.append("polished Module Hierarchy is missing its Draw.io page")
        return
    wrappers = {wrapper.get("id", ""): wrapper for wrapper in page.findall(".//object")}
    component_ids = {
        wrapper_id for wrapper_id, wrapper in wrappers.items()
        if wrapper.get("petakerjaKey", "").startswith("modules/")
        and wrapper.find("mxCell") is not None
        and wrapper.find("mxCell").get("vertex") == "1"
    }
    expected_structural = {
        "modules-application-root", "modules-module-core", "modules-module-jobs",
        "modules-module-account", "modules-module-analysis",
    }
    if len(component_ids) != 12:
        errors.append(f"polished Module Hierarchy must retain 12 interactive responsibilities, found {len(component_ids)}")
    if not expected_structural.issubset(wrappers):
        errors.append("polished Module Hierarchy is missing its root or four module parents")
    if any(identifier.startswith("modules-group-") for identifier in wrappers):
        errors.append("polished Module Hierarchy still contains the old quadrant containers")

    hierarchy_edges = []
    for wrapper in wrappers.values():
        cell = wrapper.find("mxCell")
        if cell is not None and cell.get("edge") == "1" and wrapper.get("petakerjaRelation") == "structural":
            hierarchy_edges.append((wrapper, cell))
    if len(hierarchy_edges) != 16:
        errors.append(f"polished Module Hierarchy must contain 16 structural connectors, found {len(hierarchy_edges)}")
    incoming = {identifier: 0 for identifier in component_ids}
    for wrapper, cell in hierarchy_edges:
        if "endArrow=none" not in cell.get("style", ""):
            errors.append(f"{wrapper.get('id')} must be an arrow-free hierarchy connector")
        if cell.get("target") in incoming:
            incoming[cell.get("target")] += 1
        source = cell.get("source", "").replace("modules-module-", "modules-")
        target = cell.get("target", "")
        if not cell.get("source", "").endswith("application-root"):
            source_branch = source.removeprefix("modules-").split("-", 1)[0]
            target_branch = target.removeprefix("modules-").split("-", 1)[0]
            if source_branch != target_branch:
                errors.append(f"{wrapper.get('id')} crosses module branches")
    if any(count != 1 for count in incoming.values()):
        errors.append(f"each module responsibility must have one visible parent path: {incoming}")

    dependency_cards = [identifier for identifier in wrappers if re.fullmatch(r"modules-dependency-[1-4]", identifier)]
    if "modules-dependency-panel" not in wrappers or "modules-dependency-title" not in wrappers or len(dependency_cards) != 4:
        errors.append("polished Module Hierarchy must contain the bordered four-row dependency panel")


def assert_module_assets(errors: list[str]) -> None:
    source = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    prefix = "window.PETAKERJA_DIAGRAM_ASSETS="
    payload = source.split("\n", 1)[1]
    if not payload.startswith(prefix) or not payload.endswith(";\n"):
        errors.append("diagram-assets.js has an unexpected generated wrapper")
        return
    assets = json.loads(payload[len(prefix):-2])
    module_connections = assets.get("modules", {}).get("connections", [])
    expected_ids = {
        "modules-semantic-core-jobs", "modules-semantic-core-analysis",
        "modules-semantic-account-jobs", "modules-semantic-account-analysis",
    }
    actual_ids = {connection.get("id") for connection in module_connections}
    if actual_ids != expected_ids:
        errors.append(f"polished Module Hierarchy semantic dependencies drifted: {sorted(actual_ids)}")
    if any(connection.get("visual") is not False for connection in module_connections):
        errors.append("module semantic dependencies must remain non-crossing, nonvisual registry entries")
    for diagram_id, bm_title, en_title in (
        ("architecture", "Seni Bina Berlapis PetaKerja", "PetaKerja Layered Architecture"),
        ("architecture-original", "Seni Bina Berlapis PetaKerja", "PetaKerja Layered Architecture"),
        ("modules", "Hierarki Modul PetaKerja", "PetaKerja Module Hierarchy"),
        ("modules-original", "Hierarki Modul PetaKerja", "PetaKerja Module Hierarchy"),
    ):
        svg = assets.get(diagram_id, {}).get("svg", {})
        if bm_title not in svg.get("ms", "") or en_title not in svg.get("en", "") or svg.get("ms") == svg.get("en"):
            errors.append(f"{diagram_id} does not contain distinct BM and English SVG assets")


def main() -> int:
    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    diagrams = manifest.get("diagrams", {})
    errors: list[str] = []
    if len(diagrams) != EXPECTED_DIAGRAMS:
        errors.append(f"expected {EXPECTED_DIAGRAMS} registered diagrams, found {len(diagrams)}")

    parsed_sources: dict[Path, ET.Element] = {}
    checked_pages: set[tuple[Path, str]] = set()
    structure_pages: list[tuple[str, ET.Element]] = []
    translated_pages = 0
    labelled_elements = 0
    sequence_messages = 0

    for diagram_id, entry in diagrams.items():
        source = ROOT / entry["xml"]
        page_id = entry["pageId"]
        if source not in parsed_sources:
            parsed_sources[source] = ET.parse(source).getroot()
        root = parsed_sources[source]
        page = next((item for item in root.findall("diagram") if item.get("id") == page_id), None)
        if page is None:
            errors.append(f"{diagram_id}: missing page {page_id!r} in {source.name}")
            continue
        page_key = (source, page_id)
        if page_key in checked_pages:
            continue
        checked_pages.add(page_key)
        structure_pages.append((f"{source.name}:{page_id}", page))

        page_has_translation = False
        for element, visible_attribute in visible_elements(page):
            labelled_elements += 1
            element_id = element.get("petakerjaKey") or element.get("id") or "unidentified"
            label_en = element.get("labelEn")
            label_ms = element.get("labelMs")
            if not label_en or not label_ms:
                errors.append(f"{source.name}:{page_id}:{element_id} is missing labelEn or labelMs")
                continue
            if label_en != label_ms:
                page_has_translation = True
            elif source in DESIGN_SOURCES and clean_label(label_en) not in TECHNICAL_DESIGN_LABELS:
                errors.append(
                    f"{source.name}:{page_id}:{element_id} has untranslated design text: {clean_label(label_en)!r}"
                )
            if element.tag == "object" and "/message-" in element.get("petakerjaKey", ""):
                sequence_messages += 1
                for attribute in ("simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs"):
                    if not element.get(attribute):
                        errors.append(f"{source.name}:{element_id} is missing {attribute}")
            canonical = element.get("simpleLabelEn") or label_en
            if element.get(visible_attribute) != canonical:
                errors.append(f"{source.name}:{element_id} is not stored in canonical English projection")
        if page_has_translation:
            translated_pages += 1
        else:
            errors.append(f"{source.name}:{page_id} has no distinct BM translation")

    if len(parsed_sources) != EXPECTED_SOURCES:
        errors.append(f"expected {EXPECTED_SOURCES} editor sources, found {len(parsed_sources)}")
    if len(checked_pages) != EXPECTED_DIAGRAMS:
        errors.append(f"expected {EXPECTED_DIAGRAMS} unique registered pages, found {len(checked_pages)}")

    assert_polished_module_hierarchy(errors)
    assert_module_assets(errors)

    original_page = ET.parse(ORIGINAL_MODULE_HIERARCHY).getroot().find("diagram")
    if original_page is None:
        errors.append("original Module Hierarchy is missing its Draw.io page")
    else:
        original_payload = json.dumps(
            structural_node(original_page), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        original_structure = hashlib.sha256(original_payload).hexdigest()
        if original_structure != ORIGINAL_MODULE_STRUCTURE:
            errors.append(f"original Module Hierarchy geometry changed ({original_structure})")

    reviewed_root = ET.parse(REVIEWED_MAP_FLOWCHART).getroot()
    reviewed_page = reviewed_root.find("diagram")
    reviewed_model = reviewed_page.find("mxGraphModel") if reviewed_page is not None else None
    reviewed_wrappers = reviewed_page.findall(".//object") if reviewed_page is not None else []
    reviewed_vertices = []
    reviewed_edges = []
    max_bottom = 0.0
    for wrapper in reviewed_wrappers:
        cell = wrapper.find("mxCell")
        if cell is None:
            continue
        if cell.get("vertex") == "1" and wrapper.get("petakerjaKey", "").startswith(
            "user-explore-3d-map-flowchart/"
        ):
            reviewed_vertices.append(wrapper)
            geometry = cell.find("mxGeometry")
            if geometry is not None:
                max_bottom = max(
                    max_bottom,
                    float(geometry.get("y", "0")) + float(geometry.get("height", "0")),
                )
        elif cell.get("edge") == "1":
            reviewed_edges.append(wrapper)
    if reviewed_page is None or reviewed_page.get("id") != "petakerja_flow_user_explore_3d_map":
        errors.append("reviewed Explore the 3D Map flow chart has the wrong page id")
    if reviewed_model is None or (
        reviewed_model.get("pageWidth"), reviewed_model.get("pageHeight")
    ) != ("1100", "1500"):
        errors.append("reviewed Explore the 3D Map flow chart must retain its 1100x1500 first page")
    if len(reviewed_vertices) != 21 or len(reviewed_edges) != 24:
        errors.append(
            "reviewed Explore the 3D Map flow chart must retain 21 components and 24 connectors"
        )
    if max_bottom != 1660.0:
        errors.append(
            f"reviewed Explore the 3D Map flow chart multi-page bottom drifted ({max_bottom})"
        )

    actual_structure = page_structure_hash(structure_pages)
    if actual_structure != EXPECTED_STRUCTURE:
        errors.append(f"diagram geometry/style/endpoint structure changed ({actual_structure})")

    editor_source = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    for marker in (
        "function bilingualElements(documentNode)",
        "function localizedLabelPairs(xml)",
        "cell.parentElement?.tagName !== 'object'",
        "function visibleLabelAttribute(element)",
        "element.tagName === 'mxCell' ? 'value' : 'label'",
        "connection.visual !== false",
    ):
        if marker not in editor_source:
            errors.append(f"editor-core.js is missing raw mxCell localization marker: {marker}")

    app_source = (ROOT / "app.js").read_text(encoding="utf-8")
    for marker in (
        "editorAPI?.localizedLabelPairs?.(analysis?.xml || '')",
        "translateRuntimeSvg(svg, diagramType, 'ms', localizedPairs)",
        "connection.visual !== false && !presentCellIds.has(connection.id)",
    ):
        if marker not in app_source:
            errors.append(f"app.js is missing metadata-driven runtime localization marker: {marker}")

    if errors:
        print("Bilingual all-diagram checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Bilingual all-diagram checks passed for "
        f"{len(diagrams)} diagrams, {len(parsed_sources)} sources, "
        f"{labelled_elements} labels and {sequence_messages} sequence messages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
