#!/usr/bin/env python3
"""Normalize the user-reorganized PetaKerja Google sign-in flow chart.

The reorganized Draw.io document is the authoritative layout input and is
never modified. This script repairs its stable metadata and connector model,
writes the canonical report source, copies that source into the Explorer, and
exports the report SVG and PNG through Draw.io Desktop.
"""

from __future__ import annotations

import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from pathlib import Path
from paths import DIAGRAMS, DRAWIO, EDITOR

REORGANIZED_SOURCE = EDITOR / "flowchart-user-google-sign-in-original.drawio"
OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google.drawio"
BACKUP = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google - Before Reorganized Layout.drawio"
SVG_OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google.svg"
PNG_OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google.png"

EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "flowchart-user-google-sign-in.drawio"

PAGE_ID = "petakerja_flow_google_sign_in"
ROOT_ID = "google-sign-in-flow-root"
LAYER_ID = "google-sign-in-flow-layer"
KEY_PREFIX = "user-google-sign-in-flowchart/"
PAGE_WIDTH = 980
PAGE_HEIGHT = 1540

FLOW_COMPONENTS = {
    "start",
    "select-sign-in",
    "show-google-prompt",
    "select-google",
    "start-google-oauth",
    "authorization-completed",
    "display-auth-error",
    "guest-state",
    "save-auth-session",
    "redirect-petakerja",
    "check-active-session",
    "active-session-found",
    "request-profile",
    "linked-profile-found",
    "load-linked-profile",
    "matching-email-found",
    "link-existing-profile",
    "create-new-profile",
    "profile-obtained",
    "return-profile",
    "update-user-state",
    "display-authenticated-menu",
    "end",
}

DECISION_COMPONENTS = {
    "authorization-completed",
    "active-session-found",
    "linked-profile-found",
    "matching-email-found",
    "profile-obtained",
}

CANONICAL_OBJECTS = {
    "Active session found?": (
        "google-sign-in-flow-active-session-found",
        "active-session-found",
    ),
    "Linked profile found?": (
        "google-sign-in-flow-linked-profile-found",
        "linked-profile-found",
    ),
    "Create a new PetaKerja profile": (
        "google-sign-in-flow-create-new-profile",
        "create-new-profile",
    ),
}


def set_style_value(style: str, name: str, value: str) -> str:
    parts = [part for part in style.split(";") if part and not part.startswith(f"{name}=")]
    parts.append(f"{name}={value}")
    return ";".join(parts) + ";"


def wrapper_by_label(root: ET.Element, label: str) -> ET.Element:
    matches = [wrapper for wrapper in root.findall(".//object") if wrapper.get("label") == label]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one object labelled {label!r}, found {len(matches)}")
    return matches[0]


def rename_wrapper(root: ET.Element, wrapper: ET.Element, new_id: str, stable_suffix: str) -> None:
    old_id = wrapper.get("id")
    if not old_id:
        raise RuntimeError(f"Object {wrapper.get('label')!r} has no ID")
    if old_id != new_id and any(item.get("id") == new_id for item in root.findall(".//object")):
        raise RuntimeError(f"Cannot normalize {old_id!r}; target ID {new_id!r} already exists")
    wrapper.set("id", new_id)
    wrapper.set("petakerjaKey", KEY_PREFIX + stable_suffix)
    for cell in root.findall(".//mxCell"):
        if cell.get("source") == old_id:
            cell.set("source", new_id)
        if cell.get("target") == old_id:
            cell.set("target", new_id)


def add_page_background(model_root: ET.Element) -> None:
    existing = next(
        (
            wrapper
            for wrapper in model_root.findall("object")
            if wrapper.get("petakerjaKey") == KEY_PREFIX + "page-background"
        ),
        None,
    )
    if existing is None:
        existing = ET.Element(
            "object",
            {
                "id": "google-sign-in-flow-page-background",
                "label": "",
                "petakerjaKey": KEY_PREFIX + "page-background",
            },
        )
        cell = ET.SubElement(
            existing,
            "mxCell",
            {
                "parent": LAYER_ID,
                "vertex": "1",
                "style": (
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;"
                    "strokeColor=none;pointerEvents=0;locked=1;"
                ),
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "as": "geometry",
                "x": "0",
                "y": "0",
                "width": str(PAGE_WIDTH),
                "height": str(PAGE_HEIGHT),
            },
        )
        model_root.insert(2, existing)
    else:
        geometry = existing.find("mxCell/mxGeometry")
        if geometry is None:
            raise RuntimeError("Page background is missing its geometry")
        geometry.set("x", "0")
        geometry.set("y", "0")
        geometry.set("width", str(PAGE_WIDTH))
        geometry.set("height", str(PAGE_HEIGHT))


def build() -> ET.ElementTree:
    tree = ET.parse(REORGANIZED_SOURCE)
    root = tree.getroot()
    diagram = root.find("diagram")
    if diagram is None:
        raise RuntimeError("The reorganized source has no Draw.io page")
    diagram.set("id", PAGE_ID)
    diagram.set("name", "PetaKerja Google Sign-In")

    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("The reorganized source has no mxGraphModel")
    model.set("dx", str(PAGE_WIDTH))
    model.set("dy", str(PAGE_HEIGHT))
    model.set("pageWidth", str(PAGE_WIDTH))
    model.set("pageHeight", str(PAGE_HEIGHT))
    model.set("page", "1")

    model_root = model.find("root")
    if model_root is None:
        raise RuntimeError("The reorganized source has no model root")

    add_page_background(model_root)

    for label, (new_id, stable_suffix) in CANONICAL_OBJECTS.items():
        rename_wrapper(root, wrapper_by_label(root, label), new_id, stable_suffix)

    guest = wrapper_by_label(root, "Clear local user state and display guest sign-in")
    guest.set("label", "Remain in guest state and display Sign in")
    guest.set("petakerjaKey", KEY_PREFIX + "guest-state")

    session_yes = next(
        (
            wrapper
            for wrapper in root.findall(".//object")
            if wrapper.get("petakerjaKey") == KEY_PREFIX + "session-yes"
        ),
        None,
    )
    if session_yes is None or session_yes.find("mxCell") is None:
        raise RuntimeError("The Active session Yes branch could not be found")
    session_yes.find("mxCell").set("source", "google-sign-in-flow-active-session-found")

    link_result = next(
        (
            wrapper
            for wrapper in root.findall(".//object")
            if wrapper.get("petakerjaKey") == KEY_PREFIX + "link-to-profile-result"
        ),
        None,
    )
    if link_result is None or link_result.find("mxCell") is None:
        raise RuntimeError("The existing-profile merge connector could not be found")
    link_cell = link_result.find("mxCell")
    link_cell.set("style", set_style_value(link_cell.get("style", ""), "endArrow", "classic"))
    link_cell.set("style", set_style_value(link_cell.get("style", ""), "endFill", "1"))

    guest_to_end = next(
        (
            wrapper
            for wrapper in root.findall(".//object")
            if wrapper.get("petakerjaKey") == KEY_PREFIX + "guest-to-end"
        ),
        None,
    )
    if guest_to_end is None or guest_to_end.find("mxCell") is None:
        raise RuntimeError("The guest-state End connector could not be found")
    # Keep the reorganized route, but move its outer vertical segment inside
    # the corrected 980px page so the report export cannot clip it.
    for point in guest_to_end.find("mxCell").findall(".//mxPoint"):
        if point.get("x") == "1020":
            point.set("x", "960")

    return tree


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def component_suffix(wrapper: ET.Element) -> str | None:
    stable_key = wrapper.get("petakerjaKey", "")
    return stable_key[len(KEY_PREFIX):] if stable_key.startswith(KEY_PREFIX) else None


def validate(path: Path) -> None:
    parsed = ET.parse(path).getroot()
    diagram = parsed.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise RuntimeError("Generated flow chart has the wrong page ID")
    model = diagram.find("mxGraphModel")
    if model is None or model.get("pageWidth") != str(PAGE_WIDTH) or model.get("pageHeight") != str(PAGE_HEIGHT):
        raise RuntimeError("Generated flow chart has the wrong page dimensions")

    wrappers = parsed.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    object_ids = [wrapper.get("id", "") for wrapper in wrappers]
    if len(wrappers) != 53:
        raise RuntimeError(f"Expected 53 keyed objects, found {len(wrappers)}")
    if any(not key for key in keys):
        raise RuntimeError("Generated flow chart contains an object without a petakerjaKey")
    if any(count > 1 for count in Counter(keys).values()):
        raise RuntimeError("Generated flow chart contains duplicate stable keys")
    if any(not object_id for object_id in object_ids) or len(object_ids) != len(set(object_ids)):
        raise RuntimeError("Generated flow chart contains missing or duplicate IDs")

    vertices: dict[str, ET.Element] = {}
    edges: list[ET.Element] = []
    for wrapper in wrappers:
        cell = wrapper.find("mxCell")
        if cell is None:
            raise RuntimeError(f"Object {wrapper.get('id')} has no mxCell")
        if cell.get("vertex") == "1":
            vertices[wrapper.get("id", "")] = wrapper
            geometry = cell.find("mxGeometry")
            if geometry is None:
                raise RuntimeError(f"Vertex {wrapper.get('id')} has no geometry")
            x = float(geometry.get("x", "0"))
            y = float(geometry.get("y", "0"))
            width = float(geometry.get("width", "0"))
            height = float(geometry.get("height", "0"))
            if min(x, y) < 0 or x + width > PAGE_WIDTH or y + height > PAGE_HEIGHT:
                raise RuntimeError(f"Vertex {wrapper.get('id')} overflows the {PAGE_WIDTH}x{PAGE_HEIGHT} page")
        elif cell.get("edge") == "1":
            edges.append(wrapper)

    if len(vertices) != 26 or len(edges) != 27:
        raise RuntimeError(f"Expected 26 vertices and 27 connectors, found {len(vertices)} and {len(edges)}")

    flow_by_id = {
        object_id: component_suffix(wrapper)
        for object_id, wrapper in vertices.items()
        if component_suffix(wrapper) in FLOW_COMPONENTS
    }
    if set(flow_by_id.values()) != FLOW_COMPONENTS:
        missing = sorted(FLOW_COMPONENTS - set(flow_by_id.values()))
        raise RuntimeError(f"Generated flow chart is missing canonical flow components: {missing}")

    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in edges:
        cell = wrapper.find("mxCell")
        source = cell.get("source", "")
        target = cell.get("target", "")
        if source not in flow_by_id or target not in flow_by_id:
            raise RuntimeError(f"Connector {wrapper.get('id')} has a missing or non-flow endpoint")
        if "endArrow=classic" not in cell.get("style", ""):
            raise RuntimeError(f"Connector {wrapper.get('id')} does not use the classic flow arrow")
        label = wrapper.get("label", "")
        outgoing[source].append((target, label))
        incoming[target].append(source)
        for point in cell.findall(".//mxPoint"):
            if point.get("x") is None or point.get("y") is None:
                continue
            x = float(point.get("x", "0"))
            y = float(point.get("y", "0"))
            if x < 0 or y < 0 or x > PAGE_WIDTH or y > PAGE_HEIGHT:
                raise RuntimeError(f"Connector {wrapper.get('id')} contains a point outside the page")

    suffix_to_id = {suffix: object_id for object_id, suffix in flow_by_id.items()}
    for suffix in DECISION_COMPONENTS:
        labels = sorted(label for _target, label in outgoing[suffix_to_id[suffix]])
        if labels != ["No", "Yes"]:
            raise RuntimeError(f"Decision {suffix} must have one Yes and one No branch, found {labels}")

    start_id = suffix_to_id["start"]
    end_id = suffix_to_id["end"]
    reachable = set()
    queue = deque([start_id])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(target for target, _label in outgoing[current])
    if reachable != set(flow_by_id):
        raise RuntimeError("Not every flow component is reachable from Start")

    can_reach_end = set()
    queue = deque([end_id])
    while queue:
        current = queue.popleft()
        if current in can_reach_end:
            continue
        can_reach_end.add(current)
        queue.extend(incoming[current])
    if can_reach_end != set(flow_by_id):
        raise RuntimeError("Not every flow branch eventually reaches End")


def export() -> None:
    if not DRAWIO.exists():
        raise RuntimeError(f"Draw.io Desktop not found at {DRAWIO}")
    subprocess.run(
        [str(DRAWIO), "--export", "--format", "svg", "--page-index", "0", "--output", str(SVG_OUTPUT), str(OUTPUT)],
        check=True,
    )
    subprocess.run(
        [str(DRAWIO), "--export", "--format", "png", "--page-index", "0", "--scale", "2", "--output", str(PNG_OUTPUT), str(OUTPUT)],
        check=True,
    )


def main() -> None:
    if not REORGANIZED_SOURCE.exists():
        raise FileNotFoundError(REORGANIZED_SOURCE)
    if not BACKUP.exists() and OUTPUT.exists():
        shutil.copy2(OUTPUT, BACKUP)
    tree = build()
    write_xml(tree, OUTPUT)
    validate(OUTPUT)
    EDITOR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT, EDITOR_OUTPUT)
    export()
    print(OUTPUT)
    print(SVG_OUTPUT)
    print(PNG_OUTPUT)
    print(EDITOR_OUTPUT)


if __name__ == "__main__":
    main()
