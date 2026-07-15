#!/usr/bin/env python3
"""Build polished variants for the Core Domain and Google sign-in flow chart.

The current corrected/reorganised sources remain the authoritative Original
variants.  This generator preserves their cells, labels, geometry, stable keys
and graph structure while applying presentation-only styling and targeted
connector routing fixes.  It intentionally mirrors the generic workflow used
by ``build-polished-admin-flowcharts.py``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from pathlib import Path


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR = EXPLORER / "assets" / "editor"
ADMIN_POLISHER_PATH = Path(__file__).with_name("build-polished-admin-flowcharts.py")

DOMAIN_ID = "domain"
DOMAIN_SOURCE = DIAGRAMS / "Class Diagram PetaKerja.drawio"
DOMAIN_POLISHED = DIAGRAMS / "Class Diagram PetaKerja - Polished.drawio"
DOMAIN_POLISHED_SVG = DIAGRAMS / "Class Diagram PetaKerja - Polished.svg"
DOMAIN_POLISHED_PNG = DIAGRAMS / "Class Diagram PetaKerja - Polished.png"
DOMAIN_EDITOR = EDITOR / "class-domain-petakerja.drawio"
DOMAIN_EDITOR_ORIGINAL = EDITOR / "class-domain-petakerja-original.drawio"

FLOW_ID = "user-google-sign-in-flowchart"
FLOW_SOURCE = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google.drawio"
FLOW_POLISHED = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google - Polished.drawio"
FLOW_POLISHED_SVG = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google - Polished.svg"
FLOW_POLISHED_PNG = DIAGRAMS / "Flow Chart PetaKerja - Sign in with Google - Polished.png"
FLOW_EDITOR = EDITOR / "flowchart-user-google-sign-in.drawio"
FLOW_EDITOR_ORIGINAL = EDITOR / "flowchart-user-google-sign-in-original.drawio"

FLOW_NONINTERACTIVE = {"page-background", "title", "scope-note"}
FLOW_SUCCESS = {"start", "end", "display-authenticated-menu"}
FLOW_ERROR = {"display-auth-error"}
FLOW_NEUTRAL = {"guest-state"}

GROUPS = {
    "identity": {
        "container": "JzSmHml7n7fI4_WiAD8F-4",
        "keys": {"auth-identity", "user-profile"},
        "fill": "light-dark(#edf5ff,#14263a)",
        "body": "light-dark(#fbfdff,#111a25)",
        "stroke": "light-dark(#3975a6,#86b9e6)",
        "containerFill": "light-dark(#f7fbff,#0f1b29)",
    },
    "jobs": {
        "container": "JzSmHml7n7fI4_WiAD8F-5",
        "keys": {"job-entity", "job-state-entity"},
        "fill": "light-dark(#fff6df,#392c14)",
        "body": "light-dark(#fffdf8,#201b12)",
        "stroke": "light-dark(#9a6700,#edc35b)",
        "containerFill": "light-dark(#fffcf4,#211b11)",
    },
    "mapping": {
        "container": "JzSmHml7n7fI4_WiAD8F-3",
        "keys": {
            "state-entity", "data-source-entity", "poi-group-entity",
            "poi-category-entity", "poi-entity", "highlight-entity",
            "open-data-api",
        },
        "fill": "light-dark(#eafaf1,#123222)",
        "body": "light-dark(#fbfefc,#101d17)",
        "stroke": "light-dark(#247a4d,#70d09d)",
        "containerFill": "light-dark(#f6fcf8,#0d2017)",
    },
    "ai": {
        "container": "JzSmHml7n7fI4_WiAD8F-2",
        "keys": {
            "ai-credential-entity", "ai-preference-entity",
            "ai-usage-entity", "audit-log-entity",
        },
        "fill": "light-dark(#f4efff,#2b2140)",
        "body": "light-dark(#fdfbff,#191424)",
        "stroke": "light-dark(#6941c6,#b9a2ff)",
        "containerFill": "light-dark(#faf7ff,#1b1527)",
    },
}


def load_admin_polisher():
    spec = importlib.util.spec_from_file_location("petakerja_admin_polisher", ADMIN_POLISHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADMIN_POLISHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


admin = load_admin_polisher()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def domain_suffix(cell: ET.Element) -> str | None:
    key = cell.get("petakerjaKey", "")
    prefix = f"{DOMAIN_ID}/"
    return key[len(prefix):] if key.startswith(prefix) else None


def group_for_suffix(suffix: str) -> dict[str, object]:
    for group in GROUPS.values():
        if suffix in group["keys"]:
            return group
    raise RuntimeError(f"No domain group configured for {suffix}")


def replace_inline_muted(value: str) -> str:
    return re.sub(
        r"color\s*:\s*#[0-9a-fA-F]{6}",
        "color:light-dark(#475467,#c5cedb)",
        value or "",
    )


def style_domain_class(cell: ET.Element, suffix: str, children: list[ET.Element]) -> None:
    group = group_for_suffix(suffix)
    values = admin.style_map(cell.get("style", ""))
    values.update({
        "fillColor": str(group["fill"]),
        "swimlaneFillColor": str(group["body"]),
        "strokeColor": str(group["stroke"]),
        "strokeWidth": "1.4",
        "fontColor": "light-dark(#172033,#f3f6fb)",
        "fontFamily": "Arial",
        "fontSize": "13",
        "shadow": "1",
    })
    cell.set("style", admin.style_text(values))
    cell.set("value", replace_inline_muted(cell.get("value", "")))

    for child in children:
        child_values = admin.style_map(child.get("style", ""))
        if "line" in child_values:
            child_values.update({
                "strokeColor": "light-dark(#98a2b3,#667085)",
                "strokeWidth": "1",
            })
        else:
            child_values.update({
                "fontColor": "light-dark(#273244,#e6ebf2)",
                "fontFamily": "Arial",
                "fontSize": "11",
            })
        child.set("style", admin.style_text(child_values))


def style_domain_container(cell: ET.Element, group: dict[str, object]) -> None:
    values = admin.style_map(cell.get("style", ""))
    values.update({
        "fillColor": str(group["containerFill"]),
        "strokeColor": str(group["stroke"]),
        "fontColor": "light-dark(#344054,#d8e0eb)",
        "fontFamily": "Arial",
        "fontSize": "13",
        "fontStyle": "1",
        "dashed": "1",
        "dashPattern": "6 4",
        "shadow": "0",
    })
    cell.set("style", admin.style_text(values))


def style_domain_text(cell: ET.Element) -> None:
    values = admin.style_map(cell.get("style", ""))
    if cell.get("id") == "petakerja-domain-title":
        values.update({
            "fontColor": "light-dark(#172033,#f3f6fb)",
            "fontFamily": "Arial", "fontSize": "24", "fontStyle": "1",
        })
    elif cell.get("id") == "petakerja-domain-subtitle":
        values.update({
            "fontColor": "light-dark(#475467,#c5cedb)",
            "fontFamily": "Arial", "fontSize": "11",
        })
    elif cell.get("id") == "petakerja-domain-legend":
        values.update({
            "fontColor": "light-dark(#475467,#c5cedb)",
            "fontFamily": "Arial", "fontSize": "10",
        })
    cell.set("style", admin.style_text(values))


def set_entry(cell: ET.Element, x: float, y: float) -> None:
    values = admin.style_map(cell.get("style", ""))
    values.update({
        "entryX": f"{x:g}", "entryY": f"{y:g}",
        "entryDx": "0", "entryDy": "0", "entryPerimeter": "0",
    })
    cell.set("style", admin.style_text(values))


def set_exit(cell: ET.Element, x: float, y: float) -> None:
    values = admin.style_map(cell.get("style", ""))
    values.update({
        "exitX": f"{x:g}", "exitY": f"{y:g}",
        "exitDx": "0", "exitDy": "0", "exitPerimeter": "0",
    })
    cell.set("style", admin.style_text(values))


def add_waypoint(cell: ET.Element, x: float, y: float) -> None:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    for existing in list(geometry):
        if existing.tag == "Array" and existing.get("as") == "points":
            geometry.remove(existing)
    points = ET.SubElement(geometry, "Array", {"as": "points"})
    ET.SubElement(points, "mxPoint", {"x": f"{x:g}", "y": f"{y:g}"})


def polish_domain() -> ET.ElementTree:
    tree = ET.parse(DOMAIN_SOURCE)
    root = tree.getroot()
    diagram = root.find("diagram")
    if diagram is None:
        raise RuntimeError("Domain source has no diagram page")
    diagram.set("name", f"{diagram.get('name', 'Core Domain Class Diagram')} - Polished")
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("Domain source has no mxGraphModel")
    model.set("background", "light-dark(#fbfcfe,#0b1118)")
    graph_root = model.find("root")
    if graph_root is None:
        raise RuntimeError("Domain source has no graph root")

    cells = {cell.get("id", ""): cell for cell in graph_root.findall("mxCell")}
    children: dict[str, list[ET.Element]] = defaultdict(list)
    for cell in cells.values():
        if cell.get("parent"):
            children[cell.get("parent", "")].append(cell)

    for cell in cells.values():
        suffix = domain_suffix(cell)
        if suffix:
            style_domain_class(cell, suffix, children.get(cell.get("id", ""), []))
        elif cell.get("id") in {group["container"] for group in GROUPS.values()}:
            group = next(item for item in GROUPS.values() if item["container"] == cell.get("id"))
            style_domain_container(cell, group)
        elif cell.get("id") in {
            "petakerja-domain-title", "petakerja-domain-subtitle", "petakerja-domain-legend",
        }:
            style_domain_text(cell)
        elif "edgeLabel" in cell.get("style", ""):
            values = admin.style_map(cell.get("style", ""))
            values.update({
                "fontColor": "light-dark(#344054,#d8e0eb)",
                "fontSize": "11",
                "fontFamily": "Arial",
                "labelBackgroundColor": "light-dark(#fbfcfe,#0b1118)",
            })
            cell.set("style", admin.style_text(values))
        elif cell.get("edge") == "1":
            values = admin.style_map(cell.get("style", ""))
            values.update({
                "strokeColor": "light-dark(#475467,#b8c2d0)",
                "strokeWidth": "1.3",
                "fontColor": "light-dark(#344054,#d8e0eb)",
                "fontSize": "11",
                "fontFamily": "Arial",
                "labelBackgroundColor": "light-dark(#fbfcfe,#0b1118)",
            })
            cell.set("style", admin.style_text(values))

    # Fan-in routes: preserve all endpoints and notation while separating
    # stacked arrowheads on POI, UserJobState and AIModelPreference.
    poi_entries = {
        "JzSmHml7n7fI4_WiAD8F-68": (0.0, 0.68),
        "JzSmHml7n7fI4_WiAD8F-72": (0.38, 0.0),
        "JzSmHml7n7fI4_WiAD8F-80": (1.0, 0.38),
        "JzSmHml7n7fI4_WiAD8F-84": (0.58, 1.0),
    }
    for edge_id, point in poi_entries.items():
        set_entry(cells[edge_id], *point)
    set_entry(cells["JzSmHml7n7fI4_WiAD8F-90"], 1.0, 0.25)
    set_entry(cells["JzSmHml7n7fI4_WiAD8F-93"], 0.0, 0.55)
    set_entry(cells["JzSmHml7n7fI4_WiAD8F-100"], 0.35, 1.0)
    set_entry(cells["JzSmHml7n7fI4_WiAD8F-109"], 0.0, 0.45)

    # Make the credential-to-preference dependency a deliberate horizontal
    # corridor so its label is centred instead of sitting on a bend.
    provider_edge = cells["JzSmHml7n7fI4_WiAD8F-109"]
    set_exit(provider_edge, 1.0, 0.5)
    add_waypoint(provider_edge, 2160, 455)
    return tree


def flow_suffix(wrapper: ET.Element) -> str | None:
    return admin.component_suffix(wrapper, FLOW_ID)


def flow_kind(suffix: str, cell: ET.Element) -> str:
    if "shape=mxgraph.flowchart.decision" in cell.get("style", ""):
        return "decision"
    if suffix in FLOW_ERROR:
        return "error"
    if suffix in FLOW_NEUTRAL:
        return "neutral"
    if suffix in FLOW_SUCCESS:
        return "success"
    return "process"


def polish_flowchart() -> ET.ElementTree:
    tree = ET.parse(FLOW_SOURCE)
    root = tree.getroot()
    diagram = root.find("diagram")
    if diagram is None:
        raise RuntimeError("Google flow-chart source has no diagram page")
    diagram.set("name", f"{diagram.get('name', 'Google Sign-In Flow Chart')} - Polished")
    model = diagram.find("mxGraphModel")
    if model is None:
        raise RuntimeError("Google flow-chart source has no mxGraphModel")
    model.set("background", "light-dark(#fbfcfe,#0b1118)")
    wrappers = diagram.findall(".//object")
    node_kinds: dict[str, str] = {}
    node_centres: dict[str, float] = {}
    end_id = ""

    admin.ERROR_KEYS.update(FLOW_ERROR)
    admin.NEUTRAL_KEYS.update(FLOW_NEUTRAL)
    admin.SUCCESS_KEYS.update(FLOW_SUCCESS)
    for wrapper in wrappers:
        cell = admin.wrapper_cell(wrapper)
        suffix = flow_suffix(wrapper)
        if cell.get("vertex") != "1":
            continue
        if suffix in FLOW_NONINTERACTIVE:
            admin.polish_noninteractive(wrapper, cell)
            continue
        if suffix:
            node_kinds[wrapper.get("id", "")] = flow_kind(suffix, cell)
            geometry = cell.find("mxGeometry")
            if geometry is not None:
                node_centres[wrapper.get("id", "")] = (
                    float(geometry.get("x", "0")) + float(geometry.get("width", "0")) / 2
                )
            if suffix == "end":
                end_id = wrapper.get("id", "")
            admin.polish_vertex(wrapper, suffix, cell)
        else:
            admin.polish_noninteractive(wrapper, cell)

    for wrapper in wrappers:
        cell = admin.wrapper_cell(wrapper)
        if cell.get("edge") == "1":
            admin.polish_edge(
                wrapper,
                cell,
                node_kinds.get(cell.get("source", ""), "process"),
                node_kinds.get(cell.get("target", ""), "process"),
                flow_suffix(next((item for item in wrappers if item.get("id") == cell.get("target")), ET.Element("object"))),
            )
    if end_id:
        admin.spread_end_fan_in(wrappers, end_id, node_centres)

    by_key = {flow_suffix(wrapper): admin.wrapper_cell(wrapper) for wrapper in wrappers if flow_suffix(wrapper)}
    # Separate the three successful profile sources entering the same decision.
    for key, point in {
        "load-to-profile-result": (0.0, 0.45),
        "link-to-profile-result": (0.35, 0.0),
        "create-to-profile-result": (0.68, 0.0),
    }.items():
        set_entry(by_key[key], *point)
    return tree


def validate_domain(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    diagrams = root.findall("diagram")
    if len(diagrams) != 1:
        raise RuntimeError("Domain polished output must contain one page")
    cells = diagrams[0].findall(".//mxCell")
    ids = [cell.get("id", "") for cell in cells]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise RuntimeError("Domain output contains missing or duplicate cell IDs")
    components = [cell for cell in cells if domain_suffix(cell)]
    edges = [cell for cell in cells if cell.get("edge") == "1"]
    if len(components) != 15 or len(edges) != 15:
        raise RuntimeError(f"Domain expected 15/15, found {len(components)}/{len(edges)}")
    component_ids = {cell.get("id", "") for cell in components}
    for edge in edges:
        if edge.get("source") not in component_ids or edge.get("target") not in component_ids:
            raise RuntimeError(f"Detached domain connector {edge.get('id')}")
    return {"components": len(components), "connectors": len(edges)}


def validate_flowchart(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    diagrams = root.findall("diagram")
    if len(diagrams) != 1:
        raise RuntimeError("Google flow-chart polished output must contain one page")
    wrappers = diagrams[0].findall(".//object")
    ids = [wrapper.get("id", "") for wrapper in wrappers]
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers if wrapper.get("petakerjaKey")]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise RuntimeError("Google flow-chart output contains missing or duplicate IDs")
    if any(count > 1 for count in Counter(keys).values()):
        raise RuntimeError("Google flow-chart output contains duplicate stable keys")

    components: dict[str, str] = {}
    edges: list[ET.Element] = []
    for wrapper in wrappers:
        cell = admin.wrapper_cell(wrapper)
        suffix = flow_suffix(wrapper)
        if cell.get("vertex") == "1" and suffix and suffix not in FLOW_NONINTERACTIVE:
            components[wrapper.get("id", "")] = suffix
        elif cell.get("edge") == "1":
            edges.append(wrapper)
    if len(components) != 23 or len(edges) != 27:
        raise RuntimeError(f"Google flow expected 23/27, found {len(components)}/{len(edges)}")

    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for wrapper in edges:
        cell = admin.wrapper_cell(wrapper)
        source, target = cell.get("source", ""), cell.get("target", "")
        if source not in components or target not in components:
            raise RuntimeError(f"Detached flow connector {wrapper.get('id')}")
        outgoing[source].append(target)
        incoming[target].append(source)
        style = cell.get("style", "")
        if "endArrow=classic" not in style or "endFill=1" not in style:
            raise RuntimeError(f"Non-classic flow connector {wrapper.get('id')}")

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
        raise RuntimeError("Google flow-chart contains unreachable components")

    reaches_end: set[str] = set()
    queue = deque([by_key["end"]])
    while queue:
        current = queue.popleft()
        if current in reaches_end:
            continue
        reaches_end.add(current)
        queue.extend(incoming[current])
    if reaches_end != set(components):
        raise RuntimeError("Google flow-chart contains a route that cannot reach End")
    return {"components": len(components), "connectors": len(edges)}


def write_xml(tree: ET.ElementTree, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def audit(path: Path) -> dict[str, object]:
    strict = json.loads(admin.run_checked([admin.DRAWIO_AI, "validate", str(path), "--strict"]).stdout)
    if not strict.get("ok"):
        raise RuntimeError(f"Strict validation failed for {path.name}")
    result = json.loads(admin.run_checked([admin.DRAWIO_AI, "audit", str(path)]).stdout)
    advice = list(result.get("advice", []))
    actionable = [
        item for item in advice
        if not ("Font sizes too large [24]" in item and "hero title" in item)
    ]
    if actionable:
        raise RuntimeError(f"Unresolved aesthetic advice for {path.name}: {actionable}")
    return result


def render(source: Path, svg: Path, png: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="petakerja-core-polish-") as temp_dir:
        light_source = Path(temp_dir) / source.name
        admin.light_render_copy(source, light_source)
        admin.run_checked([admin.DRAWIO_AI, "render", str(light_source), "-o", str(png), "--scale", "2"])
    admin.run_checked([
        str(admin.DRAWIO), "--export", "--format", "svg", "--page-index", "0",
        "--output", str(svg), str(source),
    ])


def main() -> None:
    for path in (DOMAIN_SOURCE, FLOW_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)
    if not admin.DRAWIO_AI:
        raise RuntimeError("drawio-ai is unavailable; install sparklabx/drawio-ai-kit v1.0.0")

    before = {str(path): sha256(path) for path in (DOMAIN_SOURCE, FLOW_SOURCE)}
    EDITOR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DOMAIN_SOURCE, DOMAIN_EDITOR_ORIGINAL)
    shutil.copy2(FLOW_SOURCE, FLOW_EDITOR_ORIGINAL)

    domain_tree = polish_domain()
    flow_tree = polish_flowchart()
    write_xml(domain_tree, DOMAIN_POLISHED)
    write_xml(flow_tree, FLOW_POLISHED)

    domain_structure = validate_domain(DOMAIN_POLISHED)
    flow_structure = validate_flowchart(FLOW_POLISHED)
    domain_audit = audit(DOMAIN_POLISHED)
    flow_audit = audit(FLOW_POLISHED)

    shutil.copy2(DOMAIN_POLISHED, DOMAIN_EDITOR)
    shutil.copy2(FLOW_POLISHED, FLOW_EDITOR)
    render(DOMAIN_POLISHED, DOMAIN_POLISHED_SVG, DOMAIN_POLISHED_PNG)
    render(FLOW_POLISHED, FLOW_POLISHED_SVG, FLOW_POLISHED_PNG)

    after = {str(path): sha256(path) for path in (DOMAIN_SOURCE, FLOW_SOURCE)}
    if before != after:
        raise RuntimeError("An authoritative Original source changed during generation")

    print(json.dumps({
        "originalHashes": before,
        "domain": {
            **domain_structure,
            "drawio": str(DOMAIN_POLISHED),
            "svg": str(DOMAIN_POLISHED_SVG),
            "png": str(DOMAIN_POLISHED_PNG),
            "auditAdvice": domain_audit.get("advice", []),
        },
        "googleSignInFlowchart": {
            **flow_structure,
            "drawio": str(FLOW_POLISHED),
            "svg": str(FLOW_POLISHED_SVG),
            "png": str(FLOW_POLISHED_PNG),
            "auditAdvice": flow_audit.get("advice", []),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
