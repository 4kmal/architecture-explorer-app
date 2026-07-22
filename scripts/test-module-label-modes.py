#!/usr/bin/env python3
"""Focused regression checks for the layered module view and generic labels."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "assets" / "editor" / "module-hierarchy-layered-stack.drawio"
ORIGINALS = (
    ROOT / "assets" / "editor" / "architecture-layered-original.drawio",
    ROOT / "assets" / "editor" / "module-hierarchy-original.drawio",
)
CURRENT = {
    "architecture": ROOT / "assets" / "editor" / "architecture-layered.drawio",
    "modules": ROOT / "assets" / "editor" / "module-hierarchy.drawio",
    "modules-layered-stack": STACK,
    "map-routing-responsibility-stack": ROOT / "assets" / "editor" / "petakerja-map-routing-responsibility-stack.drawio",
}


def mode_elements(path: Path) -> list[ET.Element]:
    return [
        element for element in ET.parse(path).getroot().findall(".//object")
        if element.get("simpleLabelEn") or element.get("codeLabelEn")
    ]


def main() -> int:
    errors: list[str] = []
    root = ET.parse(STACK).getroot()
    page = root.find("diagram")
    model = page.find("mxGraphModel") if page is not None else None
    wrappers = page.findall(".//object") if page is not None else []
    if page is None or page.get("id") != "petakerja_module_hierarchy_layered_stack":
        errors.append("layered Module Hierarchy page id drifted")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1900", "1180"):
        errors.append("layered Module Hierarchy canvas must remain 1900x1180")
    layer_ids = {item.get("id") for item in wrappers if "shape=trapezoid" in (item.find("mxCell").get("style", "") if item.find("mxCell") is not None else "")}
    if layer_ids != {"layer-product", "layer-modules", "layer-coordinators", "layer-capabilities"}:
        errors.append(f"layered Module Hierarchy tiers drifted: {sorted(layer_ids)}")
    mapped = [item for item in wrappers if item.get("petakerjaKey", "").startswith("modules/")]
    structural = [item for item in wrappers if item.get("petakerjaRelation") == "structural"]
    if len(mapped) != 12 or len(structural) != 16:
        errors.append(f"expected 12 mapped responsibilities and 16 hierarchy edges, found {len(mapped)} and {len(structural)}")
    if len([item for item in wrappers if item.get("id", "").startswith("modules-layered-stack-dependency-")]) != 4:
        errors.append("layered Module Hierarchy must retain four cross-module dependency cards")
    xml = STACK.read_text(encoding="utf-8")
    if "gradientColor" in xml or "data:image" in xml or re.search(r"https?://", xml):
        errors.append("layered Module Hierarchy contains a gradient or image dependency")

    for diagram_id, path in CURRENT.items():
        elements = mode_elements(path)
        if not elements:
            errors.append(f"{diagram_id} has no Simple/Code metadata")
            continue
        for element in elements:
            values = [element.get(name) for name in ("simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs")]
            if not all(values):
                errors.append(f"{diagram_id}:{element.get('id')} has incomplete bilingual label metadata")
            if values[0] == values[2]:
                errors.append(f"{diagram_id}:{element.get('id')} does not visibly distinguish Simple and Code")
    for path in ORIGINALS:
        if mode_elements(path):
            errors.append(f"{path.name} must remain an unchanged reference without label modes")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    entry = manifest.get("diagrams", {}).get("modules-layered-stack", {})
    if entry.get("pageId") != "petakerja_module_hierarchy_layered_stack" or entry.get("diagramType") != "module-hierarchy":
        errors.append("workspace manifest is missing the layered Module Hierarchy registration")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    expected_nav = (
        "variantKind: 'layered-stack', variantOrder: 1, variantRecommended: true",
        "variantLabelEn: 'Layered Stack', variantLabelMs: 'Susunan Bertingkat'",
        "variantKind: 'tree', variantOrder: 2",
        "variantKind: 'original', variantOrder: 3",
    )
    for needle in expected_nav:
        if needle not in architecture:
            errors.append(f"navigation registration is missing {needle!r}")

    app = (ROOT / "app.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    required_runtime = (
        "petakerja-explorer-diagram-label-mode",
        "petakerja-explorer-sequence-label-mode",
        "supportsLabelModes",
        "applyDiagramLabels",
        "setDiagramLabelMode",
        "data-diagram-label-mode",
        "petakerjaDiagramLabelMode",
        "petakerjaSequenceLabelMode",
    )
    combined = app + editor + index
    for needle in required_runtime:
        if needle not in combined:
            errors.append(f"generic label-mode runtime is missing {needle!r}")
    if "removeAttribute(LEGACY_PROJECTION_LABEL_MODE_ATTR)" not in editor:
        errors.append("legacy Draw.io label metadata is not removed from new projections")
    if 'id="sequence-label-control"' in index or "data-sequence-label-mode" in index:
        errors.append("the header still exposes the sequence-only label control")

    assets = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    if '"modules-layered-stack"' not in assets or '"supportsLabelModes":true' not in assets:
        errors.append("generated asset bundle is missing the layered diagram or label-mode capability")
    else:
        asset_payload = assets.partition("window.PETAKERJA_DIAGRAM_ASSETS=")[2].rstrip().removesuffix(";")
        stack_asset = json.loads(asset_payload).get("modules-layered-stack", {})
        component_keys = {item.get("componentKey") for item in stack_asset.get("components", [])}
        if component_keys != {item.get("petakerjaKey", "").removeprefix("modules/") for item in mapped}:
            errors.append("generated layered diagram is missing its twelve implementation mappings")
        if len(stack_asset.get("connections", [])) != 4:
            errors.append("generated layered diagram is missing its four dependency mappings")
        if len(stack_asset.get("labelElements", [])) != 12:
            errors.append("generated layered diagram is missing its twelve label projections")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Layered Module Hierarchy and generic label-mode checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
