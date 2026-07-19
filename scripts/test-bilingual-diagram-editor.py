#!/usr/bin/env python3
"""Regression checks for native BM/EN editing across every registered diagram."""

from __future__ import annotations

import hashlib
import json
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
EXPECTED_DIAGRAMS = 51
EXPECTED_SOURCES = 50
EXPECTED_STRUCTURE = "92f1f9f1d49ac4dbc9089cd8f60048d1b1d6898cdf16c739d86a376393ed832a"


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

    actual_structure = page_structure_hash(structure_pages)
    if actual_structure != EXPECTED_STRUCTURE:
        errors.append(f"diagram geometry/style/endpoint structure changed ({actual_structure})")

    editor_source = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    for marker in (
        "function bilingualElements(documentNode)",
        "cell.parentElement?.tagName !== 'object'",
        "function visibleLabelAttribute(element)",
        "element.tagName === 'mxCell' ? 'value' : 'label'",
    ):
        if marker not in editor_source:
            errors.append(f"editor-core.js is missing raw mxCell localization marker: {marker}")

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
