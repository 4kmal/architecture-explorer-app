#!/usr/bin/env python3
"""Adopt and apply the canonical Core Domain class-diagram layout.

The tracked Class Diagram Template is the reusable geometry and sizing
authority.  Passing ``--adopt`` imports a reviewed Draw.io adjustment into the
template before applying the report-readable class typography.  Running the
script without ``--adopt`` reapplies the tracked template to the Explorer's
default editable Core Domain source.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "Class Diagram Template.drawio"
DEFAULT_SOURCE = ROOT / "assets" / "editor" / "class-domain-petakerja.drawio"

CLASS_TITLE_FONT_SIZE = "16"
CLASS_STEREOTYPE_FONT_SIZE = "12"
CLASS_MEMBER_FONT_SIZE = "14"
EXPECTED_CLASS_KEYS = {
    "domain/auth-identity",
    "domain/user-profile",
    "domain/state-entity",
    "domain/data-source-entity",
    "domain/poi-group-entity",
    "domain/poi-category-entity",
    "domain/poi-entity",
    "domain/highlight-entity",
    "domain/open-data-api",
    "domain/job-entity",
    "domain/job-state-entity",
    "domain/ai-credential-entity",
    "domain/ai-preference-entity",
    "domain/ai-usage-entity",
    "domain/audit-log-entity",
}


def set_style_property(style: str, name: str, value: str) -> str:
    pattern = re.compile(rf"(?:(?<=;)|^){re.escape(name)}=[^;]*")
    if pattern.search(style):
        return pattern.sub(f"{name}={value}", style)
    separator = "" if not style or style.endswith(";") else ";"
    return f"{style}{separator}{name}={value};"


def set_stereotype_size(value: str) -> str:
    return re.sub(
        r"font-size:\s*\d+(?:\.\d+)?px",
        f"font-size:{CLASS_STEREOTYPE_FONT_SIZE}px",
        value,
        count=1,
    )


def validate_page(root: ET.Element) -> tuple[ET.Element, list[ET.Element]]:
    diagram = root.find("diagram")
    if diagram is None or diagram.get("id") != "petakerja_domain":
        raise RuntimeError("Expected the petakerja_domain Draw.io page")
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("Class diagram has no mxGraphModel")
    if (model.get("pageWidth"), model.get("pageHeight")) != ("2650", "2860"):
        raise RuntimeError("Class diagram must retain the 2650 x 2860 report canvas")
    classes = [
        cell for cell in root.findall(".//mxCell")
        if cell.get("petakerjaKey") in EXPECTED_CLASS_KEYS
    ]
    actual_keys = {cell.get("petakerjaKey", "") for cell in classes}
    if actual_keys != EXPECTED_CLASS_KEYS:
        missing = sorted(EXPECTED_CLASS_KEYS - actual_keys)
        extra = sorted(actual_keys - EXPECTED_CLASS_KEYS)
        raise RuntimeError(f"Unexpected class components; missing={missing}, extra={extra}")
    for cell in classes:
        if not cell.get("style", "").startswith("swimlane;"):
            raise RuntimeError(f"{cell.get('petakerjaKey')} is not a UML swimlane class")
        geometry = cell.find("mxGeometry")
        if geometry is None or not geometry.get("width") or not geometry.get("height"):
            raise RuntimeError(f"{cell.get('petakerjaKey')} has no class geometry")
    return diagram, classes


def apply_typography(root: ET.Element) -> None:
    diagram, classes = validate_page(root)
    diagram.set("petakerjaRevision", "2026-07-20-supervisor-readable-v2")
    root.set("petakerjaProjectionLanguage", "ms")
    class_ids = {cell.get("id", "") for cell in classes}
    for cell in classes:
        cell.set(
            "style",
            set_style_property(cell.get("style", ""), "fontSize", CLASS_TITLE_FONT_SIZE),
        )
        for attribute in ("value", "labelEn", "labelMs"):
            if cell.get(attribute):
                cell.set(attribute, set_stereotype_size(cell.get(attribute, "")))

    for cell in root.findall(".//mxCell"):
        if cell.get("parent") not in class_ids or cell.get("vertex") != "1":
            continue
        style = cell.get("style", "")
        if style.startswith("text;"):
            cell.set("style", set_style_property(style, "fontSize", CLASS_MEMBER_FONT_SIZE))


def validate_typography(root: ET.Element) -> None:
    _diagram, classes = validate_page(root)
    class_ids = {cell.get("id", "") for cell in classes}
    for cell in classes:
        style = cell.get("style", "")
        if f"fontSize={CLASS_TITLE_FONT_SIZE}" not in style:
            raise RuntimeError(f"{cell.get('petakerjaKey')} title font is not report-readable")
        if f"font-size:{CLASS_STEREOTYPE_FONT_SIZE}px" not in cell.get("value", ""):
            raise RuntimeError(f"{cell.get('petakerjaKey')} stereotype font is not report-readable")
    members = [
        cell for cell in root.findall(".//mxCell")
        if cell.get("parent") in class_ids
        and cell.get("vertex") == "1"
        and cell.get("style", "").startswith("text;")
    ]
    if not members:
        raise RuntimeError("Class diagram has no member compartments")
    for cell in members:
        if f"fontSize={CLASS_MEMBER_FONT_SIZE}" not in cell.get("style", ""):
            raise RuntimeError(f"Class member {cell.get('id')} font is not report-readable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--adopt",
        type=Path,
        help="Reviewed Draw.io layout to promote into the canonical class template",
    )
    args = parser.parse_args()
    source = args.adopt.resolve() if args.adopt else TEMPLATE
    if not source.exists():
        raise FileNotFoundError(source)

    tree = ET.parse(source)
    root = tree.getroot()
    apply_typography(root)
    validate_typography(root)
    ET.indent(tree, space="  ")
    payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE.write_bytes(payload)
    DEFAULT_SOURCE.write_bytes(payload)
    print(
        "Applied class default: "
        f"15 classes, title {CLASS_TITLE_FONT_SIZE}px, "
        f"stereotype {CLASS_STEREOTYPE_FONT_SIZE}px, members {CLASS_MEMBER_FONT_SIZE}px"
    )


if __name__ == "__main__":
    main()
