#!/usr/bin/env python3
"""Build the focused PetaKerja Administrator Manage Users flow chart.

The TTTE1113 Flow Chart Template is used as a read-only style source. The
generated chart models only the read-only Users branch after administrator
authentication and role validation have already succeeded.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from pathlib import Path


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
TEMPLATE = DIAGRAMS / "Flow Chart Template.drawio"
OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Manage Users.drawio"
SVG_OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Manage Users.svg"
PNG_OUTPUT = DIAGRAMS / "Flow Chart PetaKerja - Manage Users.png"

EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "flowchart-admin-manage-users-original.drawio"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")

PAGE_ID = "petakerja_flow_admin_manage_users"
ROOT_ID = "admin-manage-users-flow-root"
LAYER_ID = "admin-manage-users-flow-layer"
KEY_PREFIX = "admin-manage-users-flowchart/"
PAGE_WIDTH = 980
PAGE_HEIGHT = 1200

FLOW_COMPONENTS = {
    "start",
    "select-users",
    "loading-state",
    "request-users",
    "retrieve-users",
    "request-successful",
    "request-error",
    "store-users",
    "users-returned",
    "empty-state",
    "display-users",
    "end",
}
DECISIONS = {"request-successful", "users-returned"}


def template_style(predicate) -> str:
    root = ET.parse(TEMPLATE).getroot()
    for cell in root.findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError("Required style was not found in Flow Chart Template.drawio")


def strip_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


START_STYLE = template_style(lambda _cell, style: "shape=mxgraph.flowchart.start_1" in style)
DECISION_STYLE = template_style(lambda _cell, style: "shape=mxgraph.flowchart.decision" in style)
PROCESS_STYLE = template_style(
    lambda cell, style: cell.get("vertex") == "1"
    and "shape=mxgraph.flowchart" not in style
    and float(cell.find("mxGeometry").get("width", "0")) >= 100
)

THEME_STYLE = (
    "fillColor=light-dark(#ffffff,#151a22);"
    "strokeColor=light-dark(#111827,#d8dde7);"
    "fontColor=light-dark(#111827,#eef1f6);"
)
START_STYLE = strip_properties(START_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
DECISION_STYLE = strip_properties(DECISION_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
PROCESS_STYLE = strip_properties(PROCESS_STYLE, ("fillColor", "strokeColor", "fontColor")) + ";" + THEME_STYLE
TEXT_STYLE = (
    "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=middle;fontColor=light-dark(#111827,#eef1f6);"
)
NOTE_STYLE = TEXT_STYLE + "align=left;fontSize=11;fontStyle=2;"
FLOW_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    "endArrow=classic;endFill=1;strokeWidth=2;"
    "strokeColor=light-dark(#111827,#d8dde7);"
    "fontColor=light-dark(#111827,#eef1f6);labelBackgroundColor=none;"
)


def geometry(cell: ET.Element, *, x: float | None = None, y: float | None = None,
             width: float | None = None, height: float | None = None,
             relative: bool = False, points: list[tuple[float, float]] | None = None) -> ET.Element:
    attrs = {"as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    node = ET.SubElement(cell, "mxGeometry", attrs)
    for name, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        if value is not None:
            node.set(name, f"{value:g}")
    if points:
        array = ET.SubElement(node, "Array", {"as": "points"})
        for px, py in points:
            ET.SubElement(array, "mxPoint", {"x": f"{px:g}", "y": f"{py:g}"})
    return node


def add_vertex(root: ET.Element, suffix: str, label: str, style: str,
               x: float, y: float, width: float, height: float,
               *, interactive: bool = True) -> str:
    cell_id = f"admin-manage-users-flow-{suffix}"
    attrs = {"id": cell_id, "label": label}
    if interactive:
        attrs["petakerjaKey"] = KEY_PREFIX + suffix
    wrapper = ET.SubElement(root, "object", attrs)
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": LAYER_ID,
        "vertex": "1",
        "style": style,
    })
    geometry(cell, x=x, y=y, width=width, height=height)
    return cell_id


def add_edge(root: ET.Element, suffix: str, source: str, target: str,
             *, label: str = "", points: list[tuple[float, float]] | None = None,
             style: str = "") -> None:
    wrapper = ET.SubElement(root, "object", {
        "id": f"admin-manage-users-flow-{suffix}",
        "label": label,
        "petakerjaKey": KEY_PREFIX + suffix,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": LAYER_ID,
        "edge": "1",
        "source": source,
        "target": target,
        "style": FLOW_STYLE + style,
    })
    geometry(cell, relative=True, points=points)


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {
        "host": "Electron",
        "agent": "PetaKerja Architecture Explorer",
        "version": "27.0.2",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "name": "PetaKerja Manage Users",
        "id": PAGE_ID,
    })
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH),
        "dy": str(PAGE_HEIGHT),
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": str(PAGE_WIDTH),
        "pageHeight": str(PAGE_HEIGHT),
        "math": "0",
        "shadow": "0",
        "background": "light-dark(#ffffff,#0f131a)",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": ROOT_ID})
    ET.SubElement(root, "mxCell", {"id": LAYER_ID, "parent": ROOT_ID})

    add_vertex(
        root, "page-background", "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#0f131a);"
        "strokeColor=none;pointerEvents=0;locked=1;",
        0, 0, PAGE_WIDTH, PAGE_HEIGHT, interactive=False,
    )
    add_vertex(root, "title", "PetaKerja Administrator Manage Users Flow Chart",
               TEXT_STYLE + "fontSize=22;fontStyle=1;", 150, 22, 680, 38, interactive=False)
    add_vertex(root, "subtitle", "Focused read-only Users branch; dashboard access validation is documented separately.",
               TEXT_STYLE + "fontSize=11;fontStyle=2;", 130, 62, 720, 30, interactive=False)
    add_vertex(root, "precondition",
               "Precondition: The Administrator is signed in, has the admin or owner role, and the Admin Dashboard is open.",
               NOTE_STYLE, 140, 100, 700, 34, interactive=False)

    ids: dict[str, str] = {}
    ids["start"] = add_vertex(root, "start", "Start", START_STYLE, 456.665, 150, 66.67, 40)
    ids["select-users"] = add_vertex(root, "select-users", "Administrator selects the Users section", PROCESS_STYLE, 390, 225, 200, 50)
    ids["loading-state"] = add_vertex(root, "loading-state", "Display the loading state", PROCESS_STYLE, 400, 310, 180, 50)
    ids["request-users"] = add_vertex(root, "request-users", "Request recent user information", PROCESS_STYLE, 390, 395, 200, 50)
    ids["retrieve-users"] = add_vertex(root, "retrieve-users", "Retrieve up to 100 recent profiles and role assignments", PROCESS_STYLE, 370, 480, 240, 60)
    ids["request-successful"] = add_vertex(root, "request-successful", "Request successful?", DECISION_STYLE, 430, 580, 120, 70)
    ids["request-error"] = add_vertex(root, "request-error", "Clear the loading state and display the dashboard loading error", PROCESS_STYLE, 680, 585, 220, 60)
    ids["store-users"] = add_vertex(root, "store-users", "Store the returned records and clear the loading state", PROCESS_STYLE, 375, 700, 230, 60)
    ids["users-returned"] = add_vertex(root, "users-returned", "Users returned?", DECISION_STYLE, 430, 800, 120, 70)
    ids["empty-state"] = add_vertex(root, "empty-state", "Display No users returned", PROCESS_STYLE, 90, 805, 200, 60)
    ids["display-users"] = add_vertex(root, "display-users", "Display names, emails, roles, creation dates and last-login dates", PROCESS_STYLE, 365, 920, 250, 65)
    ids["end"] = add_vertex(root, "end", "End", START_STYLE, 456.665, 1080, 66.67, 40)

    vertical = "exitX=0.5;exitY=1;entryX=0.5;entryY=0;exitPerimeter=0;entryPerimeter=0;"
    right = "exitX=1;exitY=0.5;entryX=0;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
    left = "exitX=0;exitY=0.5;entryX=1;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
    end_right = "exitX=1;exitY=0.5;entryX=1;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"
    end_left = "exitX=0;exitY=0.5;entryX=0;entryY=0.5;exitPerimeter=0;entryPerimeter=0;"

    add_edge(root, "start-to-select", ids["start"], ids["select-users"], style=vertical)
    add_edge(root, "select-to-loading", ids["select-users"], ids["loading-state"], style=vertical)
    add_edge(root, "loading-to-request", ids["loading-state"], ids["request-users"], style=vertical)
    add_edge(root, "request-to-retrieve", ids["request-users"], ids["retrieve-users"], style=vertical)
    add_edge(root, "retrieve-to-request-result", ids["retrieve-users"], ids["request-successful"], style=vertical)
    add_edge(root, "request-no", ids["request-successful"], ids["request-error"], label="No", style=right)
    add_edge(root, "error-to-end", ids["request-error"], ids["end"],
             points=[(930, 615), (930, 1100)], style=end_right)
    add_edge(root, "request-yes", ids["request-successful"], ids["store-users"], label="Yes", style=vertical)
    add_edge(root, "store-to-users-result", ids["store-users"], ids["users-returned"], style=vertical)
    add_edge(root, "users-no", ids["users-returned"], ids["empty-state"], label="No", style=left)
    add_edge(root, "empty-to-end", ids["empty-state"], ids["end"],
             points=[(55, 835), (55, 1100)], style=end_left)
    add_edge(root, "users-yes", ids["users-returned"], ids["display-users"], label="Yes", style=vertical)
    add_edge(root, "display-to-end", ids["display-users"], ids["end"], style=vertical)

    add_vertex(root, "scope-note",
               "The current implementation is read-only. Role changes, account suspension and account deletion are not available.",
               NOTE_STYLE, 125, 1145, 730, 32, interactive=False)
    return ET.ElementTree(mxfile)


def suffix(wrapper: ET.Element) -> str | None:
    key = wrapper.get("petakerjaKey", "")
    return key[len(KEY_PREFIX):] if key.startswith(KEY_PREFIX) else None


def validate(path: Path) -> None:
    parsed = ET.parse(path).getroot()
    diagrams = parsed.findall("diagram")
    if len(diagrams) != 1 or diagrams[0].get("id") != PAGE_ID:
        raise RuntimeError("Expected one normalized Manage Users flow-chart page")
    model = diagrams[0].find("mxGraphModel")
    if model is None or model.get("pageWidth") != str(PAGE_WIDTH) or model.get("pageHeight") != str(PAGE_HEIGHT):
        raise RuntimeError("Generated flow chart has the wrong page dimensions")

    wrappers = parsed.findall(".//object")
    object_ids = [wrapper.get("id", "") for wrapper in wrappers]
    if any(not item for item in object_ids) or len(object_ids) != len(set(object_ids)):
        raise RuntimeError("Generated flow chart has missing or duplicate object IDs")

    keyed = [wrapper.get("petakerjaKey", "") for wrapper in wrappers if wrapper.get("petakerjaKey")]
    if any(count > 1 for count in Counter(keyed).values()):
        raise RuntimeError("Generated flow chart has duplicate petakerjaKey values")

    vertices: dict[str, str] = {}
    edges: list[ET.Element] = []
    for wrapper in wrappers:
        cell = wrapper.find("mxCell")
        if cell is None:
            raise RuntimeError(f"Object {wrapper.get('id')} has no mxCell")
        if cell.get("vertex") == "1":
            geometry_node = cell.find("mxGeometry")
            if geometry_node is None:
                raise RuntimeError(f"Vertex {wrapper.get('id')} has no geometry")
            x = float(geometry_node.get("x", "0"))
            y = float(geometry_node.get("y", "0"))
            width = float(geometry_node.get("width", "0"))
            height = float(geometry_node.get("height", "0"))
            if min(x, y) < 0 or x + width > PAGE_WIDTH or y + height > PAGE_HEIGHT:
                raise RuntimeError(f"Vertex {wrapper.get('id')} overflows the page")
            component = suffix(wrapper)
            if component in FLOW_COMPONENTS:
                vertices[wrapper.get("id", "")] = component
        elif cell.get("edge") == "1":
            edges.append(wrapper)

    if set(vertices.values()) != FLOW_COMPONENTS or len(vertices) != 12:
        raise RuntimeError("Generated flow chart must contain the 12 canonical interactive components")
    if len(edges) != 13:
        raise RuntimeError(f"Expected 13 connectors, found {len(edges)}")

    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in edges:
        cell = wrapper.find("mxCell")
        source = cell.get("source", "")
        target = cell.get("target", "")
        if source not in vertices or target not in vertices:
            raise RuntimeError(f"Connector {wrapper.get('id')} has a missing endpoint")
        if "endArrow=classic" not in cell.get("style", "") or "endFill=1" not in cell.get("style", ""):
            raise RuntimeError(f"Connector {wrapper.get('id')} does not use a filled classic arrow")
        for point in cell.findall(".//mxPoint"):
            px = float(point.get("x", "0"))
            py = float(point.get("y", "0"))
            if px < 0 or py < 0 or px > PAGE_WIDTH or py > PAGE_HEIGHT:
                raise RuntimeError(f"Connector {wrapper.get('id')} has a point outside the page")
        outgoing[source].append((target, wrapper.get("label", "")))
        incoming[target].append(source)

    by_suffix = {component: object_id for object_id, component in vertices.items()}
    for decision in DECISIONS:
        labels = sorted(label for _target, label in outgoing[by_suffix[decision]])
        if labels != ["No", "Yes"]:
            raise RuntimeError(f"Decision {decision} must have one Yes and one No branch")

    reachable: set[str] = set()
    queue = deque([by_suffix["start"]])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(target for target, _label in outgoing[current])
    if reachable != set(vertices):
        raise RuntimeError("Not every component is reachable from Start")

    can_reach_end: set[str] = set()
    queue = deque([by_suffix["end"]])
    while queue:
        current = queue.popleft()
        if current in can_reach_end:
            continue
        can_reach_end.add(current)
        queue.extend(incoming[current])
    if can_reach_end != set(vertices):
        raise RuntimeError("Not every flow route reaches End")


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


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
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    tree = build()
    write_xml(tree, OUTPUT)
    validate(OUTPUT)
    EDITOR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT, EDITOR_OUTPUT)
    export()
    print(f"Draw.io: {OUTPUT}")
    print(f"SVG: {SVG_OUTPUT}")
    print(f"PNG: {PNG_OUTPUT}")
    print(f"Explorer editor source: {EDITOR_OUTPUT}")
    print("Validated: 12 interactive components, 13 connectors, all routes reach End")


if __name__ == "__main__":
    main()
