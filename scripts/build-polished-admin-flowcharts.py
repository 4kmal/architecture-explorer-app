#!/usr/bin/env python3
"""Create presentation-polished variants of the five Administrator flow charts.

The canonical flow logic stays in the existing Draw.io sources.  This script
copies those sources into an ``Original`` Explorer variant, applies only
presentation-level styling and routing refinements to a working copy, and
publishes the result as the default ``Polished`` variant.

The visual rules follow the generic drawio-ai-kit workflow: one aligned
top-to-bottom spine, deliberate branch corridors, restrained semantic colour,
theme-aware fills, and structural validation before rendering.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR = EXPLORER / "assets" / "editor"
DRAWIO = Path(r"C:\Program Files\draw.io\draw.io.exe")
DRAWIO_AI = shutil.which("drawio-ai")


@dataclass(frozen=True)
class Spec:
    diagram_id: str
    source_stem: str
    editor_stem: str
    components: int
    connectors: int
    lane_labels: tuple[tuple[str, str, float, float, float, float], ...] = ()


SPECS = (
    Spec(
        "admin-access-dashboard-flowchart",
        "Flow Chart PetaKerja - Access Administrator Dashboard",
        "flowchart-admin-access-dashboard",
        17,
        19,
    ),
    Spec(
        "admin-monitor-activity-flowchart",
        "Flow Chart PetaKerja - Monitor System Activity Logs",
        "flowchart-admin-monitor-activity",
        12,
        13,
    ),
    Spec(
        "admin-manage-users-flowchart",
        "Flow Chart PetaKerja - Manage Users",
        "flowchart-admin-manage-users",
        12,
        13,
    ),
    Spec(
        "admin-manage-ai-configuration-flowchart",
        "Flow Chart PetaKerja - Manage AI Chatbot Configuration",
        "flowchart-admin-manage-ai-configuration",
        29,
        35,
        (
            ("key-lane", "Shared platform key", 120, 850, 400, 34),
            ("refresh-lane", "Model catalogue refresh", 900, 850, 390, 34),
        ),
    ),
    Spec(
        "admin-sign-out-flowchart",
        "Flow Chart PetaKerja - Administrator Sign Out",
        "flowchart-admin-sign-out",
        11,
        11,
    ),
)


PALETTE = {
    "process": {
        "fillColor": "light-dark(#eef5ff,#17263a)",
        "strokeColor": "light-dark(#3d6f9e,#8fb7df)",
    },
    "decision": {
        "fillColor": "light-dark(#fff7df,#3a2e16)",
        "strokeColor": "light-dark(#9a6700,#f4c95d)",
    },
    "success": {
        "fillColor": "light-dark(#ecfdf3,#133221)",
        "strokeColor": "light-dark(#1f7a4d,#72d6a1)",
    },
    "error": {
        "fillColor": "light-dark(#fff1f2,#3b1d22)",
        "strokeColor": "light-dark(#b42318,#ff9b92)",
    },
    "neutral": {
        "fillColor": "light-dark(#f3f4f6,#242933)",
        "strokeColor": "light-dark(#667085,#aeb7c7)",
    },
    "owner": {
        "fillColor": "light-dark(#f5f0ff,#2b2140)",
        "strokeColor": "light-dark(#6941c6,#b9a2ff)",
    },
}

ERROR_KEYS = {
    "sign-in-required", "access-denied", "request-error", "validation-error",
    "save-error", "sign-out-failure",
}
NEUTRAL_KEYS = {"empty-state", "read-only"}
SUCCESS_KEYS = {
    "start", "end", "display-overview", "display-activity", "display-users",
    "save-success", "refresh-complete", "reload-providers", "display-signed-out",
}
OWNER_KEYS = {
    "owner-action", "open-key-modal", "enter-key", "save-credential",
    "record-audit", "request-refresh", "read-credentials", "refresh-providers",
    "refresh-partial", "reload-refresh",
}


def style_map(style: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in style.split(";"):
        if not token:
            continue
        if "=" in token:
            key, value = token.split("=", 1)
            result[key] = value
        else:
            result[token] = ""
    return result


def style_text(values: dict[str, str]) -> str:
    return ";".join(f"{key}={value}" if value != "" else key for key, value in values.items()) + ";"


def clean_label(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value or "")).strip()


def wrapper_cell(wrapper: ET.Element) -> ET.Element:
    cell = wrapper.find("mxCell")
    if cell is None:
        raise RuntimeError(f"Object {wrapper.get('id')} has no mxCell")
    return cell


def component_suffix(wrapper: ET.Element, diagram_id: str) -> str | None:
    key = wrapper.get("petakerjaKey", "")
    prefix = f"{diagram_id}/"
    return key[len(prefix):] if key.startswith(prefix) else None


def semantic_kind(suffix: str, cell: ET.Element) -> str:
    style = cell.get("style", "")
    if "shape=mxgraph.flowchart.decision" in style:
        return "decision"
    if suffix in ERROR_KEYS or "error" in suffix or "failure" in suffix or "denied" in suffix:
        return "error"
    if suffix in NEUTRAL_KEYS:
        return "neutral"
    if suffix in SUCCESS_KEYS:
        return "success"
    if suffix in OWNER_KEYS:
        return "owner"
    return "process"


def polish_vertex(wrapper: ET.Element, suffix: str, cell: ET.Element) -> None:
    kind = semantic_kind(suffix, cell)
    values = style_map(cell.get("style", ""))
    values.update(PALETTE[kind])
    values.update({
        "fontColor": "light-dark(#172033,#f3f6fb)",
        "fontSize": "12",
        "fontFamily": "Arial",
        "spacing": "7",
        "shadow": "1",
    })
    if "shape=mxgraph.flowchart.decision" not in values and "shape=mxgraph.flowchart.start_1" not in values:
        values.update({"rounded": "1", "arcSize": "8"})
    if kind in {"decision", "success"}:
        values["fontStyle"] = "1"
    cell.set("style", style_text(values))


def polish_noninteractive(wrapper: ET.Element, cell: ET.Element) -> None:
    identifier = wrapper.get("id", "")
    values = style_map(cell.get("style", ""))
    if identifier.endswith("page-background"):
        values.update({
            "fillColor": "light-dark(#fbfcfe,#0b1118)",
            "strokeColor": "none",
            "shadow": "0",
        })
    elif identifier.endswith("title"):
        values.update({
            "fontColor": "light-dark(#172033,#f3f6fb)",
            "fontSize": "14",
            "fontStyle": "1",
            "fontFamily": "Arial",
        })
    else:
        values.update({
            "fontColor": "light-dark(#475467,#c5cedb)",
            "fontFamily": "Arial",
        })
    cell.set("style", style_text(values))


def add_lane_label(graph_root: ET.Element, layer_id: str, spec: Spec,
                   key: str, label: str, x: float, y: float, width: float, height: float) -> None:
    wrapper = ET.SubElement(graph_root, "object", {
        "id": f"{spec.diagram_id}-polished-{key}",
        "label": label,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": layer_id,
        "vertex": "1",
        "style": (
            "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
            "align=center;verticalAlign=middle;fontSize=12;fontStyle=1;"
            "fontFamily=Arial;fontColor=light-dark(#475467,#c5cedb);"
        ),
    })
    ET.SubElement(cell, "mxGeometry", {
        "x": f"{x:g}", "y": f"{y:g}", "width": f"{width:g}",
        "height": f"{height:g}", "as": "geometry",
    })


def polish_edge(wrapper: ET.Element, cell: ET.Element, source_kind: str,
                target_kind: str, target_suffix: str | None) -> None:
    values = style_map(cell.get("style", ""))
    geometry = cell.find("mxGeometry")
    has_points = bool(geometry is not None and geometry.findall(".//mxPoint"))
    values.update({
        "edgeStyle": "orthogonalEdgeStyle",
        "rounded": "0" if has_points or clean_label(wrapper.get("label", "")) else "1",
        "orthogonalLoop": "1",
        "jettySize": "auto",
        "html": "1",
        "endArrow": "classic",
        "endFill": "1",
        "strokeWidth": "2",
        "fontSize": "11",
        "fontFamily": "Arial",
        "fontColor": "light-dark(#344054,#d8e0eb)",
        "labelBackgroundColor": "light-dark(#fbfcfe,#0b1118)",
    })
    colour_kind = source_kind if target_suffix == "end" and source_kind in {"error", "neutral"} else target_kind
    edge_colour = {
        "error": "light-dark(#b42318,#ff9b92)",
        "neutral": "light-dark(#667085,#aeb7c7)",
        "success": "light-dark(#1f7a4d,#72d6a1)",
        "owner": "light-dark(#6941c6,#b9a2ff)",
    }.get(colour_kind, "light-dark(#344054,#c7d0dd)")
    values["strokeColor"] = edge_colour
    cell.set("style", style_text(values))


def spread_end_fan_in(wrappers: list[ET.Element], end_id: str, node_centres: dict[str, float]) -> None:
    incoming = [wrapper for wrapper in wrappers if wrapper_cell(wrapper).get("edge") == "1"
                and wrapper_cell(wrapper).get("target") == end_id]
    main = [wrapper for wrapper in incoming if not wrapper_cell(wrapper).findall(".//mxPoint")]
    sides = [wrapper for wrapper in incoming if wrapper not in main]
    for wrapper in main:
        values = style_map(wrapper_cell(wrapper).get("style", ""))
        values.update({"entryX": "0.5", "entryY": "0", "entryPerimeter": "0"})
        wrapper_cell(wrapper).set("style", style_text(values))
    left = [wrapper for wrapper in sides if node_centres.get(wrapper_cell(wrapper).get("source", ""), 10**9)
            < node_centres.get(end_id, 0)]
    right = [wrapper for wrapper in sides if wrapper not in left]
    for group, x in ((left, 0.0), (right, 1.0)):
        count = len(group)
        for index, wrapper in enumerate(group):
            y = 0.35 if count == 1 else 0.25 + 0.5 * index / max(1, count - 1)
            values = style_map(wrapper_cell(wrapper).get("style", ""))
            values.update({"entryX": f"{x:g}", "entryY": f"{y:g}", "entryPerimeter": "0"})
            wrapper_cell(wrapper).set("style", style_text(values))


def validate_structure(path: Path, spec: Spec) -> dict[str, object]:
    parsed = ET.parse(path).getroot()
    diagrams = parsed.findall("diagram")
    if len(diagrams) != 1:
        raise RuntimeError(f"{spec.diagram_id}: expected one page")
    wrappers = diagrams[0].findall(".//object")
    ids = [wrapper.get("id", "") for wrapper in wrappers]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise RuntimeError(f"{spec.diagram_id}: missing or duplicate object IDs")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers if wrapper.get("petakerjaKey")]
    if any(count > 1 for count in Counter(keys).values()):
        raise RuntimeError(f"{spec.diagram_id}: duplicate stable keys")

    components: dict[str, str] = {}
    edges: list[ET.Element] = []
    for wrapper in wrappers:
        cell = wrapper_cell(wrapper)
        suffix = component_suffix(wrapper, spec.diagram_id)
        if cell.get("vertex") == "1" and suffix:
            components[wrapper.get("id", "")] = suffix
        elif cell.get("edge") == "1":
            edges.append(wrapper)
    if len(components) != spec.components:
        raise RuntimeError(f"{spec.diagram_id}: expected {spec.components} components, found {len(components)}")
    if len(edges) != spec.connectors:
        raise RuntimeError(f"{spec.diagram_id}: expected {spec.connectors} connectors, found {len(edges)}")

    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in edges:
        cell = wrapper_cell(wrapper)
        source, target = cell.get("source", ""), cell.get("target", "")
        if source not in components or target not in components:
            raise RuntimeError(f"{spec.diagram_id}: detached connector {wrapper.get('id')}")
        outgoing[source].append(target)
        incoming[target].append(source)
        style = cell.get("style", "")
        if "endArrow=classic" not in style or "endFill=1" not in style:
            raise RuntimeError(f"{spec.diagram_id}: non-classic connector {wrapper.get('id')}")

    by_key = {suffix: identifier for identifier, suffix in components.items()}
    reachable: set[str] = set()
    queue = deque([by_key["start"]])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(outgoing[current])
    if reachable != set(components):
        missing = sorted(components[item] for item in set(components) - reachable)
        raise RuntimeError(f"{spec.diagram_id}: unreachable components {missing}")

    reaches_end: set[str] = set()
    queue = deque([by_key["end"]])
    while queue:
        current = queue.popleft()
        if current in reaches_end:
            continue
        reaches_end.add(current)
        queue.extend(incoming[current])
    if reaches_end != set(components):
        missing = sorted(components[item] for item in set(components) - reaches_end)
        raise RuntimeError(f"{spec.diagram_id}: components without End path {missing}")
    return {"components": len(components), "connectors": len(edges)}


def polish(source: Path, spec: Spec) -> ET.ElementTree:
    tree = ET.parse(source)
    root = tree.getroot()
    diagram = root.find("diagram")
    if diagram is None:
        raise RuntimeError(f"{source}: missing diagram")
    diagram.set("name", f"{diagram.get('name', spec.source_stem)} - Polished")
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError(f"{source}: missing mxGraphModel")
    model.set("background", "light-dark(#fbfcfe,#0b1118)")
    graph_root = model.find("root")
    if graph_root is None:
        raise RuntimeError(f"{source}: missing graph root")
    layer = next((cell for cell in graph_root.findall("mxCell") if cell.get("parent")), None)
    if layer is None:
        raise RuntimeError(f"{source}: missing layer")

    wrappers = diagram.findall(".//object")
    node_suffixes: dict[str, str] = {}
    node_kinds: dict[str, str] = {}
    node_centres: dict[str, float] = {}
    end_id = ""
    for wrapper in wrappers:
        cell = wrapper_cell(wrapper)
        suffix = component_suffix(wrapper, spec.diagram_id)
        if cell.get("vertex") == "1" and suffix:
            node_suffixes[wrapper.get("id", "")] = suffix
            node_kinds[wrapper.get("id", "")] = semantic_kind(suffix, cell)
            geo = cell.find("mxGeometry")
            if geo is not None:
                node_centres[wrapper.get("id", "")] = float(geo.get("x", "0")) + float(geo.get("width", "0")) / 2
            if suffix == "end":
                end_id = wrapper.get("id", "")
            polish_vertex(wrapper, suffix, cell)
        elif cell.get("vertex") == "1":
            polish_noninteractive(wrapper, cell)

    for wrapper in wrappers:
        cell = wrapper_cell(wrapper)
        if cell.get("edge") == "1":
            polish_edge(
                wrapper,
                cell,
                node_kinds.get(cell.get("source", ""), "process"),
                node_kinds.get(cell.get("target", ""), "process"),
                node_suffixes.get(cell.get("target", "")),
            )
    if end_id:
        spread_end_fan_in(wrappers, end_id, node_centres)

    for lane in spec.lane_labels:
        add_lane_label(graph_root, layer.get("id", ""), spec, *lane)
    return tree


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def light_render_copy(source: Path, destination: Path) -> None:
    """Write a temporary report-export copy with every adaptive colour fixed to light.

    The canonical Draw.io and SVG sources keep ``light-dark(...)`` so Explorer
    themes still work.  A report PNG, however, must not depend on the Windows
    theme of the machine running the generator.
    """
    xml = source.read_text(encoding="utf-8")
    xml = re.sub(
        r"light-dark\(\s*(#[0-9a-fA-F]{3,8})\s*,\s*(#[0-9a-fA-F]{3,8})\s*\)",
        r"\1",
        xml,
    )
    destination.write_text(xml, encoding="utf-8")


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(__import__("os").environ)
    env.setdefault("DRAWIO_CLI", str(DRAWIO))
    result = subprocess.run(command, text=True, capture_output=True, env=env)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
    return result


def build_one(spec: Spec) -> dict[str, object]:
    source = DIAGRAMS / f"{spec.source_stem}.drawio"
    polished = DIAGRAMS / f"{spec.source_stem} - Polished.drawio"
    polished_svg = DIAGRAMS / f"{spec.source_stem} - Polished.svg"
    polished_png = DIAGRAMS / f"{spec.source_stem} - Polished.png"
    editor_original = EDITOR / f"{spec.editor_stem}-original.drawio"
    editor_polished = EDITOR / f"{spec.editor_stem}.drawio"
    if not source.exists():
        raise FileNotFoundError(source)

    editor_original.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, editor_original)
    tree = polish(source, spec)
    write_xml(tree, polished)
    structural = validate_structure(polished, spec)
    shutil.copy2(polished, editor_polished)

    if not DRAWIO_AI:
        raise RuntimeError("drawio-ai was not found. Install sparklabx/drawio-ai-kit v1.0.0 first.")
    strict = run_checked([DRAWIO_AI, "validate", str(polished), "--strict"])
    validation = json.loads(strict.stdout)
    if not validation.get("ok"):
        raise RuntimeError(f"{spec.diagram_id}: drawio-ai validation failed")
    audit = json.loads(run_checked([DRAWIO_AI, "audit", str(polished)]).stdout)
    non_title_advice = [item for item in audit.get("advice", []) if "hero title" not in item]
    if non_title_advice:
        raise RuntimeError(f"{spec.diagram_id}: unresolved aesthetic advice: {non_title_advice}")

    with tempfile.TemporaryDirectory(prefix="petakerja-flowchart-") as temp_dir:
        light_source = Path(temp_dir) / polished.name
        light_render_copy(polished, light_source)
        run_checked([DRAWIO_AI, "render", str(light_source), "-o", str(polished_png), "--scale", "2"])
    run_checked([
        str(DRAWIO), "--export", "--format", "svg", "--page-index", "0",
        "--output", str(polished_svg), str(polished),
    ])
    return {
        "id": spec.diagram_id,
        **structural,
        "drawio": str(polished),
        "svg": str(polished_svg),
        "png": str(polished_png),
        "originalEditor": str(editor_original),
        "polishedEditor": str(editor_polished),
        "auditAdvice": audit.get("advice", []),
    }


def main() -> None:
    if not DRAWIO.exists():
        raise FileNotFoundError(DRAWIO)
    results = [build_one(spec) for spec in SPECS]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
