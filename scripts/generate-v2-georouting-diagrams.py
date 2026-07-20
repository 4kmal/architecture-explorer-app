#!/usr/bin/env python3
"""Generate the editable bilingual V2 Georouting Draw.io collection.

The layout system is intentionally derived from the project templates:

* Use-case actors are 70 x 140 and use cases are 62 px high.
* Sequence actors, participants, activations, messages and fragments are read
  from the supplied template; lanes use a fixed 200 px pitch and 50 px rows.
* Flowchart processes and decisions use a 10 px grid and orthogonal edges.
* UML class packages, compartments and relationships are read from the
  supplied class template; class cards use 46 px headers, 16 px titles,
  12 px stereotypes and 14 px typed members.
* Layered responsibility stacks, depth copies, cards, rails and callouts are
  read from the supplied stack template and projected into both themes.

Only files below ``assets/editor/v2-georouting`` are owned by this generator.
The historical vanilla diagrams are comparison assets and must remain untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
import html
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "editor" / "v2-georouting"
SEQUENCE_TEMPLATE = ROOT / "templates" / "Sequence Diagram Template.drawio"
CLASS_TEMPLATE = ROOT / "templates" / "Class Diagram Template.drawio"
STACK_TEMPLATE = ROOT / "templates" / "Stack Template.drawio"
STAMP = "2026-07-19"


def template_style(template: Path, predicate, description: str) -> str:
    """Return a required style from a canonical Draw.io template."""
    if not template.exists():
        raise RuntimeError(f"Missing template: {template}")
    for cell in ET.parse(template).getroot().findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError(f"{template.name} is missing its required {description} style")


def strip_style_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


SEQUENCE_ACTOR = template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlActor" in style, "actor")
SEQUENCE_PARTICIPANT = template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlLifeline" in style, "participant")
SEQUENCE_ACTIVATION = template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style,
    "activation",
)
SEQUENCE_FRAME = template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlFrame" in style, "combined fragment")
SEQUENCE_ACTOR_STEM = template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;") and cell.find("mxGeometry") is not None,
    "actor stem",
)
TEMPLATE_CALL = template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("edge") == "1" and "startArrow=classic" in style,
    "synchronous call",
)
TEMPLATE_RETURN = template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("edge") == "1" and "endArrow=open" in style and "dashed=1" in style,
    "return message",
)
TEMPLATE_DIVIDER = template_style(
    SEQUENCE_TEMPLATE,
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


def template_label(cell: ET.Element) -> str:
    return html.unescape(cell.get("labelEn") or cell.get("value", ""))


CLASS_PACKAGE_STYLES = {
    "identity": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "IDENTITY & PROFILE" in template_label(cell)
        and "dashed=1" in style,
        "identity package",
    ),
    "jobs": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "JOBS & USER STATUS" in template_label(cell)
        and "dashed=1" in style,
        "jobs package",
    ),
    "geo": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "MAPPING, POI & OPEN DATA" in template_label(cell)
        and "dashed=1" in style,
        "mapping package",
    ),
    "persistence": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "AI & ADMINISTRATION" in template_label(cell)
        and "dashed=1" in style,
        "administration package",
    ),
}
CLASS_CARD_STYLES = {
    "identity": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>UserProfile</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "identity class",
    ),
    "jobs": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>JobListing</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "jobs class",
    ),
    "geo": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>POI</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "mapping class",
    ),
    "persistence": template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>AIProviderCredential</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "administration class",
    ),
}
CLASS_MEMBER = template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("text;strokeColor=none;fillColor=none;align=left;"),
    "class member compartment",
)
CLASS_DIVIDER = template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;strokeWidth=1;fillColor=none;"),
    "class compartment divider",
)
CLASS_RELATION_LABEL = template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("edgeLabel;"),
    "relationship label",
)
CLASS_ASSOCIATION = strip_style_properties(
    template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("edge") == "1" and "endArrow=none" in style
        and "startArrow=none" in style and "dashed=1" not in style,
        "association",
    ),
    ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"),
)
CLASS_DEPENDENCY = strip_style_properties(
    template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("edge") == "1" and "endArrow=open" in style and "dashed=1" in style,
        "dependency",
    ),
    ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"),
)
CLASS_AGGREGATION = strip_style_properties(
    template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("edge") == "1" and "startArrow=diamond" in style and "startFill=0" in style,
        "aggregation",
    ),
    ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"),
)


def required_template_element(template: Path, identifier: str, description: str) -> ET.Element:
    if not template.exists():
        raise RuntimeError(f"Missing template: {template}")
    element = ET.parse(template).getroot().find(f".//*[@id='{identifier}']")
    if element is None:
        raise RuntimeError(f"{template.name} is missing its required {description} element ({identifier})")
    return element


def required_template_cell(template: Path, identifier: str, description: str) -> ET.Element:
    element = required_template_element(template, identifier, description)
    cell = element.find("mxCell") if element.tag == "object" else element
    if cell is None:
        raise RuntimeError(f"{template.name} {description} element ({identifier}) has no mxCell")
    return cell


def required_template_geometry(template: Path, identifier: str, description: str) -> tuple[float, float, float, float]:
    geometry = required_template_cell(template, identifier, description).find("mxGeometry")
    if geometry is None:
        raise RuntimeError(f"{template.name} {description} element ({identifier}) has no geometry")
    try:
        return tuple(float(geometry.get(name, "0")) for name in ("x", "y", "width", "height"))
    except ValueError as error:
        raise RuntimeError(f"{template.name} {description} element ({identifier}) has invalid geometry") from error


STACK_DARK_COLORS = {
    "#F7F9FC": "#10151B", "#172033": "#E8EDF7", "#475467": "#AEB8C8",
    "#E8EEF5": "#202B39", "#66758A": "#8493A8", "#B7C3D0": "#111923",
    "#DCEBFA": "#152A42", "#2D72D2": "#69A8EF", "#9CBFE4": "#0E1A29",
    "#EEE5FA": "#2A1F3B", "#7E57C2": "#AE8AE8", "#C4AEE3": "#171121",
    "#FFF1D6": "#382914", "#C87600": "#E0A24E", "#E6C27E": "#21170C",
    "#E1F4E8": "#173125", "#238551": "#61CC83", "#97C9AA": "#0E1D16",
    "#FFFFFF": "#171C23", "#A7B2C1": "#727F92", "#78A9DA": "#69A8EF",
    "#A184CF": "#AE8AE8", "#D89A39": "#E0A24E", "#58A777": "#61CC83",
    "#7A271A": "#FFD4CE", "#FDECEC": "#3A1C1C", "#CD4246": "#EF7377",
    "#B8C2CF": "#727F92", "#EEF4FB": "#17283F", "#5C87B2": "#78A9DA",
    "#7C8CA1": "#7F8DA1", "#7A4B00": "#FFE0A3", "#FFF4D6": "#3B2D14",
    "#344054": "#D7DEEA", "#EEF1F5": "#222832", "#98A2B3": "#727F92",
    "#667085": "#AEB8C8", "#1D4E89": "#BBD8FF", "#18663E": "#BBF2CC",
}


def theme_stack_style(style: str) -> str:
    """Make the supplied light-only Stack Template colors Explorer-theme aware."""
    property_pattern = re.compile(r"(fontColor|fillColor|strokeColor|labelBackgroundColor)=(#[0-9A-Fa-f]{6})")

    def replace_color(match: re.Match[str]) -> str:
        property_name, light = match.groups()
        canonical = light.upper()
        if property_name == "fillColor" and canonical == "#172033":
            dark = "#0B1016"
        elif property_name == "strokeColor" and canonical == "#172033":
            dark = "#596579"
        elif property_name == "fontColor" and canonical == "#FFFFFF":
            dark = "#F5F7FA"
        else:
            dark = STACK_DARK_COLORS.get(canonical)
        return f"{property_name}=light-dark({light},{dark})" if dark else match.group(0)

    return property_pattern.sub(replace_color, style)


def stack_template_style(identifier: str, description: str) -> str:
    style = required_template_cell(STACK_TEMPLATE, identifier, description).get("style", "")
    if not style:
        raise RuntimeError(f"{STACK_TEMPLATE.name} {description} element ({identifier}) has no style")
    return theme_stack_style(style)


STACK_TITLE_STYLE = stack_template_style("diagram-title", "title")
STACK_SUBTITLE_STYLE = stack_template_style("diagram-subtitle", "subtitle")
STACK_TITLE_GEOMETRY = required_template_geometry(STACK_TEMPLATE, "diagram-title", "title")
STACK_SUBTITLE_GEOMETRY = required_template_geometry(STACK_TEMPLATE, "diagram-subtitle", "subtitle")
STACK_LAYER_SLOTS = ("layer1-inputs", "layer2-maplibre", "layer3-browser", "layer4-gateway", "layer5-providers")
STACK_DEPTH_SLOTS = ("layer1-depth", "layer2-depth", "layer3-depth", "layer4-depth", "layer5-depth")
STACK_LAYER_STYLES = tuple(stack_template_style(slot, f"foreground layer {index}") for index, slot in enumerate(STACK_LAYER_SLOTS, 1))
STACK_DEPTH_STYLES = tuple(stack_template_style(slot, f"depth layer {index}") for index, slot in enumerate(STACK_DEPTH_SLOTS, 1))
STACK_LAYER_GEOMETRIES = tuple(required_template_geometry(STACK_TEMPLATE, slot, f"foreground layer {index}") for index, slot in enumerate(STACK_LAYER_SLOTS, 1))
STACK_DEPTH_GEOMETRIES = tuple(required_template_geometry(STACK_TEMPLATE, slot, f"depth layer {index}") for index, slot in enumerate(STACK_DEPTH_SLOTS, 1))
STACK_CARD_SLOTS = {
    "input-left": "input-search", "input-center": "input-ab", "input-right": "input-gps",
    "render-left": "maplibre-current", "render-right": "maplibre-capability",
    "browser-left": "browser-search-manager", "browser-center": "browser-navigation-manager", "browser-right": "browser-geo-service",
    "gateway-left": "gateway-express", "gateway-center": "gateway-core", "gateway-right": "gateway-guards",
    "provider-left": "provider-nominatim", "provider-center": "provider-valhalla", "provider-right": "provider-supabase",
}
STACK_CARD_GEOMETRIES = {
    key: required_template_geometry(STACK_TEMPLATE, slot, f"{key} card") for key, slot in STACK_CARD_SLOTS.items()
}
STACK_CARD_TEMPLATE_STYLES = {
    key: stack_template_style(slot, f"{key} card") for key, slot in STACK_CARD_SLOTS.items()
}
STACK_CARD_STYLES = {
    "neutral": stack_template_style("input-search", "neutral card"),
    "render": stack_template_style("maplibre-current", "rendering card"),
    "browser": stack_template_style("browser-search-manager", "browser card"),
    "gateway": stack_template_style("gateway-express", "gateway card"),
    "provider": stack_template_style("provider-valhalla", "provider card"),
}
STACK_CALLOUT_SLOTS = (
    "takeaway", "maplibre-boundary", "navigation-control-note", "directions-plugin-note",
    "side-flows", "fallback-note", "rollout-status",
)
STACK_CALLOUT_GEOMETRIES = {
    slot: required_template_geometry(STACK_TEMPLATE, slot, f"{slot} callout") for slot in STACK_CALLOUT_SLOTS
}
STACK_CALLOUT_STYLES = {slot: stack_template_style(slot, f"{slot} callout") for slot in STACK_CALLOUT_SLOTS}
STACK_FOOTER_GEOMETRY = required_template_geometry(STACK_TEMPLATE, "source-footer", "source footer")
STACK_FOOTER_STYLE = stack_template_style("source-footer", "source footer")
STACK_ANCHOR_STYLE = stack_template_style("request-start", "invisible rail anchor")
STACK_REQUEST_STYLE = stack_template_style("request-flow", "request rail")
STACK_RESPONSE_STYLE = stack_template_style("response-flow", "response rail")
STACK_REQUEST_LABEL_STYLE = stack_template_style("request-flow-label", "request label")
STACK_RESPONSE_LABEL_STYLE = stack_template_style("response-flow-label", "response label")
STACK_FALLBACK_STYLE = stack_template_style("gateway-fallback-branch", "fallback branch")
STACK_REQUEST_ANCHORS = (
    required_template_geometry(STACK_TEMPLATE, "request-start", "request start anchor"),
    required_template_geometry(STACK_TEMPLATE, "request-end", "request end anchor"),
)
STACK_RESPONSE_ANCHORS = (
    required_template_geometry(STACK_TEMPLATE, "response-start", "response start anchor"),
    required_template_geometry(STACK_TEMPLATE, "response-end", "response end anchor"),
)
STACK_REQUEST_LABEL_GEOMETRY = required_template_geometry(STACK_TEMPLATE, "request-flow-label", "request label")
STACK_RESPONSE_LABEL_GEOMETRY = required_template_geometry(STACK_TEMPLATE, "response-flow-label", "response label")
STACK_INTERNAL_FLOW_STYLE = strip_style_properties(
    STACK_REQUEST_STYLE,
    ("rounded", "strokeColor", "strokeWidth", "endArrow", "endFill", "fontColor", "labelBackgroundColor", "fontStyle"),
) + ";rounded=0;strokeColor=light-dark(#596579,#AEB8C8);strokeWidth=1.25;endArrow=classic;endFill=1;"


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
CLASS_HEADER_H = 46
CLASS_DIVIDER_H = 8
CLASS_MEMBER_ROW_H = 17
CLASS_STEREOTYPE_FONT_SIZE = 12


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


@dataclass(frozen=True)
class ClassSpec:
    key: str
    name: str
    stereotype: str
    attributes: tuple[str, ...]
    operations: tuple[str, ...]
    x: int
    y: int
    width: int
    tone: str
    node_ids: str
    table_name: str = ""


@dataclass(frozen=True)
class RelationshipSpec:
    key: str
    source: str
    target: str
    label_en: str
    label_ms: str
    kind: str = "association"
    source_multiplicity: str = ""
    target_multiplicity: str = ""
    points: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class StackCardSpec:
    key: str
    identifier: str
    slot: str
    label_en: str
    label_ms: str
    tone: str
    node_ids: str


@dataclass(frozen=True)
class StackLayerSpec:
    key: str
    identifier: str
    label_en: str
    label_ms: str
    cards: tuple[StackCardSpec, ...]


@dataclass(frozen=True)
class StackCalloutSpec:
    key: str
    identifier: str
    slot: str
    label_en: str
    label_ms: str
    node_ids: str = ""


@dataclass(frozen=True)
class StackFlowSpec:
    key: str
    source: str
    target: str
    points: tuple[tuple[float, float], ...]
    label_en: str = ""
    label_ms: str = ""
    style: str = "internal"


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


def add_child_vertex(root: ET.Element, identifier: str, parent: str, key: str,
                     label_en: str, label_ms: str, y: int, width: int, height: int,
                     style: str, compartment: str) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **attrs_for(label_en, label_ms, key),
        "umlCompartment": compartment,
    })
    cell = ET.SubElement(wrapper, "mxCell", {"parent": parent, "vertex": "1", "style": style})
    ET.SubElement(cell, "mxGeometry", {"y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
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


def stack_card_label(title: str, detail: str) -> str:
    return (
        f"<b>{html.escape(title)}</b><br>"
        f"<font style=\"font-size:11px\">{html.escape(detail)}</font>"
    )


def stack_callout_label(title: str, *lines: str) -> str:
    body = "<br>".join(html.escape(line) for line in lines)
    return f"<b>{html.escape(title)}</b><br><br>{body}"


def set_stack_headers(root: ET.Element, page: Page) -> None:
    for suffix, label_en, label_ms, style, geometry in (
        ("title", page.title_en, page.title_ms, STACK_TITLE_STYLE, STACK_TITLE_GEOMETRY),
        ("subtitle", page.subtitle_en, page.subtitle_ms, STACK_SUBTITLE_STYLE, STACK_SUBTITLE_GEOMETRY),
    ):
        identifier = f"{page.page_id}-{suffix}"
        wrapper = root.find(f".//*[@id='{identifier}']")
        if wrapper is None:
            raise RuntimeError(f"Generated stack page is missing {identifier}")
        wrapper.set("label", label_en)
        wrapper.set("labelEn", label_en)
        wrapper.set("labelMs", label_ms)
        wrapper.set("stackRole", suffix)
        wrapper.set("templateSlot", f"diagram-{suffix}")
        cell = wrapper.find("mxCell")
        if cell is None:
            raise RuntimeError(f"Generated stack page {identifier} has no mxCell")
        cell.set("style", style)
        mx_geometry = cell.find("mxGeometry")
        if mx_geometry is None:
            raise RuntimeError(f"Generated stack page {identifier} has no geometry")
        x, y, width, height = geometry
        mx_geometry.attrib.update({
            "x": str(x), "y": str(y), "width": str(width), "height": str(height),
        })


def add_stack_vertex(
    root: ET.Element,
    identifier: str,
    key: str,
    label_en: str,
    label_ms: str,
    geometry: tuple[float, float, float, float],
    style: str,
    role: str,
    template_slot: str,
    node_ids: str = "",
    **metadata: str,
) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **attrs_for(label_en, label_ms, key, node_ids),
        "stackRole": role,
        "templateSlot": template_slot,
        **metadata,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "vertex": "1", "style": style,
    })
    x, y, width, height = geometry
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry",
    })
    return identifier


def add_stack_edge(
    root: ET.Element,
    identifier: str,
    key: str,
    source: str,
    target: str,
    style: str,
    role: str,
    label_en: str = "",
    label_ms: str = "",
    points: tuple[tuple[float, float], ...] = (),
    template_slot: str = "",
    relative_x: str | None = None,
    relative_y: str | None = None,
) -> str:
    wrapper_attrs = {
        "id": identifier,
        **attrs_for(label_en, label_ms, key),
        "stackRole": role,
    }
    if template_slot:
        wrapper_attrs["templateSlot"] = template_slot
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": source, "target": target, "style": style,
    })
    geometry_attrs = {"relative": "1", "as": "geometry"}
    if relative_x is not None:
        geometry_attrs["x"] = relative_x
    if relative_y is not None:
        geometry_attrs["y"] = relative_y
    geometry = ET.SubElement(cell, "mxGeometry", geometry_attrs)
    if points:
        point_array = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in points:
            ET.SubElement(point_array, "mxPoint", {"x": str(x), "y": str(y)})
    return identifier


def add_stack_rail(
    root: ET.Element,
    prefix: str,
    direction: str,
    label_en: str,
    label_ms: str,
) -> None:
    if direction == "request":
        geometries = STACK_REQUEST_ANCHORS
        rail_style = STACK_REQUEST_STYLE
        label_style = STACK_REQUEST_LABEL_STYLE
        label_geometry = STACK_REQUEST_LABEL_GEOMETRY
        relative_y = "-16"
    elif direction == "response":
        geometries = STACK_RESPONSE_ANCHORS
        rail_style = STACK_RESPONSE_STYLE
        label_style = STACK_RESPONSE_LABEL_STYLE
        label_geometry = STACK_RESPONSE_LABEL_GEOMETRY
        relative_y = "-18"
    else:
        raise ValueError(f"Unknown stack rail direction: {direction}")
    anchor_ids: list[str] = []
    for endpoint, geometry in zip(("start", "end"), geometries, strict=True):
        anchor_ids.append(add_stack_vertex(
            root,
            f"{prefix}-{direction}-{endpoint}",
            f"{prefix}/{direction}-{endpoint}",
            "", "", geometry, STACK_ANCHOR_STYLE, "anchor", f"{direction}-{endpoint}",
            stackDirection=direction,
        ))
    add_stack_edge(
        root,
        f"{prefix}-{direction}-flow",
        f"{prefix}/{direction}-flow",
        anchor_ids[0], anchor_ids[1], rail_style, "rail",
        template_slot=f"{direction}-flow", relative_x="0.05", relative_y=relative_y,
    )
    add_stack_vertex(
        root,
        f"{prefix}-{direction}-flow-label",
        f"{prefix}/{direction}-flow-label",
        label_en, label_ms, label_geometry, label_style, "rail-label", f"{direction}-flow-label",
        stackDirection=direction,
    )


def render_stack_diagram(
    root: ET.Element,
    page: Page,
    prefix: str,
    layers: tuple[StackLayerSpec, ...],
    callouts: tuple[StackCalloutSpec, ...],
    flows: tuple[StackFlowSpec, ...],
    request_label_en: str,
    request_label_ms: str,
    response_label_en: str,
    response_label_ms: str,
    footer_en: str,
    footer_ms: str,
) -> None:
    if len(layers) != 5:
        raise ValueError(f"{prefix}: expected five stack layers, got {len(layers)}")
    if tuple(callout.slot for callout in callouts) != STACK_CALLOUT_SLOTS:
        raise ValueError(f"{prefix}: callouts must follow the seven Stack Template slots")
    set_stack_headers(root, page)

    # Depth copies must precede the foreground layers in document order.
    for index, layer in enumerate(layers):
        add_stack_vertex(
            root,
            f"{layer.identifier}-depth",
            f"{prefix}/layer-{layer.key}-depth",
            "", "", STACK_DEPTH_GEOMETRIES[index], STACK_DEPTH_STYLES[index],
            "depth", STACK_DEPTH_SLOTS[index], stackLayer=layer.key,
        )
    card_ids: set[str] = set()
    for index, layer in enumerate(layers):
        add_stack_vertex(
            root,
            layer.identifier,
            f"{prefix}/layer-{layer.key}",
            layer.label_en, layer.label_ms,
            STACK_LAYER_GEOMETRIES[index], STACK_LAYER_STYLES[index],
            "layer", STACK_LAYER_SLOTS[index], stackLayer=layer.key,
        )
        for card in layer.cards:
            if card.identifier in card_ids:
                raise ValueError(f"{prefix}: duplicate stack card id {card.identifier}")
            card_ids.add(card.identifier)
            add_stack_vertex(
                root,
                card.identifier,
                f"{prefix}/{card.key}",
                card.label_en, card.label_ms,
                STACK_CARD_GEOMETRIES[card.slot], STACK_CARD_TEMPLATE_STYLES[card.slot],
                "card", STACK_CARD_SLOTS[card.slot], card.node_ids,
                stackLayer=layer.key, tone=card.tone,
            )
    callout_ids = {callout.identifier for callout in callouts}
    known_targets = card_ids | callout_ids
    for flow in flows:
        if flow.source not in known_targets or flow.target not in known_targets:
            raise ValueError(f"{prefix}: flow {flow.key} references an unknown stack endpoint")
        if not flow.points:
            raise ValueError(f"{prefix}: flow {flow.key} requires explicit orthogonal waypoints")
        flow_style = STACK_FALLBACK_STYLE if flow.style == "fallback" else STACK_INTERNAL_FLOW_STYLE
        add_stack_edge(
            root,
            f"{prefix}-flow-{flow.key}",
            f"{prefix}/flow-{flow.key}",
            flow.source, flow.target, flow_style, "flow",
            flow.label_en, flow.label_ms, flow.points,
            "gateway-fallback-branch" if flow.style == "fallback" else "internal-flow",
        )
    # Callouts render after connectors so routed lines cannot cross their text.
    for callout in callouts:
        add_stack_vertex(
            root,
            callout.identifier,
            f"{prefix}/callout-{callout.key}",
            callout.label_en, callout.label_ms,
            STACK_CALLOUT_GEOMETRIES[callout.slot], STACK_CALLOUT_STYLES[callout.slot],
            "callout", callout.slot, callout.node_ids,
        )
    add_stack_rail(root, prefix, "request", request_label_en, request_label_ms)
    add_stack_rail(root, prefix, "response", response_label_en, response_label_ms)
    add_stack_vertex(
        root,
        f"{prefix}-source-footer",
        f"{prefix}/source-footer",
        footer_en, footer_ms,
        STACK_FOOTER_GEOMETRY, STACK_FOOTER_STYLE,
        "footer", "source-footer",
    )


def member_height(lines: tuple[str, ...]) -> int:
    return max(31, 12 + CLASS_MEMBER_ROW_H * len(lines))


def member_html(lines: tuple[str, ...]) -> str:
    return "".join(f"<div>{html.escape(line)}</div>" for line in lines)


def class_title(name: str, stereotype: str) -> str:
    stereotype_text = html.escape(f"<<{stereotype}>>")
    return (
        f"<b>{html.escape(name)}</b><br>"
        f"<span style=\"font-size:{CLASS_STEREOTYPE_FONT_SIZE}px;color:light-dark(#475467,#c5cedb);\">{stereotype_text}</span>"
    )


def add_uml_class(root: ET.Element, prefix: str, spec: ClassSpec) -> tuple[str, int]:
    identifier = f"{prefix}-{spec.key}"
    stable_key = f"{prefix}/{spec.key}"
    attributes_height = member_height(spec.attributes)
    operations_height = member_height(spec.operations) if spec.operations else 0
    raw_height = CLASS_HEADER_H + attributes_height + (CLASS_DIVIDER_H + operations_height if spec.operations else 0)
    height = ((raw_height + GRID - 1) // GRID) * GRID
    if spec.operations:
        operations_height += height - raw_height
    else:
        attributes_height += height - raw_height
    title = class_title(spec.name, spec.stereotype)
    wrapper_attrs = {
        "id": identifier,
        **attrs_for(title, title, stable_key, spec.node_ids, spec.table_name),
        "umlClass": "1",
        "stereotype": spec.stereotype,
        "tone": spec.tone,
    }
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "vertex": "1", "style": CLASS_CARD_STYLES[spec.tone],
    })
    ET.SubElement(cell, "mxGeometry", {
        "x": str(spec.x), "y": str(spec.y), "width": str(spec.width), "height": str(height), "as": "geometry",
    })
    attributes = member_html(spec.attributes)
    add_child_vertex(
        root, f"{identifier}-attributes", identifier, f"{stable_key}/attributes",
        attributes, attributes, CLASS_HEADER_H, spec.width, attributes_height, CLASS_MEMBER, "attributes",
    )
    if spec.operations:
        divider_y = CLASS_HEADER_H + attributes_height
        divider = ET.SubElement(root, "object", {
            "id": f"{identifier}-divider",
            **attrs_for("", "", f"{stable_key}/divider"),
            "umlCompartment": "divider",
        })
        divider_cell = ET.SubElement(divider, "mxCell", {
            "parent": identifier, "vertex": "1", "style": CLASS_DIVIDER,
        })
        ET.SubElement(divider_cell, "mxGeometry", {
            "y": str(divider_y), "width": str(spec.width), "height": str(CLASS_DIVIDER_H), "as": "geometry",
        })
        operations = member_html(spec.operations)
        add_child_vertex(
            root, f"{identifier}-operations", identifier, f"{stable_key}/operations",
            operations, operations, divider_y + CLASS_DIVIDER_H, spec.width, operations_height,
            CLASS_MEMBER, "operations",
        )
    return identifier, height


def add_relationship_label(root: ET.Element, identifier: str, parent: str, key: str,
                           label_en: str, label_ms: str, relative_x: float | None,
                           offset_x: int, offset_y: int, role: str) -> None:
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **attrs_for(label_en, label_ms, key),
        "umlRelationLabel": role,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": parent, "vertex": "1", "connectable": "0", "style": CLASS_RELATION_LABEL,
    })
    geometry_attrs = {"relative": "1", "as": "geometry"}
    if relative_x is not None:
        geometry_attrs["x"] = str(relative_x)
    geometry = ET.SubElement(cell, "mxGeometry", geometry_attrs)
    ET.SubElement(geometry, "mxPoint", {"x": str(offset_x), "y": str(offset_y), "as": "offset"})


def add_uml_relationship(root: ET.Element, prefix: str, spec: RelationshipSpec,
                         ids: dict[str, str]) -> str:
    identifier = f"{prefix}-relation-{spec.key}"
    stable_key = f"{prefix}/relation-{spec.key}"
    relation_styles = {
        "association": CLASS_ASSOCIATION,
        "dependency": CLASS_DEPENDENCY,
        "aggregation": CLASS_AGGREGATION,
    }
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **attrs_for("", "", stable_key),
        "umlRelationship": spec.kind,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": ids[spec.source], "target": ids[spec.target],
        "style": relation_styles[spec.kind],
    })
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if spec.points:
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in spec.points:
            ET.SubElement(points, "mxPoint", {"x": str(x), "y": str(y)})
    if spec.source_multiplicity:
        add_relationship_label(
            root, f"{identifier}-source-multiplicity", identifier,
            f"{stable_key}/source-multiplicity", spec.source_multiplicity, spec.source_multiplicity,
            -0.92, 15, -20, "source-multiplicity",
        )
    if spec.label_en:
        add_relationship_label(
            root, f"{identifier}-label", identifier, f"{stable_key}/label",
            spec.label_en, spec.label_ms, None, 0, -13, "role",
        )
    if spec.target_multiplicity:
        add_relationship_label(
            root, f"{identifier}-target-multiplicity", identifier,
            f"{stable_key}/target-multiplicity", spec.target_multiplicity, spec.target_multiplicity,
            0.92, 15, 5, "target-multiplicity",
        )
    return identifier


def add_uml_package(root: ET.Element, prefix: str, key: str, label_en: str, label_ms: str,
                    x: int, y: int, width: int, height: int, tone: str) -> str:
    label_en_html = f"<b>{html.escape(label_en.upper())}</b>"
    label_ms_html = f"<b>{html.escape(label_ms.upper())}</b>"
    identifier = f"{prefix}-package-{key}"
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **attrs_for(label_en_html, label_ms_html, f"{prefix}/package-{key}"),
        "umlPackage": "1",
        "tone": tone,
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "vertex": "1", "style": CLASS_PACKAGE_STYLES[tone],
    })
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry",
    })
    return identifier


def add_class(root: ET.Element, identifier: str, key: str, title_en: str, title_ms: str,
              body_en: str, body_ms: str, x: int, y: int, width: int, height: int,
              node_ids: str, table_name: str = "") -> str:
    """Render the legacy compact class card used by the unchanged V2 ERD."""
    return add_vertex(
        root, identifier, key, f"{title_en}\n{body_en}", f"{title_ms}\n{body_ms}",
        x, y, width, height, TABLE_BOX if table_name else CLASS_BOX, node_ids, table_name,
    )


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
    page = Page("domain.drawio", "v2_geo_domain", "V2 Georouting Domain", 2400, 1800,
                "PetaKerja Domain Classes — V2 Georouting", "Kelas Domain PetaKerja — Georouting V2",
                "Full UML contracts, entities and multiplicities derived from the supplied class template.",
                "Kontrak, entiti dan kardinaliti UML penuh berdasarkan templat kelas yang dibekalkan.")
    mxfile, root = create_page(page)
    packages = [
        ("identity", "Identity & application context", "Identiti & konteks aplikasi", 50, 130, 500, 410, "identity"),
        ("jobs", "Jobs & user status", "Kerja & status pengguna", 50, 570, 500, 1110, "jobs"),
        ("geo", "Map & geospatial contracts", "Kontrak peta & geospatial", 580, 130, 1280, 1550, "geo"),
        ("persistence", "Derived routing persistence", "Kegigihan penghalaan terbitan", 1890, 130, 460, 1550, "persistence"),
    ]
    for key, en, ms, x, y, width, height, tone in packages:
        add_uml_package(root, "domain", key, en, ms, x, y, width, height, tone)

    specs = [
        ClassSpec("user", "UserProfile", "entity: public.users", (
            "- id : uuid", "- better_auth_user_id : string", "- display_name : string | null",
            "- email : string | null", "- selected_state : string | null",
            "- role : 'user' | 'admin' | 'owner'",
        ), (), 160, 235, 280, "identity", "user-profile", "users"),
        ClassSpec("job", "JobListing", "interface", (
            "- id : string", "- title : string", "- company : string", "- companyLogo? : string",
            "- address? : string", "- location : string", "- description : string", "- salary? : string",
            "- employmentType : string", "- datePosted : string", "- applyLink : string", "- source : string",
            "- lat? : number", "- lng? : number", "- locationPrecision? : 'exact' | 'approximate' | 'remote'",
            "- matchScore? : number", "- skills? : string[]", "- remoteType? : string",
            "- experienceLevel? : string",
        ), (), 120, 690, 360, "jobs", "job-entity"),
        ClassSpec("state", "UserJobState", "entity: public.user_job_states", (
            "- id : uuid", "- user_id : uuid", "- source : UserJobSource", "- job_key : string",
            "- state : UserJobStateValue", "- job_title : string", "- company_name : string | null",
            "- apply_url : string | null", "- location : string | null", "- salary_raw : string | null",
            "- posted_at : string | null", "- notes : string | null", "- fit_score : number | null",
            "- saved_at : string", "- applied_at : string | null", "- updated_at : string",
        ), (), 120, 1150, 360, "jobs", "job-state-entity", "user_job_states"),
        ClassSpec("poi", "POI", "entity: public.pois", (
            "- id : uuid", "- name : string | null", "- category : string", "- category_group : string",
            "- lat : number", "- lng : number", "- address : string | null", "- postcode : string | null",
            "- website : string | null", "- is_verified : boolean", "- source_name : string",
            "- avg_rating : number", "- review_count : number",
        ), (), 640, 235, 340, "geo", "poi-entity", "pois"),
        ClassSpec("location", "GeoLocation", "interface", (
            "- lat : number", "- lng : number", "- label? : string",
        ), (), 1050, 235, 260, "geo", "geo-location"),
        ClassSpec("boundary", "GeoBoundary", "interface", (
            "- type : 'Feature'", "- geometry : Polygon | MultiPolygon",
            "- properties : Record<string, unknown>",
        ), (), 1410, 235, 360, "geo", "geo-place"),
        ClassSpec("place", "GeoPlace", "interface", (
            "- id : string", "- source : 'petakerja' | 'nominatim'", "- name : string",
            "- displayName : string", "- category : string", "- address : string | null",
            "- location : GeoLocation", "- boundingBox : [number, number, number, number] | null",
            "- osmType : 'node' | 'way' | 'relation' | null", "- osmId : string | null",
            "- confidence : LocationConfidence", "- boundary? : GeoBoundary | null",
            "- metadata? : Record<string, unknown>",
        ), (), 1010, 500, 390, "geo", "geo-place"),
        ClassSpec("route", "GeoRoute", "interface", (
            "- provider : 'valhalla' | 'straight-line'", "- profile : GeoRouteProfile",
            "- origin : GeoLocation", "- destination : GeoLocation", "- distanceMeters : number",
            "- durationSeconds : number | null", "- trafficAware : false",
            "- estimateKind : 'routed' | 'straight-line'", "- geometry : Feature<LineString>",
            "- maneuvers : GeoManeuver[]", "- alternatives : GeoRouteAlternative[]",
            "- dataTimestamp : string | null",
        ), (), 640, 820, 390, "geo", "geo-route"),
        ClassSpec("alternative", "GeoRouteAlternative", "interface", (
            "- id : string", "- distanceMeters : number", "- durationSeconds : number",
            "- geometry : Feature<LineString>", "- maneuvers : GeoManeuver[]",
        ), (), 1100, 840, 350, "geo", "geo-route-alternative"),
        ClassSpec("maneuver", "GeoManeuver", "interface", (
            "- instruction : string", "- distanceMeters : number", "- durationSeconds : number",
            "- beginShapeIndex? : number", "- endShapeIndex? : number", "- type? : number",
            "- streetNames? : string[]",
        ), (), 1510, 840, 290, "geo", "geo-maneuver"),
        ClassSpec("matrix", "GeoMatrixResult", "interface", (
            "- provider : 'valhalla'", "- profile : GeoRouteProfile", "- sources : GeoLocation[]",
            "- targets : GeoLocation[]", "- distancesMeters : Array<Array<number | null>>",
            "- durationsSeconds : Array<Array<number | null>>",
        ), (), 790, 1240, 410, "geo", "geo-matrix"),
        ClassSpec("isochrone", "GeoIsochroneResult", "interface", (
            "- provider : 'valhalla'", "- profile : GeoRouteProfile", "- origin : GeoLocation",
            "- contoursMinutes : number[]", "- featureCollection : FeatureCollection<Polygon | MultiPolygon>",
        ), (), 1320, 1240, 420, "geo", "geo-isochrone"),
        ClassSpec("resolution", "JobLocationResolution", "entity: public.job_location_resolutions", (
            "- id : uuid", "- scraped_job_id : string", "- source_location : string",
            "- normalized_location : string", "- display_name : string | null", "- latitude : number | null",
            "- longitude : number | null", "- geom : geometry(Point, 4326) generated",
            "- confidence : LocationConfidence", "- routable : boolean", "- is_remote : boolean",
            "- provider : string", "- osm_type : 'node' | 'way' | 'relation' | null",
            "- resolved_at : timestamptz", "- expires_at : timestamptz | null",
        ), (), 1945, 235, 350, "persistence", "job-location-resolution", "job_location_resolutions"),
        ClassSpec("route-cache", "GeoRouteCache", "entity: public.geo_route_cache", (
            "- cache_key : string", "- operation : 'route' | 'matrix' | 'isochrone'", "- provider : string",
            "- payload : jsonb", "- expires_at : timestamptz", "- last_accessed_at : timestamptz",
            "- hit_count : bigint", "- created_at : timestamptz",
        ), (), 1945, 760, 350, "persistence", "geo-route-cache", "geo_route_cache"),
        ClassSpec("geocode-cache", "GeoGeocodeCache", "entity: public.geo_geocode_cache", (
            "- cache_key : string", "- operation : 'search' | 'reverse' | 'lookup'", "- provider : string",
            "- payload : jsonb", "- expires_at : timestamptz", "- last_accessed_at : timestamptz",
            "- hit_count : bigint", "- created_at : timestamptz",
        ), (), 1945, 1160, 350, "persistence", "geo-geocode-cache", "geo_geocode_cache"),
    ]
    ids: dict[str, str] = {}
    for spec in specs:
        ids[spec.key], _ = add_uml_class(root, "domain", spec)

    relationships = [
        RelationshipSpec("place-location", "place", "location", "location", "lokasi", "association", "1", "1", ((960, 590), (960, 360))),
        RelationshipSpec("place-boundary", "place", "boundary", "boundary", "sempadan", "association", "1", "0..1", ((1450, 610), (1450, 390))),
        RelationshipSpec("route-origin", "route", "location", "origin", "asal", "association", "1", "1", ((720, 760), (1120, 760), (1120, 410))),
        RelationshipSpec("route-destination", "route", "location", "destination", "destinasi", "association", "1", "1", ((840, 790), (1220, 790), (1220, 430))),
        RelationshipSpec("route-alternatives", "route", "alternative", "alternatives", "alternatif", "aggregation", "1", "0..*"),
        RelationshipSpec("route-maneuvers", "route", "maneuver", "primary maneuvers", "arahan utama", "aggregation", "1", "0..*", ((1040, 1140), (1660, 1140))),
        RelationshipSpec("alternative-maneuvers", "alternative", "maneuver", "maneuvers", "arahan", "aggregation", "1", "0..*"),
        RelationshipSpec("matrix-locations", "matrix", "location", "sources + targets", "sumber + sasaran", "association", "1", "1..*", ((720, 1330), (610, 1330), (610, 360), (1040, 360))),
        RelationshipSpec("isochrone-origin", "isochrone", "location", "origin", "asal", "association", "1", "1", ((1780, 1320), (1825, 1320), (1825, 360), (1320, 360))),
        RelationshipSpec("resolution-place", "resolution", "place", "resolved as", "diselesaikan sebagai", "dependency", points=((1890, 620), (1815, 620), (1815, 680), (1400, 680))),
        RelationshipSpec("route-cache-route", "route-cache", "route", "stores normalized routes", "menyimpan laluan ternormal", "dependency", points=((1890, 870), (1840, 870), (1840, 1160), (1030, 1160))),
        RelationshipSpec("geocode-cache-place", "geocode-cache", "place", "stores normalized places", "menyimpan tempat ternormal", "dependency", points=((1890, 1260), (1810, 1260), (1810, 720), (1400, 720))),
        RelationshipSpec("resolution-job", "resolution", "job", "derived from scraped_job_id", "diterbitkan daripada scraped_job_id", "dependency", points=((2320, 1645), (25, 1645), (25, 900), (120, 900))),
    ]
    for relationship in relationships:
        add_uml_relationship(root, "domain", relationship, ids)
    base_note(root, page)
    write(page, mxfile)


def generate_implementation() -> None:
    page = Page("implementation.drawio", "v2_geo_implementation", "V2 Georouting Implementation", 2400, 1900,
                "Implementation Dependencies — V2 Georouting", "Kebergantungan Pelaksanaan — Georouting V2",
                "Template-derived UML classes show retained collaborators, owned managers and provider dependencies.",
                "Kelas UML berasaskan templat menunjukkan rakan tersimpan, pengurus milik dan kebergantungan penyedia.")
    mxfile, root = create_page(page)
    packages = [
        ("app", "Application composition", "Komposisi aplikasi", 50, 130, 2300, 300, "identity"),
        ("browser", "Browser managers & rendering", "Pengurus pelayar & pemaparan", 50, 460, 2300, 620, "geo"),
        ("service", "Client & server boundary", "Sempadan klien & pelayan", 50, 1110, 2300, 350, "jobs"),
        ("provider", "Providers & persistent data", "Penyedia & data kekal", 50, 1490, 2300, 320, "persistence"),
    ]
    for key, en, ms, x, y, width, height, tone in packages:
        add_uml_package(root, "implementation", key, en, ms, x, y, width, height, tone)
    specs = [
        ClassSpec("state", "AppState", "interface", (
            "- appMode : AppMode", "- map : maplibregl.Map", "- lang : 'en' | 'ms'",
            "- userLocation : [number, number] | null", "- jobFinder : JobFinderState",
        ), (), 300, 220, 400, "identity", "app-state"),
        ClassSpec("app", "MyPetaApp", "class", (
            "- state : AppState", "- mapManager : MapManager", "- mapToolsPanelManager : MapToolsPanelManager",
            "- geoNavigationManager : GeoNavigationManager | null",
            "- routeAppearanceManager : RouteAppearanceManager", "- jobFinderManager : JobFinderManager",
        ), ("+ init() : Promise<void>",), 1000, 185, 430, "identity", "mypeta-app"),
        ClassSpec("map", "MapManager", "class", (
            "- state : AppState", "- basemapMode : BasemapMode", "- baseLayersReady : boolean",
            "- jobOrbitAnimationId : number",
        ), (
            "+ init() : void", "+ getBasemapMode() : BasemapMode", "+ setBasemapMode(mode) : void",
            "+ fitBoundsGuarded(bounds, options?) : void",
        ), 100, 570, 330, "geo", "map-manager"),
        ClassSpec("tools", "MapToolsPanelManager", "class", (
            "- state : AppState", "- definitions : Map<MapToolId, MapToolDefinition>",
            "- rail : HTMLElement | null", "- drawer : HTMLElement | null",
        ), (
            "+ bind() : void", "+ registerTool(definition) : void", "+ openTool(id, focusDrawer?) : void",
            "+ close(restoreFocus?) : void", "+ getFitPadding(base?) : PaddingOptions",
        ), 480, 550, 350, "geo", "map-tools-manager"),
        ClassSpec("nav", "GeoNavigationManager", "class", (
            "- state : AppState", "- start : GeoPlace | null", "- destination : GeoPlace | null",
            "- profile : GeoRouteProfile", "- currentRoute : GeoRoute | null",
            "- routeRenderer : GeoRouteRenderer | null",
        ), ("+ bind() : void",), 880, 560, 360, "geo", "geo-navigation-manager"),
        ClassSpec("renderer", "GeoRouteRenderer", "class", (
            "- route : GeoRoute | null", "- selectedRouteId : string", "- start : GeoPlace | null",
            "- destination : GeoPlace | null", "- preview : JourneyPreviewState", "- destroyed : boolean",
        ), (
            "+ setRoute(route, selectedRouteId?) : void", "+ setSelectedRoute(routeId) : void",
            "+ setAppearance(settings) : void", "+ setEndpoints(start, destination) : void",
            "+ playPreview() : void", "+ pausePreview() : void", "+ redraw() : void", "+ destroy() : void",
        ), 1290, 500, 430, "geo", "geo-route-renderer"),
        ClassSpec("appearance", "RouteAppearanceManager", "class", (
            "- settings : RouteAppearanceSettings", "- controller : RouteAppearanceController | null",
            "- host : HTMLElement | null",
        ), (
            "+ bind() : void", "+ bindController(controller) : void", "+ getSettings() : RouteAppearanceSettings",
            "+ updatePreviewState() : void",
        ), 1780, 560, 390, "geo", "route-appearance-manager"),
        ClassSpec("job", "JobFinderManager", "class", (
            "- state : AppState", "- jobsById : Map<string, JobListing>",
            "- jobCoordsById : Map<string, [number, number]>", "- activeJobId : string | null",
            "- mapTools? : MapToolsPanelManager",
        ), (
            "+ bind() : void", "+ executeSearch() : Promise<void>", "+ onTabActivated() : void",
        ), 880, 840, 360, "geo", "job-manager"),
        ClassSpec("client", "GeoClient", "module: src/services/geo.ts", (), (
            "+ searchGeoPlaces(options) : Promise<GeoPlace[]>",
            "+ reverseGeoLocation(location, language) : Promise<GeoPlace | null>",
            "+ calculateGeoRoute(origin, destination, profile) : Promise<GeoRoute>",
            "+ calculateGeoMatrix(sources, targets, profile) : Promise<GeoMatrixResult>",
            "+ calculateGeoIsochrone(origin, contours, profile) : Promise<GeoIsochroneResult>",
            "+ resolveGeoJobLocation(jobId) : Promise<JobGeoResolution>",
        ), 230, 1200, 500, "jobs", "geo-service"),
        ClassSpec("api", "GeoApiController", "controller: server/routes/geo.ts", (), (
            "+ GET /search | /reverse | /lookup", "+ POST /route | /matrix | /isochrone",
            "+ POST /within", "+ GET /status", "+ GET /datasets/:name", "+ POST /jobs/:jobId/resolve",
        ), 850, 1200, 500, "jobs", "geo-api"),
        ClassSpec("gateway", "GeoGateway", "service: server/geo/gateway.ts", (), (
            "+ isEnabled() : boolean", "+ search(options) : Promise<GeoPlace[]>",
            "+ reverse(location, language) : Promise<GeoPlace | null>",
            "+ lookup(osmIds, language, boundary?) : Promise<GeoPlace[]>",
            "+ route(options) : Promise<GeoRoute>",
            "+ straightLineRoute(origin, destination, profile) : GeoRoute",
            "+ matrix(sources, targets, profile) : Promise<GeoMatrixResult>",
            "+ isochrone(origin, contours, profile) : Promise<GeoIsochroneResult>",
            "+ status() : Promise<GeoStatus>",
        ), 1440, 1145, 800, "jobs", "geo-gateway"),
        ClassSpec("supabase", "Supabase / PostGIS", "database", (
            "- geo_geocode_cache : server-only", "- geo_route_cache : server-only",
            "- job_location_resolutions : server-only",
        ), (), 150, 1600, 480, "persistence", "supabase-db"),
        ClassSpec("valhalla", "Valhalla", "external service: enabled", (
            "- provider : 'valhalla'", "- enabled : true", "- available : true",
        ), ("+ route()", "+ matrix()", "+ isochrone()"), 760, 1570, 400, "persistence", "valhalla"),
        ClassSpec("nominatim", "Nominatim", "external service: disabled", (
            "- provider : 'nominatim'", "- enabled : false", "- available : false",
        ), ("+ search()", "+ reverse()", "+ lookup()"), 1310, 1570, 420, "persistence", "nominatim"),
    ]
    ids: dict[str, str] = {}
    for spec in specs:
        ids[spec.key], _ = add_uml_class(root, "implementation", spec)
    relationships = [
        RelationshipSpec("app-state", "app", "state", "owns state", "memiliki keadaan", "association", "1", "1"),
        RelationshipSpec("app-map", "app", "map", "owns", "memiliki", "aggregation", "1", "1", ((900, 400), (265, 400), (265, 570))),
        RelationshipSpec("app-tools", "app", "tools", "owns", "memiliki", "aggregation", "1", "1", ((940, 420), (655, 420), (655, 550))),
        RelationshipSpec("app-nav", "app", "nav", "owns", "memiliki", "aggregation", "1", "0..1"),
        RelationshipSpec("app-appearance", "app", "appearance", "owns", "memiliki", "aggregation", "1", "1", ((1450, 400), (1975, 400), (1975, 560))),
        RelationshipSpec("app-job", "app", "job", "owns", "memiliki", "aggregation", "1", "1", ((1110, 430), (1110, 840))),
        RelationshipSpec("nav-map", "nav", "map", "retains", "menyimpan", "association", "1", "1", ((850, 730), (430, 730))),
        RelationshipSpec("nav-tools", "nav", "tools", "retains", "menyimpan", "association", "1", "1"),
        RelationshipSpec("nav-renderer", "nav", "renderer", "creates", "mencipta", "aggregation", "1", "0..1"),
        RelationshipSpec("nav-appearance", "nav", "appearance", "binds controller", "mengikat pengawal", "association", "1", "1", ((1260, 790), (1750, 790))),
        RelationshipSpec("job-nav", "job", "nav", "emits workplace destination", "memancar destinasi tempat kerja", "dependency", points=((1060, 840), (1060, 800))),
        RelationshipSpec("nav-client", "nav", "client", "calls typed geo client", "memanggil klien geo berjenis", "dependency", points=((850, 1035), (760, 1035), (760, 1190), (650, 1190))),
        RelationshipSpec("job-client", "job", "client", "resolves workplace", "menyelesaikan tempat kerja", "dependency", points=((850, 1000), (700, 1000), (700, 1170), (600, 1170))),
        RelationshipSpec("client-api", "client", "api", "same-origin /api/geo/*", "asal sama /api/geo/*", "dependency"),
        RelationshipSpec("api-gateway", "api", "gateway", "validates and delegates", "mengesah dan mewakilkan", "association", "1", "1"),
        RelationshipSpec("gateway-supabase", "gateway", "supabase", "reads and writes normalized cache", "membaca dan menulis cache ternormal", "dependency", points=((1470, 1450), (390, 1450), (390, 1600))),
        RelationshipSpec("gateway-valhalla", "gateway", "valhalla", "route, matrix and isochrone", "laluan, matriks dan isokron", "dependency", points=((1620, 1460), (960, 1460), (960, 1570))),
        RelationshipSpec("gateway-nominatim", "gateway", "nominatim", "search only when enabled", "carian hanya apabila diaktifkan", "dependency", points=((1760, 1460), (1520, 1460), (1520, 1570))),
    ]
    for relationship in relationships:
        add_uml_relationship(root, "implementation", relationship, ids)
    add_text(
        root, "implementation-fallback-constraint", "implementation/fallback-constraint",
        "{constraint} straightLineRoute sets estimateKind='straight-line',<br>durationSeconds=null and maneuvers=[];<br>it is a non-navigable fallback.",
        "{kekangan} straightLineRoute menetapkan estimateKind='straight-line',<br>durationSeconds=null dan maneuvers=[];<br>ia sandaran yang tidak boleh dinavigasi.",
        1440, 1370, 800, 75, TEXT + "align=left;verticalAlign=middle;fontStyle=2;",
    )
    base_note(root, page)
    write(page, mxfile)


def generate_architecture() -> None:
    page = Page("architecture.drawio", "v2_geo_architecture", "V2 Georouting Layered Architecture", 1900, 1180,
                "Layered Architecture — V2 Georouting", "Seni Bina Berlapis — Georouting V2",
                "Broad georouting capabilities arranged on the supplied five-layer responsibility stack.",
                "Keupayaan georouting luas disusun pada tindanan tanggungjawab lima lapisan yang dibekalkan.")
    mxfile, root = create_page(page)
    layers = (
        StackLayerSpec("inputs", "arch-layer-inputs", "<b>LAYER 1 · INPUTS &amp; CONSUMERS</b>", "<b>LAPISAN 1 · INPUT &amp; PENGGUNA</b>", (
            StackCardSpec("search", "arch-search", "input-left",
                          stack_card_label("Place, address & boundary", "Search · reverse · POI within"),
                          stack_card_label("Tempat, alamat & sempadan", "Cari · songsang · POI dalam"),
                          "neutral", "search-manager,geo-place"),
            StackCardSpec("ab", "arch-ab", "input-center",
                          stack_card_label("A/B, GPS & travel profile", "Route · matrix · isochrone intent"),
                          stack_card_label("A/B, GPS & profil perjalanan", "Niat laluan · matriks · isokron"),
                          "neutral", "geo-navigation-manager,geo-location"),
            StackCardSpec("job", "arch-job", "input-right",
                          stack_card_label("Workplace / Geo Studio", "Job destination · analysis handoff"),
                          stack_card_label("Tempat kerja / Studio Geo", "Destinasi kerja · serahan analisis"),
                          "neutral", "job-manager,geo-studio"),
        )),
        StackLayerSpec("render", "arch-layer-render", "<b>LAYER 2 · MAPLIBRE RENDERING</b>", "<b>LAPISAN 2 · PEMAPARAN MAPLIBRE</b>", (
            StackCardSpec("maplibre", "arch-maplibre", "render-left",
                          stack_card_label("Routes & alternatives", "Lines · markers · maneuvers · camera fit"),
                          stack_card_label("Laluan & alternatif", "Garisan · penanda · arahan · pelarasan kamera"),
                          "render", "maplibre-gl"),
            StackCardSpec("renderer", "arch-renderer", "render-right",
                          stack_card_label("Analytical overlays", "Isochrones · boundaries · Geo Studio layers"),
                          stack_card_label("Tindihan analisis", "Isokron · sempadan · lapisan Studio Geo"),
                          "render", "geo-route-renderer,maplibre-gl,geo-studio"),
        )),
        StackLayerSpec("browser", "arch-layer-browser", "<b>LAYER 3 · BROWSER ORCHESTRATION</b>", "<b>LAPISAN 3 · ORKESTRASI PELAYAR</b>", (
            StackCardSpec("tools", "arch-tools", "browser-left",
                          stack_card_label("Map Tools + SearchManager", "Intent · panels · place discovery"),
                          stack_card_label("Alat Peta + SearchManager", "Niat · panel · penemuan tempat"),
                          "browser", "map-tools-manager,search-manager"),
            StackCardSpec("nav", "arch-nav", "browser-center",
                          stack_card_label("GeoNavigationManager", "A/B · profiles · alternatives · analysis"),
                          stack_card_label("GeoNavigationManager", "A/B · profil · alternatif · analisis"),
                          "browser", "geo-navigation-manager,geo-route-renderer"),
            StackCardSpec("client", "arch-client", "browser-right",
                          stack_card_label("JobFinder + geo client", "Workplace confidence · typed requests"),
                          stack_card_label("JobFinder + klien geo", "Keyakinan tempat kerja · permintaan berjenis"),
                          "browser", "job-manager,geo-service"),
        )),
        StackLayerSpec("gateway", "arch-layer-gateway", "<b>LAYER 4 · SAME-ORIGIN GEOGATEWAY</b>", "<b>LAPISAN 4 · GEOGATEWAY ASAL SAMA</b>", (
            StackCardSpec("fallback", "arch-fallback", "gateway-left",
                          stack_card_label("Safety, cache & fallback", "Malaysia bounds · rate limits · labels"),
                          stack_card_label("Keselamatan, cache & sandaran", "Had Malaysia · had kadar · label"),
                          "gateway", "geo-gateway"),
            StackCardSpec("gateway", "arch-gateway", "gateway-center",
                          stack_card_label("GeoGateway", "Provider-neutral normalization"),
                          stack_card_label("GeoGateway", "Normalisasi bebas penyedia"),
                          "gateway", "geo-gateway"),
            StackCardSpec("api", "arch-api", "gateway-right",
                          stack_card_label("Express /api/geo/*", "Same-origin API surface"),
                          stack_card_label("Express /api/geo/*", "Permukaan API asal sama"),
                          "gateway", "geo-api"),
        )),
        StackLayerSpec("providers", "arch-layer-providers", "<b>LAYER 5 · PROVIDERS &amp; PERSISTENCE</b>", "<b>LAPISAN 5 · PENYEDIA &amp; KEKALAN</b>", (
            StackCardSpec("nominatim", "arch-nominatim", "provider-left",
                          stack_card_label("Nominatim · disabled", "Search · reverse · boundary lookup"),
                          stack_card_label("Nominatim · dinyahaktifkan", "Cari · songsang · carian sempadan"),
                          "neutral", "nominatim"),
            StackCardSpec("valhalla", "arch-valhalla", "provider-center",
                          stack_card_label("Valhalla · enabled", "Routes · alternatives · matrix · isochrone"),
                          stack_card_label("Valhalla · diaktifkan", "Laluan · alternatif · matriks · isokron"),
                          "provider", "valhalla"),
            StackCardSpec("cache", "arch-cache", "provider-right",
                          stack_card_label("Supabase / PostGIS", "Routing cache · workplace resolutions"),
                          stack_card_label("Supabase / PostGIS", "Cache laluan · penyelesaian tempat kerja"),
                          "provider", "supabase-db,geo-route-cache,job-location-resolution"),
        )),
    )
    callouts = (
        StackCalloutSpec("takeaway", "arch-callout-takeaway", "takeaway",
                         stack_callout_label("ARCHITECTURE AT A GLANCE", "Intent enters once", "Browser coordinates capabilities", "Providers remain replaceable"),
                         stack_callout_label("RINGKASAN SENI BINA", "Niat masuk sekali", "Pelayar menyelaras keupayaan", "Penyedia kekal boleh diganti")),
        StackCalloutSpec("maplibre", "arch-callout-maplibre", "maplibre-boundary",
                         stack_callout_label("MAPLIBRE IS THE VISUAL BOUNDARY", "It renders route and analytical GeoJSON.", "It does not calculate routes or search addresses."),
                         stack_callout_label("MAPLIBRE IALAH SEMPADAN VISUAL", "Ia memapar GeoJSON laluan dan analisis.", "Ia tidak mengira laluan atau mencari alamat."), "maplibre-gl"),
        StackCalloutSpec("analysis", "arch-callout-analysis", "navigation-control-note",
                         stack_callout_label("ANALYTICS", "Matrix + isochrone + boundary flows stay explicit."),
                         stack_callout_label("ANALISIS", "Aliran matriks + isokron + sempadan kekal jelas."), "geo-navigation-manager"),
        StackCalloutSpec("workplace", "arch-callout-workplace", "directions-plugin-note",
                         stack_callout_label("WORKPLACE ROUTING", "Remote and low-confidence jobs are rejected before routing."),
                         stack_callout_label("PENGHALAAN TEMPAT KERJA", "Kerja jarak jauh dan keyakinan rendah ditolak sebelum penghalaan."), "job-manager"),
        StackCalloutSpec("studio", "arch-callout-studio", "side-flows",
                         stack_callout_label("GEO STUDIO HANDOFF", "Normalized boundaries and analytical outputs can open as editable workspace context."),
                         stack_callout_label("SERAHAN STUDIO GEO", "Sempadan ternormal dan output analisis boleh dibuka sebagai konteks ruang kerja boleh sunting."), "geo-studio"),
        StackCalloutSpec("fallback", "arch-callout-fallback", "fallback-note",
                         stack_callout_label("GATED SEARCH + HONEST FALLBACK", "Nominatim calls stop while disabled.", "Straight-line fallback has no ETA, maneuvers", "or navigable-route claim."),
                         stack_callout_label("CARIAN BERPAGAR + SANDARAN JUJUR", "Panggilan Nominatim berhenti ketika dinyahaktifkan.", "Sandaran garis lurus tiada ETA, arahan", "atau dakwaan laluan boleh dinavigasi."), "geo-gateway,nominatim"),
        StackCalloutSpec("status", "arch-callout-status", "rollout-status",
                         stack_callout_label("RUNTIME · 2026-07-19", "Valhalla + shared cache available", "Nominatim disabled · ETA traffic-independent"),
                         stack_callout_label("MASA JALAN · 2026-07-19", "Valhalla + cache bersama tersedia", "Nominatim dinyahaktifkan · ETA bebas trafik")),
    )
    flows = (
        StackFlowSpec("ab-to-route-render", "arch-ab", "arch-maplibre", ((680, 305), (490, 305))),
        StackFlowSpec("job-to-analysis-render", "arch-job", "arch-renderer", ((887.5, 320), (825, 320))),
        StackFlowSpec("tools-to-navigation", "arch-tools", "arch-nav", ((545, 576),)),
        StackFlowSpec("navigation-to-client", "arch-nav", "arch-client", ((835, 576),)),
        StackFlowSpec("navigation-to-renderer", "arch-nav", "arch-renderer", ((690, 655), (1180, 655), (1180, 393), (975, 393))),
        StackFlowSpec("client-to-api", "arch-client", "arch-api", ((955, 680), (930, 680))),
        StackFlowSpec("api-to-gateway", "arch-api", "arch-gateway", ((768, 761),)),
        StackFlowSpec("gateway-to-safety", "arch-gateway", "arch-fallback", ((498, 761),)),
        StackFlowSpec("gateway-to-valhalla", "arch-gateway", "arch-valhalla", ((632.5, 865), (665, 865))),
        StackFlowSpec("gateway-to-nominatim", "arch-gateway", "arch-nominatim", ((632.5, 850), (180, 850), (180, 961), (210, 961))),
        StackFlowSpec("safety-to-cache", "arch-fallback", "arch-cache", ((370, 845), (1180, 845), (1180, 961), (1115, 961))),
        StackFlowSpec("fallback-constraint", "arch-fallback", "arch-callout-fallback", ((370, 840), (1250, 840), (1250, 980), (1570, 980), (1570, 975)), style="fallback"),
    )
    render_stack_diagram(
        root, page, "architecture", layers, callouts, flows,
        "INTENT + REQUEST ↓<br>A/B · jobs · analytics<br>/api/geo/*",
        "NIAT + PERMINTAAN ↓<br>A/B · kerja · analisis<br>/api/geo/*",
        "RESULTS ↑<br>normalized GeoJSON<br>routes + polygons",
        "HASIL ↑<br>GeoJSON ternormal<br>laluan + poligon",
        "Source-grounded in Map Tools, GeoNavigationManager, JobFinderManager, src/services/geo.ts, Express /api/geo/* and GeoGateway. Current ETA is traffic-independent.",
        "Berasaskan sumber Alat Peta, GeoNavigationManager, JobFinderManager, src/services/geo.ts, Express /api/geo/* dan GeoGateway. ETA semasa tidak mengambil kira trafik.",
    )
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
    page = Page("routing-stack.drawio", "v2_geo_routing_stack", "V2 Routing Responsibility Stack", 1900, 1180,
                "A-to-B Routing Responsibilities — V2", "Tanggungjawab Penghalaan A-ke-B — V2",
                "Focused request and normalized-response ownership on the supplied five-layer stack.",
                "Pemilikan permintaan dan respons ternormal yang berfokus pada tindanan lima lapisan yang dibekalkan.")
    mxfile, root = create_page(page)
    layers = (
        StackLayerSpec("inputs", "stack-layer-inputs", "<b>LAYER 1 · ROUTE INPUTS</b>", "<b>LAPISAN 1 · INPUT LALUAN</b>", (
            StackCardSpec("origin", "stack-origin", "input-left",
                          stack_card_label("Origin A", "Map click · selected place"),
                          stack_card_label("Asal A", "Klik peta · tempat dipilih"),
                          "neutral", "geo-location,geo-navigation-manager"),
            StackCardSpec("input", "stack-input", "input-center",
                          stack_card_label("Destination B", "Map click · selected workplace"),
                          stack_card_label("Destinasi B", "Klik peta · tempat kerja dipilih"),
                          "neutral", "geo-location,job-manager"),
            StackCardSpec("profile", "stack-profile", "input-right",
                          stack_card_label("GPS + profile", "Current location · drive/walk/cycle"),
                          stack_card_label("GPS + profil", "Lokasi semasa · pandu/jalan/basikal"),
                          "neutral", "geo-location,geo-navigation-manager"),
        )),
        StackLayerSpec("render", "stack-layer-render", "<b>LAYER 2 · MAPLIBRE RENDERING</b>", "<b>LAPISAN 2 · PEMAPARAN MAPLIBRE</b>", (
            StackCardSpec("map", "stack-map", "render-left",
                          stack_card_label("MapLibre route rendering", "Primary + alternatives · A/B markers"),
                          stack_card_label("Pemaparan laluan MapLibre", "Utama + alternatif · penanda A/B"),
                          "render", "maplibre-gl"),
            StackCardSpec("rendering", "stack-rendering", "render-right",
                          stack_card_label("Route interaction", "Selection · maneuvers · camera fit"),
                          stack_card_label("Interaksi laluan", "Pemilihan · arahan · pelarasan kamera"),
                          "render", "geo-route-renderer,maplibre-gl"),
        )),
        StackLayerSpec("browser", "stack-layer-browser", "<b>LAYER 3 · BROWSER ORCHESTRATION</b>", "<b>LAPISAN 3 · ORKESTRASI PELAYAR</b>", (
            StackCardSpec("nav", "stack-nav", "browser-left",
                          stack_card_label("GeoNavigationManager", "A/B state · profile · alternatives"),
                          stack_card_label("GeoNavigationManager", "Keadaan A/B · profil · alternatif"),
                          "browser", "geo-navigation-manager"),
            StackCardSpec("renderer", "stack-renderer", "browser-center",
                          stack_card_label("GeoRouteRenderer", "Ordered sources · layers · selection"),
                          stack_card_label("GeoRouteRenderer", "Sumber tersusun · lapisan · pemilihan"),
                          "browser", "geo-route-renderer"),
            StackCardSpec("client", "stack-client", "browser-right",
                          stack_card_label("src/services/geo.ts", "Typed same-origin route request"),
                          stack_card_label("src/services/geo.ts", "Permintaan laluan asal sama berjenis"),
                          "browser", "geo-service"),
        )),
        StackLayerSpec("gateway", "stack-layer-gateway", "<b>LAYER 4 · API &amp; GEOGATEWAY</b>", "<b>LAPISAN 4 · API &amp; GEOGATEWAY</b>", (
            StackCardSpec("safety", "stack-safety", "gateway-left",
                          stack_card_label("Safety + fallback", "Malaysia bounds · limits · explicit label"),
                          stack_card_label("Keselamatan + sandaran", "Had Malaysia · had kadar · label jelas"),
                          "gateway", "geo-gateway"),
            StackCardSpec("gateway", "stack-gateway", "gateway-center",
                          stack_card_label("GeoGateway", "Cache key · dispatch · normalize"),
                          stack_card_label("GeoGateway", "Kunci cache · agihan · normalisasi"),
                          "gateway", "geo-gateway"),
            StackCardSpec("api", "stack-api", "gateway-right",
                          stack_card_label("Express /api/geo/route", "Validate · authenticate · rate-limit"),
                          stack_card_label("Express /api/geo/route", "Sah · pengesahan · had kadar"),
                          "gateway", "geo-api"),
        )),
        StackLayerSpec("providers", "stack-layer-providers", "<b>LAYER 5 · CACHE &amp; PROVIDERS</b>", "<b>LAPISAN 5 · CACHE &amp; PENYEDIA</b>", (
            StackCardSpec("nominatim", "stack-nominatim", "provider-left",
                          stack_card_label("Nominatim · disabled", "Not used for A-to-B calculations"),
                          stack_card_label("Nominatim · dinyahaktifkan", "Tidak digunakan untuk pengiraan A-ke-B"),
                          "neutral", "nominatim"),
            StackCardSpec("valhalla", "stack-valhalla", "provider-center",
                          stack_card_label("Valhalla · enabled", "Road route · alternatives · maneuvers"),
                          stack_card_label("Valhalla · diaktifkan", "Laluan jalan · alternatif · arahan"),
                          "provider", "valhalla"),
            StackCardSpec("cache", "stack-cache", "provider-right",
                          stack_card_label("Supabase cache · available", "Stable normalized route results"),
                          stack_card_label("Cache Supabase · tersedia", "Hasil laluan ternormal stabil"),
                          "provider", "supabase-db,geo-route-cache"),
        )),
    )
    callouts = (
        StackCalloutSpec("takeaway", "stack-callout-takeaway", "takeaway",
                         stack_callout_label("THE BOTTOM LINE", "MapLibre = visualizer", "GeoGateway = orchestrator", "Valhalla = route calculator"),
                         stack_callout_label("RINGKASANNYA", "MapLibre = pemapar", "GeoGateway = pengatur", "Valhalla = pengira laluan")),
        StackCalloutSpec("maplibre", "stack-callout-maplibre", "maplibre-boundary",
                         stack_callout_label("MAPLIBRE DOES NOT ROUTE", "It draws normalized route GeoJSON and handles interaction.", "Road calculations remain outside the renderer."),
                         stack_callout_label("MAPLIBRE TIDAK MENGHALA", "Ia melukis GeoJSON laluan ternormal dan mengurus interaksi.", "Pengiraan jalan kekal di luar pemapar."), "maplibre-gl"),
        StackCalloutSpec("eta", "stack-callout-eta", "navigation-control-note",
                         stack_callout_label("ETA", "Duration is provider-derived and traffic-independent."),
                         stack_callout_label("ETA", "Tempoh diperoleh daripada penyedia dan bebas trafik."), "geo-gateway"),
        StackCalloutSpec("response", "stack-callout-response", "directions-plugin-note",
                         stack_callout_label("NORMALIZED RESPONSE", "Route geometry, alternatives, distance, duration and maneuvers share one contract."),
                         stack_callout_label("RESPONS TERNORMAL", "Geometri laluan, alternatif, jarak, tempoh dan arahan berkongsi satu kontrak."), "geo-service,geo-gateway"),
        StackCalloutSpec("dispatch", "stack-callout-dispatch", "side-flows",
                         stack_callout_label("CACHE + PROVIDER DISPATCH", "Stable keys can return cached output before Valhalla is called."),
                         stack_callout_label("CACHE + AGIHAN PENYEDIA", "Kunci stabil boleh memulangkan output cache sebelum Valhalla dipanggil."), "geo-gateway,geo-route-cache"),
        StackCalloutSpec("fallback", "stack-fallback", "fallback-note",
                         stack_callout_label("LABELLED FALLBACK ONLY", "Provider failure → Haversine straight line", "No ETA · no maneuvers", "No navigable-route claim"),
                         stack_callout_label("SANDARAN BERLABEL SAHAJA", "Kegagalan penyedia → garis lurus Haversine", "Tiada ETA · tiada arahan", "Tiada dakwaan laluan boleh dinavigasi"), "geo-gateway"),
        StackCalloutSpec("status", "stack-callout-status", "rollout-status",
                         stack_callout_label("RUNTIME · 2026-07-19", "Valhalla + shared cache available", "Nominatim disabled · ETA traffic-independent"),
                         stack_callout_label("MASA JALAN · 2026-07-19", "Valhalla + cache bersama tersedia", "Nominatim dinyahaktifkan · ETA bebas trafik")),
    )
    flows = (
        StackFlowSpec("destination-to-navigation", "stack-input", "stack-nav", ((680, 300), (170, 300), (170, 576), (300, 576))),
        StackFlowSpec("navigation-to-renderer", "stack-nav", "stack-renderer", ((545, 576),)),
        StackFlowSpec("renderer-to-client", "stack-renderer", "stack-client", ((835, 576),)),
        StackFlowSpec("renderer-to-map", "stack-renderer", "stack-map", ((690, 655), (170, 655), (170, 393), (335, 393))),
        StackFlowSpec("map-to-interaction", "stack-map", "stack-rendering", ((660, 393),)),
        StackFlowSpec("client-to-api", "stack-client", "stack-api", ((955, 680), (930, 680))),
        StackFlowSpec("api-to-gateway", "stack-api", "stack-gateway", ((768, 761),)),
        StackFlowSpec("gateway-to-safety", "stack-gateway", "stack-safety", ((498, 761),)),
        StackFlowSpec("gateway-to-valhalla", "stack-gateway", "stack-valhalla", ((632.5, 865), (665, 865))),
        StackFlowSpec("gateway-to-nominatim", "stack-gateway", "stack-nominatim", ((632.5, 850), (180, 850), (180, 961), (210, 961))),
        StackFlowSpec("safety-to-cache", "stack-safety", "stack-cache", ((370, 845), (1180, 845), (1180, 961), (1115, 961))),
        StackFlowSpec("fallback-constraint", "stack-safety", "stack-fallback", ((370, 840), (1250, 840), (1250, 980), (1570, 980), (1570, 975)), style="fallback"),
    )
    render_stack_diagram(
        root, page, "routing-stack", layers, callouts, flows,
        "REQUEST ↓<br>A + B + profile<br>POST /api/geo/route",
        "PERMINTAAN ↓<br>A + B + profil<br>POST /api/geo/route",
        "RESPONSE ↑<br>normalized route<br>distance · duration",
        "RESPONS ↑<br>laluan ternormal<br>jarak · tempoh",
        "Source-grounded in GeoNavigationManager, GeoRouteRenderer, src/services/geo.ts, Express /api/geo/route and GeoGateway. Current ETA is traffic-independent.",
        "Berasaskan sumber GeoNavigationManager, GeoRouteRenderer, src/services/geo.ts, Express /api/geo/route dan GeoGateway. ETA semasa tidak mengambil kira trafik.",
    )
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
