#!/usr/bin/env python3
"""Generate the editable bilingual V2 Georouting Draw.io collection.

The layout system is intentionally derived from the project templates:

* Use-case actors are 70 x 140 and use cases are 62 px high.
* Sequence actors, participants, activations, messages and fragments are read
  from the supplied template; lanes use a fixed 200 px pitch and 50 px rows.
* Flowchart processes and decisions use a 10 px grid and orthogonal edges.

Only files below ``assets/editor/v2-georouting`` are owned by this generator.
The historical vanilla diagrams are comparison assets and must remain untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "editor" / "v2-georouting"
SEQUENCE_TEMPLATE = ROOT / "templates" / "Sequence Diagram Template.drawio"
STAMP = "2026-07-19"


def template_style(predicate, description: str) -> str:
    """Return a required style from the canonical sequence template."""
    if not SEQUENCE_TEMPLATE.exists():
        raise RuntimeError(f"Missing sequence template: {SEQUENCE_TEMPLATE}")
    for cell in ET.parse(SEQUENCE_TEMPLATE).getroot().findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError(f"Sequence template is missing its required {description} style")


def strip_style_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


SEQUENCE_ACTOR = template_style(lambda _cell, style: "shape=umlActor" in style, "actor")
SEQUENCE_PARTICIPANT = template_style(lambda _cell, style: "shape=umlLifeline" in style, "participant")
SEQUENCE_ACTIVATION = template_style(
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style,
    "activation",
)
SEQUENCE_FRAME = template_style(lambda _cell, style: "shape=umlFrame" in style, "combined fragment")
SEQUENCE_ACTOR_STEM = template_style(
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;") and cell.find("mxGeometry") is not None,
    "actor stem",
)
TEMPLATE_CALL = template_style(
    lambda cell, style: cell.get("edge") == "1" and "startArrow=classic" in style,
    "synchronous call",
)
TEMPLATE_RETURN = template_style(
    lambda cell, style: cell.get("edge") == "1" and "endArrow=open" in style and "dashed=1" in style,
    "return message",
)
TEMPLATE_DIVIDER = template_style(
    lambda cell, style: cell.get("edge") == "1" and "endArrow=none" in style and "dashed=1" in style,
    "fragment divider",
)
SEQUENCE_CALL = strip_style_properties(
    TEMPLATE_CALL,
    (
        "startArrow", "startFill", "endArrow", "endFill", "entryX", "entryY",
        "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy",
    ),
) + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=10;labelBackgroundColor=none;"
SEQUENCE_RETURN = strip_style_properties(
    TEMPLATE_RETURN,
    ("entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
) + ";strokeWidth=1;fontSize=10;labelBackgroundColor=none;"


# Template-derived geometry. Keep these constants explicit so future diagram
# edits cannot silently drift back to oversized, free-form components.
GRID = 10
ACTOR_W, ACTOR_H = 70, 140
USECASE_H = 62
PARTICIPANT_W, PARTICIPANT_H = 100, 60
LIFELINE_W = 10
PROCESS_W, PROCESS_H = 220, 60
DECISION_W, DECISION_H = 180, 100
CARD_W, CARD_H = 240, 80
PAGE_MARGIN = 50


TITLE = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=24;fontStyle=1;fontColor=light-dark(#172033,#e8edf7);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;fontFamily=Arial;fontSize=12;fontColor=light-dark(#596579,#aeb8c8);"
TEXT = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontFamily=Arial;fontSize=12;fontColor=light-dark(#172033,#e8edf7);"
NOTE = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#fff8df,#3d3418);strokeColor=light-dark(#d9a928,#bd8b16);fontColor=light-dark(#5f4700,#ffe8a3);fontFamily=Arial;fontSize=11;align=left;verticalAlign=middle;spacing=8;"
BOX_BLUE = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#eaf3ff,#17293f);strokeColor=light-dark(#4d8dd8,#69a8ef);fontColor=light-dark(#17375e,#e7f2ff);fontFamily=Arial;fontSize=12;spacing=6;"
BOX_CYAN = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#e4f8fa,#17363a);strokeColor=light-dark(#32a6b2,#55d1dc);fontColor=light-dark(#134c53,#dffcff);fontFamily=Arial;fontSize=12;spacing=6;"
BOX_GREEN = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#ebf8ef,#183324);strokeColor=light-dark(#48a868,#61cc83);fontColor=light-dark(#194a2c,#e4ffec);fontFamily=Arial;fontSize=12;spacing=6;"
BOX_PURPLE = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#f1eafe,#302242);strokeColor=light-dark(#8c68c8,#ae8ae8);fontColor=light-dark(#43276a,#f2e8ff);fontFamily=Arial;fontSize=12;spacing=6;"
BOX_ORANGE = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#fff2df,#3a2a16);strokeColor=light-dark(#d28b2e,#e0a24e);fontColor=light-dark(#633d0f,#fff0d4);fontFamily=Arial;fontSize=12;spacing=6;"
BOX_GRAY = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=light-dark(#f4f6f8,#242932);strokeColor=light-dark(#8a96a8,#727f92);fontColor=light-dark(#283345,#edf1f7);fontFamily=Arial;fontSize=12;spacing=6;"
GROUP = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=light-dark(#7f8a9a,#566173);strokeWidth=1.5;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=13;fontStyle=1;verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;strokeColor=light-dark(#2d72d2,#7ab7ff);fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=12;fontStyle=1;"
ACTOR_MUTED = ACTOR.replace("#2d72d2,#7ab7ff", "#687385,#9aa6b8")
USECASE = "ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontColor=light-dark(#172033,#e8edf7);fillColor=light-dark(#ffffff,#17293f);strokeColor=light-dark(#4b5563,#69a8ef);strokeWidth=1.25;"
PROCESS = "whiteSpace=wrap;html=1;strokeWidth=1.5;rounded=0;fillColor=light-dark(#edf4ff,#17283f);strokeColor=light-dark(#4f86c6,#6da9ef);fontColor=light-dark(#17375e,#e7f2ff);fontFamily=Arial;fontSize=12;spacing=6;"
DECISION = "shape=mxgraph.flowchart.decision;whiteSpace=wrap;html=1;strokeWidth=1.5;fillColor=light-dark(#fff2df,#392a18);strokeColor=light-dark(#d18a2b,#e5a651);fontColor=light-dark(#59370f,#ffefd0);fontFamily=Arial;fontSize=11;"
TERMINATOR = "shape=mxgraph.flowchart.start_1;whiteSpace=wrap;html=1;strokeWidth=1.5;fillColor=light-dark(#e9f8ef,#193427);strokeColor=light-dark(#3f9b62,#61cf87);fontColor=light-dark(#18482b,#e4ffec);fontFamily=Arial;fontSize=12;fontStyle=1;"
CLASS_BOX = "swimlane;fontStyle=1;align=left;verticalAlign=top;startSize=28;horizontal=1;collapsible=0;whiteSpace=wrap;html=1;rounded=0;fillColor=light-dark(#eaf3ff,#17283f);strokeColor=light-dark(#4f86c6,#6da9ef);fontColor=light-dark(#17375e,#e7f2ff);fontFamily=Arial;fontSize=11;spacingLeft=7;spacingTop=5;"
TABLE_BOX = CLASS_BOX.replace("#eaf3ff,#17283f", "#eee8fb,#2d2140").replace("#4f86c6,#6da9ef", "#815ebc,#a989de").replace("#17375e,#e7f2ff", "#402665,#f2e9ff")
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=light-dark(#596579,#aeb8c8);fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
ASSOCIATION = "rounded=0;html=1;endArrow=none;startArrow=none;strokeColor=light-dark(#596579,#aeb8c8);strokeWidth=1.25;"
INCLUDE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=8 4;endArrow=open;endFill=0;strokeColor=light-dark(#596579,#aeb8c8);fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
SEQUENCE_LABEL = "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=10;fontColor=light-dark(#172033,#ededed);"
SEQUENCE_OPERAND = SEQUENCE_LABEL + "align=left;fontStyle=2;"


@dataclass(frozen=True)
class Page:
    filename: str
    page_id: str
    name: str
    width: int
    height: int
    title_en: str
    title_ms: str
    subtitle_en: str
    subtitle_ms: str


def attrs_for(label_en: str, label_ms: str, key: str, node_ids: str = "", table_name: str = "", hotspots: str = "") -> dict[str, str]:
    attrs = {"label": label_en, "labelEn": label_en, "labelMs": label_ms, "petakerjaKey": key}
    if node_ids:
        attrs.update({"nodeIds": node_ids, "component": "1"})
    if table_name:
        attrs["tableName"] = table_name
    if hotspots:
        attrs["uiHotspots"] = hotspots
    return attrs


def add_vertex(root: ET.Element, identifier: str, key: str, label_en: str, label_ms: str,
               x: float, y: float, width: float, height: float, style: str,
               node_ids: str = "", table_name: str = "", hotspots: str = "") -> str:
    wrapper = ET.SubElement(root, "object", {"id": identifier, **attrs_for(label_en, label_ms, key, node_ids, table_name, hotspots)})
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": style})
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return identifier


def add_edge(root: ET.Element, identifier: str, key: str, source: str, target: str,
             label_en: str = "", label_ms: str = "", style: str = EDGE,
             simple_en: str | None = None, simple_ms: str | None = None,
             code_en: str | None = None, code_ms: str | None = None) -> str:
    wrapper_attrs = {"id": identifier, **attrs_for(label_en, label_ms, key)}
    if simple_en is not None:
        wrapper_attrs.update({
            "simpleLabelEn": simple_en, "simpleLabelMs": simple_ms or simple_en,
            "codeLabelEn": code_en or simple_en, "codeLabelMs": code_ms or code_en or simple_ms or simple_en,
            "message": "1",
        })
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "edge": "1", "source": source, "target": target, "style": style})
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    return identifier


def add_edge_points(root: ET.Element, identifier: str, key: str, source: str, target: str,
                    points: list[tuple[float, float]], label_en: str = "", label_ms: str = "",
                    style: str = EDGE) -> str:
    wrapper = ET.SubElement(root, "object", {"id": identifier, **attrs_for(label_en, label_ms, key)})
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "edge": "1", "source": source, "target": target, "style": style})
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    array = ET.SubElement(geometry, "Array", {"as": "points"})
    for x, y in points:
        ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})
    return identifier


def add_text(root: ET.Element, identifier: str, key: str, en: str, ms: str,
             x: float, y: float, width: float, height: float, style: str = TEXT) -> str:
    return add_vertex(root, identifier, key, en, ms, x, y, width, height, style)


def create_page(page: Page) -> tuple[ET.Element, ET.Element]:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer", "agent": "PetaKerja V2 Georouting Generator",
        "version": "27.0.2", "compressed": "false", "pages": "1",
        "petakerjaProjectionLanguage": "en", "petakerjaSequenceLabelMode": "simple",
        "petakerjaLayoutStandard": "project-template-v2",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": page.page_id, "name": page.name})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(page.width), "dy": str(page.height), "grid": "1", "gridSize": str(GRID), "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(page.width), "pageHeight": str(page.height), "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    add_vertex(root, f"{page.page_id}-title", "title", page.title_en, page.title_ms, PAGE_MARGIN, 25, page.width - 2 * PAGE_MARGIN, 38, TITLE)
    add_vertex(root, f"{page.page_id}-subtitle", "subtitle", page.subtitle_en, page.subtitle_ms, PAGE_MARGIN, 65, page.width - 2 * PAGE_MARGIN, 42, SUBTITLE)
    return mxfile, root


def write(page: Page, mxfile: ET.Element) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(OUTPUT / page.filename, encoding="utf-8", xml_declaration=False)


def base_note(root: ET.Element, page: Page) -> None:
    add_text(root, f"{page.page_id}-runtime", "runtime-status",
             f"Runtime verified {STAMP}: Valhalla enabled and available; shared cache available; Nominatim disabled.",
             f"Runtime disahkan {STAMP}: Valhalla diaktifkan dan tersedia; cache bersama tersedia; Nominatim dinyahaktifkan.",
             PAGE_MARGIN, page.height - 58, page.width - 2 * PAGE_MARGIN, 36, NOTE)


def add_class(root: ET.Element, identifier: str, key: str, title_en: str, title_ms: str,
              body_en: str, body_ms: str, x: int, y: int, width: int, height: int,
              node_ids: str, table_name: str = "") -> str:
    return add_vertex(root, identifier, key, f"{title_en}\n{body_en}", f"{title_ms}\n{body_ms}", x, y, width, height,
                      TABLE_BOX if table_name else CLASS_BOX, node_ids, table_name)


def generate_usecase() -> None:
    page = Page("usecase.drawio", "v2_geo_usecase", "V2 Georouting Use Cases", 1600, 1120,
                "PetaKerja V2 Georouting Use Case Diagram", "Rajah Kes Guna Georouting V2 PetaKerja",
                "Road routing, analytical travel tools, workplace navigation and explicit fallback behaviour.",
                "Penghalaan jalan, alat analisis perjalanan, navigasi tempat kerja dan tingkah laku sandaran yang jelas.")
    mxfile, root = create_page(page)
    user = add_vertex(root, "uc-user", "actor-user", "User", "Pengguna", 55, 265, ACTOR_W, ACTOR_H, ACTOR, "pengguna")
    seeker = add_vertex(root, "uc-seeker", "actor-seeker", "Signed-in\njob seeker", "Pencari kerja\nyang log masuk", 55, 690, ACTOR_W, ACTOR_H, ACTOR, "pengguna")
    valhalla = add_vertex(root, "uc-valhalla", "actor-valhalla", "Valhalla\n(enabled)", "Valhalla\n(diaktifkan)", 1475, 265, ACTOR_W, ACTOR_H, ACTOR, "valhalla")
    nominatim = add_vertex(root, "uc-nominatim", "actor-nominatim", "Nominatim\n(disabled)", "Nominatim\n(dinyahaktifkan)", 1475, 650, ACTOR_W, ACTOR_H, ACTOR_MUTED, "nominatim")
    add_vertex(root, "uc-boundary", "system-boundary", "PetaKerja georouting", "Georouting PetaKerja", 165, 125, 1270, 900, GROUP)

    specs = [
        ("set-endpoints", "Set A and B", "Tetapkan A dan B", 235, 190, 250, "geo-navigation-manager"),
        ("gps", "Use current GPS location", "Guna lokasi GPS semasa", 535, 190, 250, "geo-navigation-manager"),
        ("profile", "Choose drive, walk or cycle", "Pilih pandu, jalan atau basikal", 835, 190, 250, "geo-navigation-manager"),
        ("route", "Calculate road route", "Kira laluan jalan", 1135, 190, 250, "geo-gateway"),
        ("alternatives", "Review route alternatives", "Semak alternatif laluan", 235, 350, 250, "geo-route-renderer"),
        ("appearance", "Adjust route appearance", "Laraskan rupa laluan", 535, 350, 250, "route-appearance-manager"),
        ("preview", "Preview journey and maneuvers", "Pratonton perjalanan dan arahan", 835, 350, 250, "geo-route-renderer"),
        ("cache", "Reuse normalized cached result", "Guna semula hasil cache ternormal", 1135, 350, 250, "geo-route-cache"),
        ("matrix", "Compare travel times", "Bandingkan masa perjalanan", 235, 535, 250, "geo-navigation-manager"),
        ("isochrone", "Show reachable area", "Paparkan kawasan boleh dicapai", 535, 535, 250, "geo-navigation-manager"),
        ("boundary-search", "Search within boundary", "Cari dalam sempadan", 835, 535, 250, "geo-navigation-manager"),
        ("studio", "Open context in Geo Studio", "Buka konteks dalam Studio Geo", 1135, 535, 250, "geo-studio"),
        ("workplace", "Route to workplace", "Halakan ke tempat kerja", 465, 760, 280, "job-manager"),
        ("fallback", "Show labelled straight-line fallback", "Paparkan sandaran garis lurus berlabel", 855, 760, 280, "geo-gateway"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, x, y, width, node in specs:
        ids[key] = add_vertex(root, f"uc-{key}", f"usecase/{key}", en, ms, x, y, width, USECASE_H, USECASE, node)

    for index, key in enumerate(("set-endpoints", "alternatives", "matrix"), 1):
        add_edge(root, f"uc-user-{index}", f"relation/user-{key}", user, ids[key], style=ASSOCIATION)
    add_edge(root, "uc-seeker-workplace", "relation/seeker-workplace", seeker, ids["workplace"], style=ASSOCIATION)
    add_edge(root, "uc-route-valhalla", "relation/route-valhalla", ids["route"], valhalla, style=ASSOCIATION)
    add_edge(root, "uc-boundary-nominatim", "relation/boundary-nominatim", ids["boundary-search"], nominatim, style=ASSOCIATION + "dashed=1;")
    relations = [
        ("gps", "set-endpoints", "extend", "lanjutan"), ("route", "set-endpoints", "include", "termasuk"),
        ("route", "profile", "include", "termasuk"), ("alternatives", "route", "extend", "lanjutan"),
        ("appearance", "route", "extend", "lanjutan"), ("preview", "route", "extend", "lanjutan"),
        ("route", "cache", "include", "termasuk"), ("workplace", "route", "include when routable", "termasuk apabila boleh dihala"),
        ("fallback", "route", "extend on failure", "lanjutan apabila gagal"), ("studio", "boundary-search", "extend", "lanjutan"),
    ]
    for index, (source, target, en, ms) in enumerate(relations, 1):
        # The object label is HTML-enabled by Draw.io. Keep the angle brackets
        # as entities until Draw.io's render pass so the stereotype is visible.
        add_edge(root, f"uc-rel-{index}", f"relation/{source}-{target}", ids[source], ids[target],
                 f"&lt;&lt;{en}&gt;&gt;", f"&lt;&lt;{ms}&gt;&gt;", INCLUDE)
    base_note(root, page)
    write(page, mxfile)


def flow_edge(root: ET.Element, index: int, source: str, target: str, en: str = "", ms: str = "", style: str = EDGE) -> None:
    add_edge(root, f"flow-edge-{index}", f"flow/edge-{index}", source, target, en, ms, style)


def generate_flowchart() -> None:
    page = Page("map-flowchart.drawio", "v2_geo_map_flowchart", "V2 Explore and Navigate Map", 1480, 1340,
                "Explore and Navigate the Map — V2 Georouting", "Teroka dan Navigasi Peta — Georouting V2",
                "A template-aligned flow from map readiness to route rendering and optional analysis.",
                "Aliran sejajar templat daripada kesediaan peta kepada pemaparan laluan dan analisis pilihan.")
    mxfile, root = create_page(page)
    nodes: dict[str, str] = {}
    specs = [
        ("start", "Start", "Mula", 650, 125, 180, 50, TERMINATOR, ""),
        ("open", "Open Malaysia map workspace", "Buka ruang kerja peta Malaysia", 630, 215, PROCESS_W, PROCESS_H, PROCESS, "mypeta-app"),
        ("ready", "MapLibre style ready?", "Gaya MapLibre sedia?", 650, 325, DECISION_W, DECISION_H, DECISION, "maplibre-gl"),
        ("tools", "Mount Map Tools and A–B Navigator", "Pasang Alat Peta dan Navigasi A–B", 630, 485, PROCESS_W, PROCESS_H, PROCESS, "map-tools-manager"),
        ("endpoints", "Choose A and B", "Pilih A dan B", 630, 585, PROCESS_W, PROCESS_H, PROCESS, "geo-navigation-manager"),
        ("both", "Both endpoints available?", "Kedua-dua titik tersedia?", 650, 700, DECISION_W, DECISION_H, DECISION, "geo-navigation-manager"),
        ("route", "POST /api/geo/route", "POST /api/geo/route", 630, 860, PROCESS_W, PROCESS_H, PROCESS, "geo-api"),
        ("provider", "Valhalla route available?", "Laluan Valhalla tersedia?", 650, 975, DECISION_W, DECISION_H, DECISION, "geo-gateway"),
        ("render", "Render route, ETA, alternatives and maneuvers", "Papar laluan, ETA, alternatif dan arahan", 370, 1135, 280, 70, BOX_GREEN, "geo-route-renderer,maplibre-gl"),
        ("fallback", "Show straight-line warning; no ETA or maneuvers", "Papar amaran garis lurus; tiada ETA atau arahan", 830, 1135, 280, 70, BOX_ORANGE, "geo-gateway"),
        ("finish", "Interactive route", "Laluan interaktif", 650, 1240, 180, 50, TERMINATOR, "geo-navigation-manager"),
        ("wait", "Keep base map usable; await style.load", "Kekalkan peta asas; tunggu style.load", 1000, 340, 280, 70, BOX_GRAY, "map-manager"),
        ("idle", "Keep Navigator open", "Kekalkan Navigator terbuka", 200, 715, 250, 70, BOX_GRAY, "map-tools-manager"),
        ("analysis", "Optional matrix, isochrone, boundary or Geo Studio", "Matriks, isokron, sempadan atau Studio Geo pilihan", 1010, 560, 300, 90, BOX_PURPLE, "geo-navigation-manager"),
    ]
    for key, en, ms, x, y, w, h, style, node in specs:
        nodes[key] = add_vertex(root, f"flow-{key}", f"flow/{key}", en, ms, x, y, w, h, style, node)
    links = [
        ("start", "open", "", ""), ("open", "ready", "", ""), ("ready", "tools", "Yes", "Ya"),
        ("ready", "wait", "No", "Tidak"), ("wait", "ready", "style.load", "style.load"),
        ("tools", "endpoints", "", ""), ("tools", "analysis", "optional", "pilihan"),
        ("endpoints", "both", "", ""), ("both", "route", "Yes", "Ya"), ("both", "idle", "No", "Tidak"),
        ("idle", "endpoints", "select", "pilih"), ("route", "provider", "", ""),
        ("provider", "render", "Yes", "Ya"), ("provider", "fallback", "No", "Tidak"),
        ("render", "finish", "", ""), ("fallback", "finish", "", ""),
    ]
    for index, (source, target, en, ms) in enumerate(links, 1):
        style = INCLUDE if source == "tools" and target == "analysis" else EDGE
        flow_edge(root, index, nodes[source], nodes[target], en, ms, style)
    base_note(root, page)
    write(page, mxfile)


@dataclass(frozen=True)
class SequenceParticipant:
    header: str
    lifeline: str
    center_x: float


def add_participants(
    root: ET.Element,
    prefix: str,
    participants: list[tuple[str, str, str, str]],
    width: int,
    lifeline_bottom: int,
) -> dict[str, SequenceParticipant]:
    centers = [90 + 200 * index for index in range(len(participants))]
    if centers and centers[-1] + PARTICIPANT_W / 2 > width - 20:
        raise ValueError(f"{prefix}: participant grid exceeds the {width}px page")
    lifeline_y = 185
    lifeline_h = lifeline_bottom - lifeline_y
    result: dict[str, SequenceParticipant] = {}
    for index, (key, en, ms, node_ids) in enumerate(participants):
        center_x = centers[index]
        if index == 0:
            header = add_vertex(root, f"{prefix}-participant-{key}", f"{prefix}/participant-{key}", "", "",
                                center_x - 10, 127, 20, 40, SEQUENCE_ACTOR, node_ids)
            add_text(root, f"{prefix}-participant-{key}-label", f"{prefix}/participant-{key}-label", en, ms,
                     center_x - 70, 166, 140, 18, SEQUENCE_LABEL)
            add_vertex(root, f"{prefix}-participant-{key}-stem", f"{prefix}/participant-{key}-stem", "", "",
                       center_x - 5, 167, 10, 18, SEQUENCE_ACTOR_STEM)
        else:
            header = add_vertex(root, f"{prefix}-participant-{key}", f"{prefix}/participant-{key}", en, ms,
                                center_x - PARTICIPANT_W / 2, 125, PARTICIPANT_W, PARTICIPANT_H,
                                SEQUENCE_PARTICIPANT, node_ids)
        lifeline = add_vertex(root, f"{prefix}-lifeline-{key}", f"{prefix}/lifeline-{key}", "", "",
                              center_x - LIFELINE_W / 2, lifeline_y, LIFELINE_W, lifeline_h,
                              SEQUENCE_ACTIVATION, node_ids)
        result[key] = SequenceParticipant(header, lifeline, center_x)
    return result


def add_fragment(
    root: ET.Element,
    prefix: str,
    key: str,
    kind: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> str:
    return add_vertex(root, f"{prefix}-fragment-{key}", f"{prefix}/fragment-{key}", kind, kind,
                      x, y, width, height, SEQUENCE_FRAME)


def add_fragment_divider(
    root: ET.Element,
    prefix: str,
    key: str,
    y: float,
    x1: float,
    x2: float,
) -> None:
    wrapper = ET.SubElement(root, "object", {
        "id": f"{prefix}-divider-{key}", "label": "", "labelEn": "", "labelMs": "",
        "petakerjaKey": f"{prefix}/divider-{key}", "fragmentDivider": "1",
    })
    divider_style = strip_style_properties(
        TEMPLATE_DIVIDER,
        ("entryX", "entryY", "entryDx", "entryDy", "exitX", "exitY", "exitDx", "exitDy"),
    ) + ";strokeWidth=1;"
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "edge": "1", "style": divider_style})
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(geometry, "mxPoint", {"x": str(x1), "y": str(y), "as": "sourcePoint"})
    ET.SubElement(geometry, "mxPoint", {"x": str(x2), "y": str(y), "as": "targetPoint"})


def add_operand(
    root: ET.Element,
    prefix: str,
    key: str,
    en: str,
    ms: str,
    x: float,
    y: float,
    width: float,
) -> None:
    add_text(root, f"{prefix}-operand-{key}", f"{prefix}/operand-{key}", en, ms,
             x, y, width, 18, SEQUENCE_OPERAND)


def add_messages(root: ET.Element, prefix: str, participants: dict[str, SequenceParticipant],
                 rows: list[tuple[str, str, str, str, str, str]], start_y: int = 245, row_gap: int = 50,
                 row_positions: list[int] | None = None) -> None:
    lifeline_y = 185
    lifeline_h = max(1, int(next(iter(participants.values())).center_x * 0 + 1000))
    if row_positions is not None and len(row_positions) != len(rows):
        raise ValueError(f"{prefix}: expected {len(rows)} row positions, received {len(row_positions)}")
    # The normalized anchor is based on each actual lifeline geometry. All
    # messages remain horizontal and every row owns one unambiguous y level.
    for index, (source, target, simple_en, simple_ms, code_en, code_ms) in enumerate(rows, 1):
        y = row_positions[index - 1] if row_positions is not None else start_y + (index - 1) * row_gap
        source_p, target_p = participants[source], participants[target]
        activation = root.find(f".//object[@id='{source_p.lifeline}']/mxCell/mxGeometry")
        actual_h = float(activation.get("height", "1000")) if activation is not None else lifeline_h
        anchor_y = min(0.96, max(0.04, (y - lifeline_y) / actual_h))
        left_to_right = source_p.center_x < target_p.center_x
        exit_x, entry_x = (1, 0) if left_to_right else (0, 1)
        returning = simple_en.lower().startswith(("return", "render", "display", "show", "reuse", "report", "explain"))
        style = (SEQUENCE_RETURN if returning else SEQUENCE_CALL) + (
            f"exitX={exit_x};exitY={anchor_y:.4f};exitDx=0;exitDy=0;exitPerimeter=0;"
            f"entryX={entry_x};entryY={anchor_y:.4f};entryDx=0;entryDy=0;entryPerimeter=0;"
        )
        add_edge(root, f"{prefix}-message-{index}", f"{prefix}/message-{index}", source_p.lifeline, target_p.lifeline,
                 simple_en, simple_ms, style, simple_en, simple_ms, code_en, code_ms)


def generate_route_sequence() -> None:
    page = Page("route-sequence.drawio", "v2_geo_route_sequence", "V2 A-to-B Route Sequence", 1760, 1320,
                "A-to-B Road Routing Sequence — V2", "Jujukan Penghalaan Jalan A-ke-B — V2",
                "Cache hit, provider success and explicit straight-line fallback on separate message rows.",
                "Cache ditemui, kejayaan penyedia dan sandaran garis lurus yang jelas pada baris mesej berasingan.")
    mxfile, root = create_page(page)
    p = add_participants(root, "route", [
        ("user", "User", "Pengguna", "pengguna"), ("tools", "Map Tools UI", "UI Alat Peta", "map-tools-manager"),
        ("nav", "GeoNavigation Manager", "Pengurus Navigasi Geo", "geo-navigation-manager"),
        ("client", "Geo client", "Klien Geo", "geo-service"), ("api", "Express Geo API", "API Geo Express", "geo-api"),
        ("gateway", "GeoGateway", "GeoGateway", "geo-gateway"), ("cache", "Route cache", "Cache laluan", "geo-route-cache"),
        ("valhalla", "Valhalla", "Valhalla", "valhalla"), ("renderer", "MapLibre renderer", "Pemapar MapLibre", "geo-route-renderer,maplibre-gl"),
    ], page.width, 1035)
    add_fragment(root, "route", "cache", "alt", 630, 515, 920, 345)
    add_operand(root, "route", "cache-hit", "Cached route exists", "Laluan cache wujud", 645, 530, 230)
    add_fragment_divider(root, "route", "cache", 580, 630, 1550)
    add_operand(root, "route", "cache-miss", "Cache miss", "Cache tiada", 645, 585, 180)
    add_fragment(root, "route", "provider", "alt", 630, 630, 920, 225)
    add_operand(root, "route", "provider-success", "Valhalla route succeeds", "Laluan Valhalla berjaya", 645, 645, 260)
    add_fragment_divider(root, "route", "provider", 800, 630, 1550)
    add_operand(root, "route", "provider-failure", "Provider unavailable or fails", "Penyedia tidak tersedia atau gagal", 645, 805, 300)
    rows = [
        ("user", "tools", "Choose A, B and profile", "Pilih A, B dan profil", "selectEndpoints(); setProfile()", "selectEndpoints(); setProfile()"),
        ("tools", "nav", "Recalculate route", "Kira semula laluan", "recalculate()", "recalculate()"),
        ("nav", "client", "Request route alternatives", "Minta alternatif laluan", "calculateGeoRoute(...) ", "calculateGeoRoute(...)"),
        ("client", "api", "POST route request", "POST permintaan laluan", "POST /api/geo/route", "POST /api/geo/route"),
        ("api", "gateway", "Validate coordinates and profile", "Sahkan koordinat dan profil", "assertMalaysiaLocation(); assertRouteProfile()", "assertMalaysiaLocation(); assertRouteProfile()"),
        ("gateway", "cache", "Read normalized route cache", "Baca cache laluan ternormal", "readCache('geo_route_cache')", "readCache('geo_route_cache')"),
        ("cache", "gateway", "Reuse cache hit", "Guna semula cache ditemui", "geo_touch_cache()", "geo_touch_cache()"),
        ("gateway", "valhalla", "Request route on cache miss", "Minta laluan apabila cache tiada", "POST /route", "POST /route"),
        ("valhalla", "gateway", "Return geometry, ETA and maneuvers", "Pulangkan geometri, ETA dan arahan", "trip + alternates", "trip + alternates"),
        ("gateway", "cache", "Write normalized route", "Simpan laluan ternormal", "writeCache('geo_route_cache')", "writeCache('geo_route_cache')"),
        ("gateway", "api", "Return routed response", "Pulangkan respons laluan", "estimateKind: 'routed'", "estimateKind: 'routed'"),
        ("api", "client", "Return fallback when provider fails", "Pulangkan sandaran apabila penyedia gagal", "estimateKind: 'straight-line'", "estimateKind: 'straight-line'"),
        ("client", "nav", "Return route and warning", "Pulangkan laluan dan amaran", "{ route, warning? }", "{ route, warning? }"),
        ("nav", "renderer", "Render deterministic layer order", "Papar susunan lapisan deterministik", "setRoute(); fitBounds()", "setRoute(); fitBounds()"),
        ("renderer", "user", "Display route or labelled estimate", "Paparkan laluan atau anggaran berlabel", "MapLibre layers + status", "Lapisan MapLibre + status"),
    ]
    add_messages(root, "route", p, rows, 245, 50)
    add_text(root, "route-fallback-note", "route/fallback-note", "Fallback has no driving ETA, maneuvers or navigable-route claim.", "Sandaran tiada ETA pemanduan, arahan atau dakwaan laluan navigasi.", 960, 1080, 700, 55, NOTE)
    base_note(root, page)
    write(page, mxfile)


def generate_travel_sequence() -> None:
    page = Page("travel-analysis-sequence.drawio", "v2_geo_travel_analysis_sequence", "V2 Travel Analysis Sequence", 1760, 1450,
                "Travel Analysis Sequence — V2", "Jujukan Analisis Perjalanan — V2",
                "Matrix, isochrone and feature-gated boundary search use a consistent lifeline grid.",
                "Matriks, isokron dan carian sempadan berpagar ciri menggunakan grid talian hayat yang konsisten.")
    mxfile, root = create_page(page)
    p = add_participants(root, "travel", [
        ("user", "User", "Pengguna", "pengguna"), ("nav", "GeoNavigation Manager", "Pengurus Navigasi Geo", "geo-navigation-manager"),
        ("client", "Geo client", "Klien Geo", "geo-service"), ("api", "Express Geo API", "API Geo Express", "geo-api"),
        ("data", "Supabase / PostGIS", "Supabase / PostGIS", "supabase-db,job-location-resolution"),
        ("gateway", "GeoGateway", "GeoGateway", "geo-gateway"), ("valhalla", "Valhalla", "Valhalla", "valhalla"),
        ("nominatim", "Nominatim (gated)", "Nominatim (berpagar)", "nominatim"), ("map", "MapLibre", "MapLibre", "maplibre-gl"),
    ], page.width, 1230)
    add_fragment(root, "travel", "matrix", "opt", 30, 215, 1700, 485)
    add_operand(root, "travel", "matrix", "Compare visible destinations", "Bandingkan destinasi kelihatan", 45, 235, 300)
    add_fragment(root, "travel", "isochrone", "opt", 30, 720, 1700, 225)
    add_operand(root, "travel", "isochrone", "Show reachable-time area", "Paparkan kawasan masa boleh dicapai", 45, 740, 320)
    add_fragment(root, "travel", "boundary", "opt", 30, 965, 1700, 315)
    add_operand(root, "travel", "boundary", "Search within boundary", "Cari dalam sempadan", 45, 985, 250)
    add_fragment(root, "travel", "geocoder", "alt", 230, 1040, 1500, 225)
    add_operand(root, "travel", "geocoder-enabled", "Nominatim enabled", "Nominatim diaktifkan", 245, 1060, 220)
    add_fragment_divider(root, "travel", "geocoder", 1225, 230, 1730)
    add_operand(root, "travel", "geocoder-disabled", "Nominatim disabled — no provider or boundary query", "Nominatim dinyahaktifkan — tiada pertanyaan penyedia atau sempadan", 245, 1230, 520)
    rows = [
        ("user", "nav", "Compare visible POIs or jobs", "Bandingkan POI atau kerja kelihatan", "compareVisibleDestinations()", "compareVisibleDestinations()"),
        ("nav", "client", "Load bounded destinations", "Muat destinasi terbatas", "loadGeoDataset(name, bounds)", "loadGeoDataset(name, bounds)"),
        ("client", "api", "GET bounded dataset", "GET set data terbatas", "GET /api/geo/datasets/:name", "GET /api/geo/datasets/:name"),
        ("api", "data", "Read routable coordinates", "Baca koordinat yang boleh dihala", "pois | job_location_resolutions", "pois | job_location_resolutions"),
        ("data", "nav", "Return bounded candidates", "Pulangkan calon terbatas", "rows[]", "rows[]"),
        ("nav", "gateway", "Calculate 1-to-many matrix", "Kira matriks 1-ke-banyak", "POST /api/geo/matrix", "POST /api/geo/matrix"),
        ("gateway", "valhalla", "Request sources_to_targets", "Minta sources_to_targets", "POST /sources_to_targets", "POST /sources_to_targets"),
        ("valhalla", "nav", "Return distance and duration", "Pulangkan jarak dan tempoh", "distancesMeters; durationsSeconds", "distancesMeters; durationsSeconds"),
        ("nav", "map", "Render ranked destinations", "Papar destinasi tersusun", "render results", "papar hasil"),
        ("user", "nav", "Choose reachable-time area", "Pilih kawasan masa boleh dicapai", "showIsochrone(minutes)", "showIsochrone(minutes)"),
        ("nav", "gateway", "Calculate isochrone", "Kira isokron", "POST /api/geo/isochrone", "POST /api/geo/isochrone"),
        ("gateway", "valhalla", "Request reachable polygons", "Minta poligon boleh dicapai", "POST /isochrone", "POST /isochrone"),
        ("valhalla", "map", "Render returned polygons", "Papar poligon dipulangkan", "FeatureCollection", "FeatureCollection"),
        ("user", "nav", "Search within boundary", "Cari dalam sempadan", "showBoundary(place)", "showBoundary(place)"),
        ("nav", "nominatim", "Lookup boundary when enabled", "Cari sempadan apabila diaktifkan", "GET /api/geo/lookup", "GET /api/geo/lookup"),
        ("nominatim", "data", "Query POIs within boundary", "Tanya POI dalam sempadan", "geo_search_pois_within()", "geo_search_pois_within()"),
        ("data", "map", "Render matching POIs", "Papar POI sepadan", "FeatureCollection<Point>", "FeatureCollection<Point>"),
    ]
    add_messages(root, "travel", p, rows, 270, 50)
    add_text(root, "travel-gate-note", "travel/gate-note", "Matrix and isochrone are available; Nominatim boundary lookup is disabled.", "Matriks dan isokron tersedia; carian sempadan Nominatim dinyahaktifkan.", 980, 1310, 680, 52, NOTE)
    base_note(root, page)
    write(page, mxfile)


def generate_job_sequence() -> None:
    page = Page("job-route-sequence.drawio", "v2_geo_job_route_sequence", "V2 Route to Workplace Sequence", 1760, 1500,
                "Route to Workplace Sequence — V2", "Jujukan Laluan ke Tempat Kerja — V2",
                "Authentication, confidence, remote-work and geocoder gates remain visually distinct.",
                "Pengesahan, keyakinan, kerja jarak jauh dan pagar geokod kekal berbeza secara visual.")
    mxfile, root = create_page(page)
    p = add_participants(root, "jobroute", [
        ("user", "Job seeker", "Pencari kerja", "pengguna"), ("job", "JobFinder Manager", "Pengurus Pencari Kerja", "job-manager"),
        ("client", "Geo client", "Klien Geo", "geo-service"), ("api", "Authenticated API", "API disahkan", "geo-api"),
        ("resolver", "Location resolver", "Penyelesai lokasi", "job-location-resolver"), ("jobs", "scraped_jobs", "scraped_jobs", "job-entity"),
        ("resolution", "Location resolutions", "Penyelesaian lokasi", "job-location-resolution"), ("nominatim", "Nominatim (gated)", "Nominatim (berpagar)", "nominatim"),
        ("nav", "GeoNavigation Manager", "Pengurus Navigasi Geo", "geo-navigation-manager"),
    ], page.width, 1300)
    add_fragment(root, "jobroute", "resolution", "alt", 830, 430, 720, 540)
    add_operand(root, "jobroute", "resolution-cache", "Unexpired cached resolution", "Penyelesaian cache belum luput", 845, 450, 280)
    add_fragment_divider(root, "jobroute", "resolution", 575, 830, 1550)
    add_operand(root, "jobroute", "resolution-required", "Resolution required", "Penyelesaian diperlukan", 845, 580, 220)
    add_fragment(root, "jobroute", "remote", "alt", 830, 675, 320, 80)
    add_operand(root, "jobroute", "remote-job", "Remote job", "Kerja jarak jauh", 845, 690, 130)
    add_fragment_divider(root, "jobroute", "remote", 715, 830, 1150)
    add_operand(root, "jobroute", "onsite-job", "On-site or hybrid", "Di lokasi atau hibrid", 845, 720, 180)
    add_fragment(root, "jobroute", "geocoder", "alt", 830, 760, 720, 195)
    add_operand(root, "jobroute", "geocoder-enabled", "Nominatim enabled", "Nominatim diaktifkan", 845, 775, 190)
    add_fragment_divider(root, "jobroute", "geocoder", 925, 830, 1550)
    add_operand(root, "jobroute", "geocoder-disabled", "Nominatim disabled — new resolution remains gated", "Nominatim dinyahaktifkan — penyelesaian baharu kekal berpagar", 845, 930, 430)
    add_fragment(root, "jobroute", "routable", "alt", 30, 990, 1700, 300)
    add_operand(root, "jobroute", "routable-yes", "Routable with sufficient confidence", "Boleh dihala dengan keyakinan mencukupi", 45, 1010, 330)
    add_fragment_divider(root, "jobroute", "routable", 1180, 30, 1730)
    add_operand(root, "jobroute", "routable-no", "Remote, unresolved or low confidence", "Jarak jauh, tidak selesai atau keyakinan rendah", 45, 1190, 360)
    rows = [
        ("user", "job", "Select Route to workplace", "Pilih Halakan ke tempat kerja", "data-jf-action='route-job'", "data-jf-action='route-job'"),
        ("job", "client", "Resolve selected job", "Selesaikan kerja dipilih", "resolveGeoJobLocation(job.id)", "resolveGeoJobLocation(job.id)"),
        ("client", "api", "POST authenticated request", "POST permintaan disahkan", "POST /api/geo/jobs/:id/resolve", "POST /api/geo/jobs/:id/resolve"),
        ("api", "resolver", "Require session; keep source immutable", "Wajibkan sesi; kekalkan sumber", "requireAuth; resolveJobLocation()", "requireAuth; resolveJobLocation()"),
        ("resolver", "resolution", "Read unexpired resolution", "Baca penyelesaian belum luput", "getJobLocationResolution()", "getJobLocationResolution()"),
        ("resolution", "resolver", "Reuse confidence result", "Guna semula hasil keyakinan", "expires_at > now()", "expires_at > now()"),
        ("resolver", "jobs", "Read location and remote type", "Baca lokasi dan jenis jarak jauh", "select location, remote_type", "select location, remote_type"),
        ("resolver", "nominatim", "Search only when enabled", "Cari hanya apabila diaktifkan", "GeoGateway.search()", "GeoGateway.search()"),
        ("nominatim", "resolver", "Return place and confidence", "Pulangkan tempat dan keyakinan", "exact | street | locality", "exact | street | locality"),
        ("resolver", "resolution", "Store derived coordinate", "Simpan koordinat terbitan", "upsert job_location_resolutions", "upsert job_location_resolutions"),
        ("resolution", "job", "Return routable state", "Pulangkan keadaan boleh dihala", "JobGeoResolution", "JobGeoResolution"),
        ("job", "nav", "Set routable destination", "Tetapkan destinasi boleh dihala", "petakerja:geo-job-destination", "petakerja:geo-job-destination"),
        ("nav", "user", "Open Navigator and route", "Buka Navigator dan hala", "setEndpoint(); recalculate()", "setEndpoint(); recalculate()"),
        ("job", "user", "Explain remote or low confidence", "Jelaskan jarak jauh atau keyakinan rendah", "routable === false", "routable === false"),
    ]
    add_messages(root, "jobroute", p, rows, row_positions=[
        250, 300, 350, 400, 500, 550, 650, 800, 850, 900, 1050, 1100, 1150, 1250,
    ])
    add_text(root, "jobroute-note", "jobroute/note", "With Nominatim off, new workplace resolutions remain gated while Valhalla routing stays live.", "Apabila Nominatim dimatikan, penyelesaian tempat kerja baharu kekal berpagar sementara Valhalla aktif.", 930, 1330, 730, 55, NOTE)
    base_note(root, page)
    write(page, mxfile)


def generate_domain() -> None:
    page = Page("domain.drawio", "v2_geo_domain", "V2 Georouting Domain", 1600, 1100,
                "PetaKerja Domain Classes — V2 Georouting", "Kelas Domain PetaKerja — Georouting V2",
                "Compact class cards follow the class proportions in the supplied template.",
                "Kad kelas padat mengikut perkadaran kelas dalam templat yang dibekalkan.")
    mxfile, root = create_page(page)
    groups = [("core", "Existing core domain", "Domain teras sedia ada", 50, 130, 400, 840),
              ("geo", "Geospatial contracts", "Kontrak geospatial", 480, 130, 700, 840),
              ("derived", "Derived routing data", "Data penghalaan terbitan", 1210, 130, 340, 840)]
    for key, en, ms, x, y, w, h in groups:
        add_vertex(root, f"domain-group-{key}", f"domain/group-{key}", en, ms, x, y, w, h, GROUP)
    ids: dict[str, str] = {}
    core = [
        ("user", "UserProfile", "ProfilPengguna", "id, role, selected_state", "id, peranan, selected_state", 100, 215, "user-profile"),
        ("poi", "POI", "POI", "id, category, geom, address", "id, kategori, geom, alamat", 100, 400, "poi-entity"),
        ("job", "JobListing", "SenaraiKerja", "id, title, company, location", "id, tajuk, syarikat, lokasi", 100, 585, "job-entity"),
        ("state", "UserJobState", "StatusKerjaPengguna", "user_id, job_key, state", "user_id, job_key, status", 100, 770, "job-state-entity"),
    ]
    for key, en, ms, ben, bms, x, y, node in core:
        ids[key] = add_class(root, f"domain-{key}", f"domain/{key}", en, ms, ben, bms, x, y, 300, 120, node)
    geo = [
        ("location", "GeoLocation", "LokasiGeo", "lat, lng, label?", "lat, lng, label?", 520, 215, "geo-location"),
        ("place", "GeoPlace", "TempatGeo", "source, confidence, boundary?", "sumber, keyakinan, sempadan?", 850, 215, "geo-place"),
        ("route", "GeoRoute", "LaluanGeo", "profile, geometry, distance, duration?", "profil, geometri, jarak, tempoh?", 520, 400, "geo-route"),
        ("alternative", "GeoRouteAlternative", "AlternatifLaluanGeo", "geometry, duration, maneuvers", "geometri, tempoh, arahan", 850, 400, "geo-route-alternative"),
        ("maneuver", "GeoManeuver", "ArahanGeo", "instruction, shape indexes", "arahan, indeks bentuk", 520, 585, "geo-maneuver"),
        ("matrix", "GeoMatrixResult", "HasilMatriksGeo", "sources, targets, distances, durations", "sumber, sasaran, jarak, tempoh", 850, 585, "geo-matrix"),
        ("isochrone", "GeoIsochroneResult", "HasilIsokronGeo", "origin, contours, FeatureCollection", "asal, kontur, FeatureCollection", 685, 770, "geo-isochrone"),
    ]
    for key, en, ms, ben, bms, x, y, node in geo:
        ids[key] = add_class(root, f"domain-{key}", f"domain/{key}", en, ms, ben, bms, x, y, 290, 120, node)
    derived = [
        ("resolution", "JobLocationResolution", "PenyelesaianLokasiKerja", "scraped_job_id\ncoordinates, confidence\nroutable, is_remote", "scraped_job_id\nkoordinat, keyakinan\nboleh_dihala, jarak_jauh", 1260, 235, 240, 170, "job-location-resolution", "job_location_resolutions"),
        ("route-cache", "GeoRouteCache", "CacheLaluanGeo", "operation, provider\npayload, expires_at", "operasi, penyedia\npayload, expires_at", 1260, 505, 240, 140, "geo-route-cache", "geo_route_cache"),
        ("geocode-cache", "GeoGeocodeCache", "CacheGeokodGeo", "operation, provider\npayload, expires_at", "operasi, penyedia\npayload, expires_at", 1260, 745, 240, 140, "geo-geocode-cache", "geo_geocode_cache"),
    ]
    for key, en, ms, ben, bms, x, y, w, h, node, table in derived:
        ids[key] = add_class(root, f"domain-{key}", f"domain/{key}", en, ms, ben, bms, x, y, w, h, node, table)
    links = [("place", "location", "has", "mempunyai"), ("route", "location", "origin + destination", "asal + destinasi"),
             ("route", "alternative", "0..*", "0..*"), ("alternative", "maneuver", "0..*", "0..*"),
             ("resolution", "place", "resolved as", "diselesaikan sebagai")]
    for index, (source, target, en, ms) in enumerate(links, 1):
        add_edge(root, f"domain-edge-{index}", f"domain/edge-{index}", ids[source], ids[target], en, ms)
    add_edge_points(root, "domain-edge-job-resolution", "domain/edge-job-resolution", ids["resolution"], ids["job"],
                    [(1190, 925), (455, 925), (455, 645)], "derived from", "diterbitkan daripada")
    base_note(root, page)
    write(page, mxfile)


def generate_implementation() -> None:
    page = Page("implementation.drawio", "v2_geo_implementation", "V2 Georouting Implementation", 1680, 1180,
                "Implementation Dependencies — V2 Georouting", "Kebergantungan Pelaksanaan — Georouting V2",
                "Aligned responsibility lanes replace the previous free-form dependency field.",
                "Lorong tanggungjawab sejajar menggantikan medan kebergantungan bebas sebelumnya.")
    mxfile, root = create_page(page)
    lanes = [("app", "Application composition", "Komposisi aplikasi", 50, 130, 1580, 175),
             ("browser", "Browser managers and rendering", "Pengurus pelayar dan pemaparan", 50, 335, 1580, 300),
             ("service", "Client and server boundary", "Sempadan klien dan pelayan", 50, 665, 1580, 190),
             ("provider", "Providers and persistent data", "Penyedia dan data kekal", 50, 885, 1580, 190)]
    for key, en, ms, x, y, w, h in lanes:
        add_vertex(root, f"impl-group-{key}", f"implementation/group-{key}", en, ms, x, y, w, h, GROUP)
    specs = [
        ("state", "AppState", "AppState", "map, userLocation, jobFinder", "map, userLocation, jobFinder", 290, 195, 260, 80, "app-state"),
        ("app", "MyPetaApp", "MyPetaApp", "creates and binds managers", "mencipta dan mengikat pengurus", 710, 185, 260, 100, "mypeta-app"),
        ("map", "MapManager", "MapManager", "style lifecycle and camera", "kitar gaya dan kamera", 105, 420, 220, 90, "map-manager"),
        ("tools", "MapToolsPanelManager", "MapToolsPanelManager", "rail, drawer and fit padding", "rel, laci dan ruang fit", 360, 420, 220, 90, "map-tools-manager"),
        ("nav", "GeoNavigationManager", "GeoNavigationManager", "A/B, route, matrix, isochrone", "A/B, laluan, matriks, isokron", 615, 405, 260, 120, "geo-navigation-manager"),
        ("renderer", "GeoRouteRenderer", "GeoRouteRenderer", "ordered MapLibre layers", "lapisan MapLibre tersusun", 910, 420, 220, 90, "geo-route-renderer"),
        ("appearance", "RouteAppearanceManager", "RouteAppearanceManager", "versioned visual settings", "tetapan visual berversi", 1165, 420, 220, 90, "route-appearance-manager"),
        ("job", "JobFinderManager", "JobFinderManager", "workplace destination event", "peristiwa destinasi kerja", 615, 545, 260, 65, "job-manager"),
        ("client", "src/services/geo.ts", "src/services/geo.ts", "typed same-origin fetches", "fetch asal sama berjenis", 500, 725, 280, 90, "geo-service"),
        ("api", "server/routes/geo.ts", "server/routes/geo.ts", "validation, auth and rate limits", "pengesahan, auth dan had kadar", 820, 725, 280, 90, "geo-api"),
        ("gateway", "server/geo/gateway.ts", "server/geo/gateway.ts", "normalization, cache and fallback", "normalisasi, cache dan sandaran", 1140, 715, 300, 110, "geo-gateway"),
        ("supabase", "Supabase / PostGIS", "Supabase / PostGIS", "cache and job resolution", "cache dan penyelesaian kerja", 500, 950, 300, 80, "supabase-db"),
        ("valhalla", "Valhalla", "Valhalla", "route, matrix and isochrone", "laluan, matriks dan isokron", 820, 950, 300, 80, "valhalla"),
        ("nominatim", "Nominatim (disabled)", "Nominatim (dinyahaktifkan)", "search, reverse and lookup", "carian, songsang dan lookup", 1140, 950, 300, 80, "nominatim"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, ben, bms, x, y, w, h, node in specs:
        ids[key] = add_class(root, f"impl-{key}", f"implementation/{key}", en, ms, ben, bms, x, y, w, h, node)
    links = [("app", "state"), ("app", "nav"), ("nav", "tools"), ("nav", "map"), ("nav", "renderer"),
             ("nav", "appearance"), ("job", "nav"), ("nav", "client"), ("client", "api"), ("api", "gateway"),
             ("gateway", "supabase"), ("gateway", "valhalla"), ("gateway", "nominatim")]
    for index, (source, target) in enumerate(links, 1):
        add_edge(root, f"impl-edge-{index}", f"implementation/edge-{index}", ids[source], ids[target])
    base_note(root, page)
    write(page, mxfile)


def trapezoid_style(fill: str, stroke: str) -> str:
    return f"shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;direction=south;fillColor=light-dark({fill},#20252d);strokeColor=light-dark({stroke},{stroke});strokeWidth=2;fontFamily=Arial;fontSize=15;fontStyle=1;verticalAlign=top;align=left;spacingTop=10;spacingLeft=28;fontColor=light-dark(#172033,#e8edf7);"


def generate_architecture() -> None:
    page = Page("architecture.drawio", "v2_geo_architecture", "V2 Georouting Layered Architecture", 1600, 1200,
                "Layered Architecture — V2 Georouting", "Seni Bina Berlapis — Georouting V2",
                "A centered stacked-responsibility view with three evenly spaced components per layer.",
                "Paparan tanggungjawab bertindan berpusat dengan tiga komponen berjarak sekata setiap lapisan.")
    mxfile, root = create_page(page)
    layers = [
        ("inputs", "1 · Inputs and user intent", "1 · Input dan niat pengguna", 250, 130, 1100, 160, "#e8eef5", "#66758a"),
        ("render", "2 · MapLibre rendering", "2 · Pemaparan MapLibre", 200, 330, 1200, 160, "#dcebfa", "#2d72d2"),
        ("browser", "3 · Browser orchestration", "3 · Orkestrasi pelayar", 150, 530, 1300, 175, "#eee5fa", "#7e57c2"),
        ("gateway", "4 · Same-origin GeoGateway", "4 · GeoGateway asal sama", 100, 745, 1400, 175, "#fff1d6", "#c87600"),
        ("providers", "5 · Providers and reusable data", "5 · Penyedia dan data boleh guna semula", 50, 960, 1500, 150, "#e9f6ed", "#3d965b"),
    ]
    for key, en, ms, x, y, w, h, fill, stroke in layers:
        add_vertex(root, f"arch-layer-{key}", f"architecture/layer-{key}", en, ms, x, y, w, h, trapezoid_style(fill, stroke))
    specs = [
        ("search", "Place or address", "Tempat atau alamat", 390, 205, BOX_GRAY, "search-manager"),
        ("ab", "A/B, map click or GPS", "A/B, klik peta atau GPS", 680, 205, BOX_GRAY, "geo-navigation-manager"),
        ("job", "Workplace destination", "Destinasi tempat kerja", 970, 205, BOX_GRAY, "job-manager"),
        ("maplibre", "MapLibre route and polygon layers", "Lapisan laluan dan poligon MapLibre", 680, 405, BOX_BLUE, "maplibre-gl"),
        ("renderer", "GeoRouteRenderer interactions", "Interaksi GeoRouteRenderer", 970, 405, BOX_BLUE, "geo-route-renderer"),
        ("tools", "Map Tools UI", "UI Alat Peta", 390, 610, BOX_PURPLE, "map-tools-manager"),
        ("nav", "GeoNavigationManager", "GeoNavigationManager", 680, 610, BOX_PURPLE, "geo-navigation-manager"),
        ("client", "Geo client contracts", "Kontrak klien Geo", 970, 610, BOX_PURPLE, "geo-service"),
        ("api", "Express /api/geo/*", "Express /api/geo/*", 970, 825, BOX_ORANGE, "geo-api"),
        ("gateway", "GeoGateway normalization", "Normalisasi GeoGateway", 680, 825, BOX_ORANGE, "geo-gateway"),
        ("fallback", "Haversine fallback", "Sandaran Haversine", 390, 825, BOX_ORANGE, "geo-gateway"),
        ("cache", "Supabase cache", "Cache Supabase", 390, 1020, BOX_GREEN, "supabase-db,geo-route-cache"),
        ("valhalla", "Valhalla · enabled", "Valhalla · diaktifkan", 680, 1020, BOX_GREEN, "valhalla"),
        ("nominatim", "Nominatim · disabled", "Nominatim · dinyahaktifkan", 970, 1020, BOX_GRAY, "nominatim"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, x, y, style, nodes in specs:
        ids[key] = add_vertex(root, f"arch-{key}", f"architecture/{key}", en, ms, x, y, CARD_W, 58, style, nodes)
    links = [("ab", "maplibre"), ("maplibre", "nav"), ("tools", "nav"), ("nav", "renderer"), ("nav", "client"),
             ("client", "api"), ("api", "gateway"), ("gateway", "cache"), ("gateway", "valhalla"),
             ("gateway", "nominatim"), ("gateway", "fallback")]
    for index, (source, target) in enumerate(links, 1):
        add_edge(root, f"arch-edge-{index}", f"architecture/edge-{index}", ids[source], ids[target])
    base_note(root, page)
    write(page, mxfile)


def generate_modules() -> None:
    page = Page("modules.drawio", "v2_geo_modules", "V2 Georouting Module Hierarchy", 1580, 1080,
                "Module Hierarchy — V2 Georouting", "Hierarki Modul — Georouting V2",
                "Three aligned ownership columns replace the previous all-to-all hierarchy.",
                "Tiga lajur pemilikan sejajar menggantikan hierarki semua-ke-semua sebelumnya.")
    mxfile, root = create_page(page)
    app = add_vertex(root, "module-app", "modules/app", "MyPetaApp · application composition root", "MyPetaApp · punca komposisi aplikasi", 560, 125, 460, 70, BOX_BLUE, "mypeta-app")
    groups = [("ui", "Discovery and intent", "Penemuan dan niat", 70, 260, 430, 690),
              ("orchestration", "Georouting orchestration", "Orkestrasi georouting", 575, 260, 430, 690),
              ("infra", "Gateway and infrastructure", "Gerbang dan infrastruktur", 1080, 260, 430, 690)]
    for key, en, ms, x, y, w, h in groups:
        add_vertex(root, f"module-group-{key}", f"modules/group-{key}", en, ms, x, y, w, h, GROUP)
    specs = [
        ("map", "MapManager", "MapManager", 125, 350, BOX_BLUE, "map-manager"),
        ("tools", "MapToolsPanelManager", "MapToolsPanelManager", 125, 500, BOX_BLUE, "map-tools-manager"),
        ("search", "SearchManager", "SearchManager", 125, 650, BOX_BLUE, "search-manager"),
        ("job", "JobFinderManager", "JobFinderManager", 125, 800, BOX_BLUE, "job-manager"),
        ("nav", "GeoNavigationManager", "GeoNavigationManager", 630, 350, BOX_PURPLE, "geo-navigation-manager"),
        ("renderer", "GeoRouteRenderer", "GeoRouteRenderer", 630, 500, BOX_PURPLE, "geo-route-renderer"),
        ("appearance", "RouteAppearanceManager", "RouteAppearanceManager", 630, 650, BOX_PURPLE, "route-appearance-manager"),
        ("client", "Geo service contracts", "Kontrak servis Geo", 630, 800, BOX_PURPLE, "geo-service"),
        ("api", "Express Geo API", "API Geo Express", 1135, 350, BOX_ORANGE, "geo-api"),
        ("gateway", "GeoGateway", "GeoGateway", 1135, 500, BOX_ORANGE, "geo-gateway"),
        ("providers", "Valhalla / Nominatim", "Valhalla / Nominatim", 1135, 650, BOX_ORANGE, "valhalla,nominatim"),
        ("data", "Supabase routing data", "Data penghalaan Supabase", 1135, 800, BOX_ORANGE, "supabase-db,geo-route-cache,job-location-resolution"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, x, y, style, node in specs:
        ids[key] = add_vertex(root, f"module-{key}", f"modules/{key}", en, ms, x, y, 320, 70, style, node)
    for index, target in enumerate(("map", "nav", "api"), 1):
        add_edge(root, f"module-root-{index}", f"modules/root-{index}", app, ids[target], "owns / uses", "memiliki / menggunakan")
    links = [("map", "tools"), ("tools", "search"), ("search", "job"), ("nav", "renderer"), ("renderer", "appearance"),
             ("appearance", "client"), ("api", "gateway"), ("gateway", "providers"), ("providers", "data")]
    for index, (source, target) in enumerate(links, 1):
        add_edge(root, f"module-edge-{index}", f"modules/edge-{index}", ids[source], ids[target])
    base_note(root, page)
    write(page, mxfile)


def generate_data_flow() -> None:
    page = Page("data-flow.drawio", "v2_geo_data_flow", "V2 Georouting Data Flow", 1720, 1050,
                "Data Flow — V2 Georouting", "Aliran Data — Georouting V2",
                "Five equal columns separate the outbound request from the normalized response path.",
                "Lima lajur sama memisahkan permintaan keluar daripada laluan respons ternormal.")
    mxfile, root = create_page(page)
    columns = [("input", "Inputs", "Input", 50), ("browser", "Browser", "Pelayar", 385), ("api", "Same-origin API", "API asal sama", 720),
               ("gateway", "Gateway", "Gerbang", 1055), ("provider", "Providers and data", "Penyedia dan data", 1390)]
    for key, en, ms, x in columns:
        add_vertex(root, f"data-column-{key}", f"data/column-{key}", en, ms, x, 130, 280, 790, GROUP)
    specs = [
        ("intent", "A/B + profile", "A/B + profil", 80, 245, BOX_GRAY, "pengguna"),
        ("gps", "GPS or map coordinate", "GPS atau koordinat peta", 80, 465, BOX_GRAY, "geo-location"),
        ("search", "Bounds, place or job ID", "Sempadan, tempat atau ID kerja", 80, 685, BOX_GRAY, "search-manager,job-manager"),
        ("nav", "1 · GeoNavigationManager", "1 · GeoNavigationManager", 415, 245, BOX_PURPLE, "geo-navigation-manager"),
        ("client", "2 · src/services/geo.ts", "2 · src/services/geo.ts", 415, 465, BOX_PURPLE, "geo-service"),
        ("render", "9 · GeoRouteRenderer + MapLibre", "9 · GeoRouteRenderer + MapLibre", 415, 685, BOX_BLUE, "geo-route-renderer,maplibre-gl"),
        ("routes", "3 · Validate, authenticate and rate-limit", "3 · Sahkan, auth dan had kadar", 750, 465, BOX_ORANGE, "geo-api"),
        ("response", "8 · Return bounded GeoJSON", "8 · Pulangkan GeoJSON terbatas", 750, 685, BOX_CYAN, "geo-api"),
        ("normalize", "4 · Stable-key cache and provider dispatch", "4 · Cache kunci stabil dan agihan penyedia", 1085, 465, BOX_ORANGE, "geo-gateway,geo-route-cache,geo-geocode-cache"),
        ("fallback", "7 · Normalize or label fallback", "7 · Normalisasi atau label sandaran", 1085, 685, BOX_ORANGE, "geo-gateway"),
        ("valhalla", "5a · Valhalla calculations", "5a · Pengiraan Valhalla", 1420, 245, BOX_GREEN, "valhalla"),
        ("nominatim", "5b · Nominatim (gated)", "5b · Nominatim (berpagar)", 1420, 465, BOX_GRAY, "nominatim"),
        ("supabase", "5c · Supabase / PostGIS", "5c · Supabase / PostGIS", 1420, 685, BOX_GREEN, "supabase-db"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, x, y, style, node in specs:
        ids[key] = add_vertex(root, f"data-{key}", f"data/{key}", en, ms, x, y, 220, 75, style, node)
    links = [("intent", "nav"), ("gps", "client"), ("search", "render"), ("nav", "client"), ("client", "routes"),
             ("routes", "normalize"), ("normalize", "valhalla"), ("normalize", "nominatim"), ("normalize", "supabase"),
             ("valhalla", "fallback"), ("nominatim", "fallback"), ("supabase", "fallback"),
             ("fallback", "response"), ("response", "render")]
    for index, (source, target) in enumerate(links, 1):
        add_edge(root, f"data-edge-{index}", f"data/edge-{index}", ids[source], ids[target])
    base_note(root, page)
    write(page, mxfile)


def generate_erd() -> None:
    page = Page("erd.drawio", "v2_geo_erd", "V2 Georouting ERD", 1500, 980,
                "Routing Data Model — V2 Georouting", "Model Data Penghalaan — Georouting V2",
                "Four compact entity tables; only the real scraped-job relationship is connected.",
                "Empat jadual entiti padat; hanya hubungan kerja tersauk sebenar disambungkan.")
    mxfile, root = create_page(page)
    specs = [
        ("jobs", "public.scraped_jobs", "public.scraped_jobs", "PK id : text\nlocation : text?\nremote_type : text?", "PK id : text\nlokasi : text?\nremote_type : text?", 120, 210, 330, 210, "job-entity", "scraped_jobs"),
        ("resolution", "public.job_location_resolutions", "public.job_location_resolutions", "PK id : uuid\nFK scraped_job_id : text\nlatitude / longitude / geom\nconfidence / routable / is_remote\nresolved_at / expires_at", "PK id : uuid\nFK scraped_job_id : text\nlatitude / longitude / geom\nkeyakinan / boleh_dihala / jarak_jauh\nresolved_at / expires_at", 560, 175, 380, 280, "job-location-resolution", "job_location_resolutions"),
        ("route-cache", "public.geo_route_cache", "public.geo_route_cache", "PK cache_key : text\noperation : route | matrix | isochrone\nprovider / payload / expires_at\nhit_count / last_accessed_at", "PK cache_key : text\noperasi : route | matrix | isochrone\npenyedia / payload / expires_at\nhit_count / last_accessed_at", 1050, 175, 330, 250, "geo-route-cache", "geo_route_cache"),
        ("geocode-cache", "public.geo_geocode_cache", "public.geo_geocode_cache", "PK cache_key : text\noperation : search | reverse | lookup\nprovider / payload / expires_at\nhit_count / last_accessed_at", "PK cache_key : text\noperasi : search | reverse | lookup\npenyedia / payload / expires_at\nhit_count / last_accessed_at", 1050, 540, 330, 250, "geo-geocode-cache", "geo_geocode_cache"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, ben, bms, x, y, w, h, node, table in specs:
        ids[key] = add_class(root, f"erd-{key}", f"erd/{key}", en, ms, ben, bms, x, y, w, h, node, table)
    add_edge(root, "erd-jobs-resolution", "erd/jobs-resolution", ids["jobs"], ids["resolution"], "1 job : 0..* derived resolutions", "1 kerja : 0..* penyelesaian terbitan")
    add_text(root, "erd-security", "erd/security", "Geo tables use RLS, revoke browser roles and grant server service_role access only.", "Jadual geo menggunakan RLS, menarik akses peranan pelayar dan memberi akses service_role pelayan sahaja.", 120, 555, 820, 80, NOTE)
    add_text(root, "erd-no-history", "erd/no-history", "Route cache does not persist raw user-location history.", "Cache laluan tidak menyimpan sejarah lokasi mentah pengguna.", 120, 690, 820, 65, BOX_GREEN)
    base_note(root, page)
    write(page, mxfile)


def generate_routing_stack() -> None:
    page = Page("routing-stack.drawio", "v2_geo_routing_stack", "V2 Routing Responsibility Stack", 1600, 1120,
                "A-to-B Routing Responsibilities — V2", "Tanggungjawab Penghalaan A-ke-B — V2",
                "The established stacked-Doritos view, re-centered on a regular spacing grid.",
                "Paparan Doritos bertindan yang ditetapkan, dipusatkan semula pada grid jarak seragam.")
    mxfile, root = create_page(page)
    layers = [
        ("inputs", "1 · Inputs", "1 · Input", 250, 125, 1100, 150, "#e8eef5", "#66758a"),
        ("render", "2 · MapLibre rendering", "2 · Pemaparan MapLibre", 200, 315, 1200, 150, "#dcebfa", "#2d72d2"),
        ("browser", "3 · Browser orchestration", "3 · Orkestrasi pelayar", 150, 505, 1300, 160, "#eee5fa", "#7e57c2"),
        ("gateway", "4 · GeoGateway boundary", "4 · Sempadan GeoGateway", 100, 705, 1400, 160, "#fff1d6", "#c87600"),
        ("providers", "5 · Providers and cache", "5 · Penyedia dan cache", 50, 905, 1500, 145, "#e9f6ed", "#3d965b"),
    ]
    for key, en, ms, x, y, w, h, fill, stroke in layers:
        add_vertex(root, f"stack-layer-{key}", f"routing-stack/layer-{key}", en, ms, x, y, w, h, trapezoid_style(fill, stroke))
    specs = [
        ("input", "A/B + GPS + profile", "A/B + GPS + profil", 650, 195, 300, BOX_GRAY, "geo-location"),
        ("map", "MapLibre · renderer and interaction only", "MapLibre · pemapar dan interaksi sahaja", 560, 385, 480, BOX_BLUE, "maplibre-gl"),
        ("nav", "GeoNavigationManager + GeoRouteRenderer", "GeoNavigationManager + GeoRouteRenderer", 390, 575, 390, BOX_PURPLE, "geo-navigation-manager,geo-route-renderer"),
        ("client", "src/services/geo.ts", "src/services/geo.ts", 900, 575, 300, BOX_PURPLE, "geo-service"),
        ("api", "Express /api/geo + safety checks", "Express /api/geo + semakan keselamatan", 900, 775, 390, BOX_ORANGE, "geo-api"),
        ("gateway", "GeoGateway normalization + fallback", "Normalisasi + sandaran GeoGateway", 330, 775, 420, BOX_ORANGE, "geo-gateway"),
        ("cache", "Supabase cache · available", "Cache Supabase · tersedia", 250, 970, 310, BOX_GREEN, "supabase-db,geo-route-cache"),
        ("valhalla", "Valhalla · enabled", "Valhalla · diaktifkan", 645, 970, 310, BOX_GREEN, "valhalla"),
        ("nominatim", "Nominatim · disabled", "Nominatim · dinyahaktifkan", 1040, 970, 310, BOX_GRAY, "nominatim"),
    ]
    ids: dict[str, str] = {}
    for key, en, ms, x, y, w, style, nodes in specs:
        ids[key] = add_vertex(root, f"stack-{key}", f"routing-stack/{key}", en, ms, x, y, w, 55, style, nodes)
    for index, (source, target) in enumerate([("input", "nav"), ("nav", "map"), ("nav", "client"), ("client", "api"),
                                                   ("api", "gateway"), ("gateway", "cache"), ("gateway", "valhalla"), ("gateway", "nominatim")], 1):
        add_edge(root, f"stack-edge-{index}", f"routing-stack/edge-{index}", ids[source], ids[target])
    add_text(root, "stack-fallback", "routing-stack/fallback", "Provider failure → Haversine straight line → no ETA, maneuvers or navigable claim", "Kegagalan penyedia → garis lurus Haversine → tiada ETA, arahan atau dakwaan navigasi", 360, 1055, 880, 35, NOTE)
    write(page, mxfile)


SUPABASE_GROUPS = {
    "Auth and profile": ["account", "session", "user", "verification", "users", "user_api_tokens"],
    "AI and administration": ["ai_admin_audit_logs", "ai_provider_credentials", "ai_usage_events", "ai_user_model_preferences"],
    "POI, map and community": ["spatial_ref_sys", "data_sources", "states", "pois", "poi_categories", "poi_category_groups", "poi_bookmarks", "poi_reviews", "map_styles", "geocode_cache", "coffee_shops", "events", "transit_routes", "company_address_cache", "user_marker_purchases"],
    "Jobs and automation": ["scraped_jobs", "job_location_resolutions", "user_job_states", "pipeline_runs", "pipeline_run_items", "user_pipeline_settings", "extractor_runs", "extractor_jobs", "user_company_watchlist", "watchlist_discovered_jobs", "watchlist_polls", "user_gmail_integrations", "user_gmail_messages", "user_gmail_sync_runs", "notifications", "user_notification_prefs", "user_privacy_prefs"],
    "Blog and newsletter": ["blog_analytics_events", "blog_author_profiles", "blog_broadcast_recipients", "blog_broadcast_redirects", "blog_broadcasts", "blog_categories", "blog_comments", "blog_cron_runs", "blog_email_events", "blog_email_suppressions", "blog_media", "blog_newsletters", "blog_post_bookmarks", "blog_post_reactions", "blog_post_revisions", "blog_post_tags", "blog_post_views", "blog_post_views_daily", "blog_post_views_daily_dim", "blog_posts", "blog_reading_history", "blog_recommendations", "blog_subscriber_events", "blog_subscriber_newsletters", "blog_subscribers", "blog_tags", "blog_views_rollup_state"],
    "Community submissions": ["poll_options", "polls", "rc_masjids", "rc_submissions", "votes"],
    "Architecture Explorer": ["architecture_slide_decks", "architecture_slide_deck_branches", "architecture_slide_deck_versions", "architecture_diagrams", "architecture_diagram_members", "architecture_diagram_branches", "architecture_diagram_versions", "architecture_diagram_crdt_updates", "architecture_diagram_sync_snapshots"],
    "Geo platform": ["geo_geocode_cache", "geo_route_cache", "geo_workspaces", "geo_workspace_assets"],
}


def generate_supabase() -> None:
    page = Page("supabase.drawio", "v2_geo_supabase", "V2 Supabase Schema Snapshot", 1900, 1450,
                "Supabase Public Schema Snapshot — V2 Georouting", "Snapshot Skema Awam Supabase — Georouting V2",
                f"Verified {STAMP}: 87 public tables and 119 foreign keys; five geo-related tables are identified.",
                f"Disahkan {STAMP}: 87 jadual awam dan 119 kunci asing; lima jadual berkaitan geo dikenal pasti.")
    mxfile, root = create_page(page)
    positions = {
        "Auth and profile": (50, 135, 420, 250), "AI and administration": (500, 135, 420, 250),
        "POI, map and community": (950, 135, 420, 470), "Jobs and automation": (1400, 135, 450, 530),
        "Blog and newsletter": (50, 420, 870, 790), "Community submissions": (950, 650, 420, 240),
        "Architecture Explorer": (1400, 710, 450, 390), "Geo platform": (950, 940, 420, 270),
    }
    ms_groups = {
        "Auth and profile": "Pengesahan dan profil", "AI and administration": "AI dan pentadbiran",
        "POI, map and community": "POI, peta dan komuniti", "Jobs and automation": "Kerja dan automasi",
        "Blog and newsletter": "Blog dan surat berita", "Community submissions": "Penyerahan komuniti",
        "Architecture Explorer": "Architecture Explorer", "Geo platform": "Platform geo",
    }
    for index, (group, tables) in enumerate(SUPABASE_GROUPS.items(), 1):
        x, y, w, h = positions[group]
        lines = "\n".join(f"public.{name}" for name in tables)
        style = (TABLE_BOX if group == "Geo platform" else GROUP) + "fontSize=10;spacingTop=7;"
        add_vertex(root, f"schema-group-{index}", f"supabase/group-{index}", f"{group}\n{lines}", f"{ms_groups[group]}\n{lines}", x, y, w, h, style, "supabase-db")
    add_text(root, "schema-geo-note", "supabase/geo-note",
             "Geo tables: geo_geocode_cache, geo_route_cache, job_location_resolutions, geo_workspaces and geo_workspace_assets. The routing ERD excludes the two Geo Studio workspace tables.",
             "Jadual geo: geo_geocode_cache, geo_route_cache, job_location_resolutions, geo_workspaces dan geo_workspace_assets. ERD penghalaan mengecualikan dua jadual ruang kerja Studio Geo.",
             50, 1260, 1800, 75, NOTE)
    base_note(root, page)
    write(page, mxfile)


def main() -> None:
    generators = [
        generate_usecase, generate_flowchart, generate_route_sequence, generate_travel_sequence,
        generate_job_sequence, generate_domain, generate_implementation, generate_architecture,
        generate_modules, generate_data_flow, generate_erd, generate_routing_stack, generate_supabase,
    ]
    for generator in generators:
        generator()
    generated = sorted(OUTPUT.glob("*.drawio"))
    if len(generated) != 13:
        raise RuntimeError(f"Expected 13 V2 sources, generated {len(generated)}")
    print(f"Generated {len(generated)} template-aligned V2 Georouting Draw.io sources in {OUTPUT}")


if __name__ == "__main__":
    main()
