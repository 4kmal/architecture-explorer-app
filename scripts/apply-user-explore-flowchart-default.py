#!/usr/bin/env python3
"""Adopt and validate the reviewed Explore the 3D Map flow-chart layout.

The Explorer's editable polished source is the canonical layout.  The reviewed
diagram intentionally keeps its 1100 x 1500 page while allowing the final
interaction and End node to continue below the first page boundary.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "editor" / "flowchart-user-explore-3d-map.drawio"
PAGE_ID = "petakerja_flow_user_explore_3d_map"
DIAGRAM_ID = "user-explore-3d-map-flowchart"
PAGE_SIZE = (1100.0, 1500.0)
EXPECTED_COMPONENTS = 21
EXPECTED_CONNECTORS = 24
EXPECTED_END_GEOMETRY = (517.0, 1620.0, 66.67, 40.0)


def geometry(cell: ET.Element) -> tuple[float, float, float, float]:
    node = cell.find("mxGeometry")
    if node is None:
        raise RuntimeError(f"{cell.get('id', 'unidentified')} has no geometry")
    return tuple(float(node.get(name, "0")) for name in ("x", "y", "width", "height"))


def validate(root: ET.Element) -> tuple[ET.Element, float]:
    diagrams = root.findall("diagram")
    if len(diagrams) != 1 or diagrams[0].get("id") != PAGE_ID:
        raise RuntimeError(f"Expected one Draw.io page with id {PAGE_ID}")
    diagram = diagrams[0]
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("Flow chart has no mxGraphModel")
    page_size = (float(model.get("pageWidth", "0")), float(model.get("pageHeight", "0")))
    if page_size != PAGE_SIZE:
        raise RuntimeError(f"Reviewed flow chart must retain page size {PAGE_SIZE}, got {page_size}")

    wrappers = diagram.findall(".//object")
    identifiers = [wrapper.get("id", "") for wrapper in wrappers]
    if any(not identifier for identifier in identifiers) or len(identifiers) != len(set(identifiers)):
        raise RuntimeError("Flow chart has missing or duplicate object ids")
    stable_keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers if wrapper.get("petakerjaKey")]
    duplicates = [key for key, count in Counter(stable_keys).items() if count > 1]
    if duplicates:
        raise RuntimeError(f"Flow chart has duplicate stable keys: {duplicates}")

    prefix = f"{DIAGRAM_ID}/"
    components: dict[str, str] = {}
    connectors: list[ET.Element] = []
    max_bottom = 0.0
    end_geometry: tuple[float, float, float, float] | None = None
    for wrapper in wrappers:
        cell = wrapper.find("mxCell")
        if cell is None:
            raise RuntimeError(f"{wrapper.get('id')} has no mxCell")
        key = wrapper.get("petakerjaKey", "")
        if cell.get("vertex") == "1" and key.startswith(prefix):
            rectangle = geometry(cell)
            components[wrapper.get("id", "")] = key[len(prefix):]
            max_bottom = max(max_bottom, rectangle[1] + rectangle[3])
            if key == f"{prefix}end":
                end_geometry = rectangle
        elif cell.get("edge") == "1":
            connectors.append(wrapper)

    if len(components) != EXPECTED_COMPONENTS:
        raise RuntimeError(f"Expected {EXPECTED_COMPONENTS} components, found {len(components)}")
    if len(connectors) != EXPECTED_CONNECTORS:
        raise RuntimeError(f"Expected {EXPECTED_CONNECTORS} connectors, found {len(connectors)}")
    if end_geometry != EXPECTED_END_GEOMETRY:
        raise RuntimeError(f"Reviewed End geometry drifted: {end_geometry}")
    if max_bottom <= PAGE_SIZE[1]:
        raise RuntimeError("Reviewed layout must intentionally extend below the first page")

    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in connectors:
        cell = wrapper.find("mxCell")
        if cell is None:
            continue
        source, target = cell.get("source", ""), cell.get("target", "")
        if source not in components or target not in components:
            raise RuntimeError(f"Detached connector: {wrapper.get('petakerjaKey')}")
        outgoing[source].append(target)
        incoming[target].append(source)

    by_key = {key: identifier for identifier, key in components.items()}
    for origin, adjacency, expected in (
        (by_key["start"], outgoing, set(components)),
        (by_key["end"], incoming, set(components)),
    ):
        reached: set[str] = set()
        queue = deque([origin])
        while queue:
            current = queue.popleft()
            if current in reached:
                continue
            reached.add(current)
            queue.extend(adjacency[current])
        if reached != expected:
            missing = sorted(components[item] for item in expected - reached)
            raise RuntimeError(f"Flow chart has disconnected components: {missing}")
    return diagram, max_bottom


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--adopt",
        type=Path,
        help="Reviewed Draw.io source to promote as the polished Explorer default",
    )
    args = parser.parse_args()
    source = args.adopt.resolve() if args.adopt else DEFAULT_SOURCE
    if not source.exists():
        raise FileNotFoundError(source)

    tree = ET.parse(source)
    root = tree.getroot()
    diagram, max_bottom = validate(root)
    diagram.set("petakerjaRevision", "2026-07-20-reviewed-overflow-v2")

    if args.adopt:
        ET.indent(tree, space="  ")
        DEFAULT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
        tree.write(DEFAULT_SOURCE, encoding="utf-8", xml_declaration=True)
        validate(ET.parse(DEFAULT_SOURCE).getroot())

    print(
        "Validated Explore the 3D Map default: "
        f"{EXPECTED_COMPONENTS} components, {EXPECTED_CONNECTORS} connectors, "
        f"content bottom {max_bottom:g}px on a {PAGE_SIZE[1]:g}px first page"
    )


if __name__ == "__main__":
    main()
