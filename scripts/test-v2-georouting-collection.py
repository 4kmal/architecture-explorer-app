#!/usr/bin/env python3
"""Regression checks for the isolated V2 Georouting Explorer collection."""

from __future__ import annotations

import json
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDS = {
    "v2-geo-usecase": ("usecase.drawio", "v2_geo_usecase", "usecase.svg", "usecase"),
    "v2-geo-map-flowchart": ("map-flowchart.drawio", "v2_geo_map_flowchart", "map-flowchart.svg", "user-explore-3d-map-flowchart"),
    "v2-geo-route-sequence": ("route-sequence.drawio", "v2_geo_route_sequence", "route-sequence.svg", "user-explore-3d-map-sequence"),
    "v2-geo-travel-analysis-sequence": ("travel-analysis-sequence.drawio", "v2_geo_travel_analysis_sequence", "travel-analysis-sequence.svg", None),
    "v2-geo-job-route-sequence": ("job-route-sequence.drawio", "v2_geo_job_route_sequence", "job-route-sequence.svg", None),
    "v2-geo-domain": ("domain.drawio", "v2_geo_domain", "domain.svg", "domain"),
    "v2-geo-implementation": ("implementation.drawio", "v2_geo_implementation", "implementation.svg", "implementation"),
    "v2-geo-architecture": ("architecture.drawio", "v2_geo_architecture", "architecture.svg", "architecture"),
    "v2-geo-modules": ("modules.drawio", "v2_geo_modules", "modules.svg", "modules"),
    "v2-geo-data-flow": ("data-flow.drawio", "v2_geo_data_flow", "data-flow.svg", "data-flow"),
    "v2-geo-erd": ("erd.drawio", "v2_geo_erd", "erd.svg", "erd"),
    "v2-geo-routing-stack": ("routing-stack.drawio", "v2_geo_routing_stack", "routing-stack.svg", "map-routing-responsibility-stack"),
    "v2-geo-supabase": ("supabase.drawio", "v2_geo_supabase", "supabase.svg", "supabase"),
}
SEQUENCES = {
    "v2-geo-route-sequence", "v2-geo-travel-analysis-sequence", "v2-geo-job-route-sequence",
}
COLLECTION_GROUPS = {
    "v2-geo-usecase": "use-cases",
    "v2-geo-map-flowchart": "flowcharts",
    "v2-geo-route-sequence": "sequences",
    "v2-geo-travel-analysis-sequence": "sequences",
    "v2-geo-job-route-sequence": "sequences",
    "v2-geo-domain": "classes",
    "v2-geo-implementation": "classes",
    "v2-geo-architecture": "architecture-modules",
    "v2-geo-modules": "architecture-modules",
    "v2-geo-data-flow": "data",
    "v2-geo-erd": "data",
    "v2-geo-routing-stack": "architecture-modules",
    "v2-geo-supabase": "data",
}
GROUP_COUNTS = {
    "use-cases": 1, "flowcharts": 1, "sequences": 3,
    "classes": 2, "architecture-modules": 3, "data": 3,
}
SEQUENCE_ROWS = {
    "v2-geo-route-sequence": [245 + 50 * index for index in range(15)],
    "v2-geo-travel-analysis-sequence": [270 + 50 * index for index in range(17)],
    "v2-geo-job-route-sequence": [250, 300, 350, 400, 500, 550, 650, 800, 850, 900, 1050, 1100, 1150, 1250],
}
SEQUENCE_FRAGMENTS = {
    "v2-geo-route-sequence": {"route/fragment-cache": "alt", "route/fragment-provider": "alt"},
    "v2-geo-travel-analysis-sequence": {
        "travel/fragment-matrix": "opt", "travel/fragment-isochrone": "opt",
        "travel/fragment-boundary": "opt", "travel/fragment-geocoder": "alt",
    },
    "v2-geo-job-route-sequence": {
        "jobroute/fragment-resolution": "alt", "jobroute/fragment-remote": "alt",
        "jobroute/fragment-geocoder": "alt", "jobroute/fragment-routable": "alt",
    },
}
GEO_TABLES = {
    "geo_geocode_cache", "geo_route_cache", "job_location_resolutions", "geo_workspaces", "geo_workspace_assets",
}
ACTOR_SIZE = (70.0, 140.0)
USECASE_HEIGHT = 62.0
PARTICIPANT_SIZE = (100.0, 60.0)
SEQUENCE_ACTOR_SIZE = (20.0, 40.0)
LIFELINE_WIDTH = 10.0
SEQUENCE_TEMPLATE = ROOT / "templates" / "Sequence Diagram Template.drawio"
CLASS_TEMPLATE = ROOT / "templates" / "Class Diagram Template.drawio"
CLASS_DEFAULT_SOURCE = ROOT / "assets" / "editor" / "class-domain-petakerja.drawio"
CLASS_TITLE_FONT_SIZE = 16
CLASS_STEREOTYPE_FONT_SIZE = 12
CLASS_MEMBER_FONT_SIZE = 14
CLASS_DEFAULT_GEOMETRIES = {
    "domain/job-entity": (80.0, 1420.0, 270.94, 359.0),
    "domain/job-state-entity": (500.0, 1275.88, 275.66, 365.25),
    "domain/open-data-api": (890.0, 1910.0, 350.0, 192.5),
    "domain/poi-category-entity": (1840.0, 1788.5, 393.57, 268.0),
    "domain/poi-group-entity": (1840.0, 2360.0, 396.33, 180.0),
}
STACK_TEMPLATE = ROOT / "templates" / "Stack Template.drawio"
STACK_DIAGRAMS = {"v2-geo-architecture", "v2-geo-routing-stack"}
STACK_PAGE_SIZE = (1900.0, 1180.0)
CLASS_PAGE_SIZES = {
    "v2-geo-domain": (2400.0, 1800.0),
    "v2-geo-implementation": (2400.0, 1900.0),
}
CLASS_COUNTS = {"v2-geo-domain": 15, "v2-geo-implementation": 14}
DOMAIN_CLASS_KEYS = {
    "domain/user", "domain/job", "domain/state", "domain/poi", "domain/location",
    "domain/boundary", "domain/place", "domain/route", "domain/alternative", "domain/maneuver",
    "domain/matrix", "domain/isochrone", "domain/resolution", "domain/route-cache", "domain/geocode-cache",
}
IMPLEMENTATION_CLASS_KEYS = {
    "implementation/state", "implementation/app", "implementation/map", "implementation/tools",
    "implementation/nav", "implementation/renderer", "implementation/appearance", "implementation/job",
    "implementation/client", "implementation/api", "implementation/gateway", "implementation/supabase",
    "implementation/valhalla", "implementation/nominatim",
}

STACK_LAYER_SLOTS = ("layer1-inputs", "layer2-maplibre", "layer3-browser", "layer4-gateway", "layer5-providers")
STACK_DEPTH_SLOTS = ("layer1-depth", "layer2-depth", "layer3-depth", "layer4-depth", "layer5-depth")
STACK_CARD_SLOTS = {
    "input-search", "input-ab", "input-gps", "maplibre-current", "maplibre-capability",
    "browser-search-manager", "browser-navigation-manager", "browser-geo-service",
    "gateway-express", "gateway-core", "gateway-guards",
    "provider-nominatim", "provider-valhalla", "provider-supabase",
}
STACK_CALLOUT_SLOTS = {
    "takeaway", "maplibre-boundary", "navigation-control-note", "directions-plugin-note",
    "side-flows", "fallback-note", "rollout-status",
}
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


def cell_style(wrapper: ET.Element) -> str:
    cell = wrapper.find("mxCell")
    return cell.get("style", "") if cell is not None else ""


def required_template_style(template: Path, predicate, description: str) -> str:
    for cell in ET.parse(template).getroot().findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError(f"{template.name} is missing {description}")


def template_label(cell: ET.Element) -> str:
    return html.unescape(cell.get("labelEn") or cell.get("value", ""))


def strip_style_properties(style: str, names: tuple[str, ...]) -> str:
    for name in names:
        style = re.sub(rf"(?:^|;){name}=[^;]*;?", ";", style)
    return style.strip(";")


def required_template_element(template: Path, identifier: str) -> ET.Element:
    element = ET.parse(template).getroot().find(f".//*[@id='{identifier}']")
    if element is None:
        raise RuntimeError(f"{template.name} is missing {identifier}")
    return element


def required_template_cell(template: Path, identifier: str) -> ET.Element:
    element = required_template_element(template, identifier)
    cell = element.find("mxCell") if element.tag == "object" else element
    if cell is None:
        raise RuntimeError(f"{template.name} {identifier} has no mxCell")
    return cell


def template_geometry(template: Path, identifier: str) -> tuple[float, float, float, float]:
    node = required_template_cell(template, identifier).find("mxGeometry")
    if node is None:
        raise RuntimeError(f"{template.name} {identifier} has no geometry")
    return tuple(float(node.get(name, "0")) for name in ("x", "y", "width", "height"))


def theme_stack_style(style: str) -> str:
    color_pattern = re.compile(r"(fontColor|fillColor|strokeColor|labelBackgroundColor)=(#[0-9A-Fa-f]{6})")

    def replacement(match: re.Match[str]) -> str:
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

    return color_pattern.sub(replacement, style)


def stack_template_style(identifier: str) -> str:
    style = required_template_cell(STACK_TEMPLATE, identifier).get("style", "")
    if not style:
        raise RuntimeError(f"{STACK_TEMPLATE.name} {identifier} has no style")
    return theme_stack_style(style)


STACK_INTERNAL_FLOW_STYLE = strip_style_properties(
    stack_template_style("request-flow"),
    ("rounded", "strokeColor", "strokeWidth", "endArrow", "endFill", "fontColor", "labelBackgroundColor", "fontStyle"),
) + ";rounded=0;strokeColor=light-dark(#596579,#AEB8C8);strokeWidth=1.25;endArrow=classic;endFill=1;"


TEMPLATE_ACTOR = required_template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlActor" in style, "actor")
TEMPLATE_PARTICIPANT = required_template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlLifeline" in style, "participant")
TEMPLATE_ACTIVATION = required_template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style,
    "activation",
)
TEMPLATE_FRAME = required_template_style(SEQUENCE_TEMPLATE, lambda _cell, style: "shape=umlFrame" in style, "fragment")
TEMPLATE_STEM = required_template_style(
    SEQUENCE_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;") and cell.find("mxGeometry") is not None,
    "actor stem",
)

CLASS_PACKAGE_STYLES = {
    "identity": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "IDENTITY & PROFILE" in template_label(cell)
        and "dashed=1" in style,
        "identity package",
    ),
    "jobs": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "JOBS & USER STATUS" in template_label(cell)
        and "dashed=1" in style,
        "jobs package",
    ),
    "geo": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "MAPPING, POI & OPEN DATA" in template_label(cell)
        and "dashed=1" in style,
        "mapping package",
    ),
    "persistence": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "AI & ADMINISTRATION" in template_label(cell)
        and "dashed=1" in style,
        "administration package",
    ),
}
CLASS_CARD_STYLES = {
    "identity": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>UserProfile</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "identity class",
    ),
    "jobs": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>JobListing</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "jobs class",
    ),
    "geo": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>POI</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "mapping class",
    ),
    "persistence": required_template_style(
        CLASS_TEMPLATE,
        lambda cell, style: cell.get("vertex") == "1" and "<b>AIProviderCredential</b>" in template_label(cell)
        and style.startswith("swimlane;"),
        "administration class",
    ),
}
CLASS_MEMBER_STYLE = required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1"
    and style.startswith("text;strokeColor=none;fillColor=none;align=left;"),
    "class member compartment",
)
CLASS_DIVIDER_STYLE = required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;strokeWidth=1;fillColor=none;"),
    "class compartment divider",
)
CLASS_RELATION_LABEL_STYLE = required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("edgeLabel;"),
    "relationship label",
)
CLASS_ASSOCIATION_STYLE = strip_style_properties(required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("edge") == "1" and "dashed=1" not in style
    and "startArrow=none" in style and "endArrow=none" in style,
    "association",
), ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"))
CLASS_DEPENDENCY_STYLE = strip_style_properties(required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("edge") == "1" and "dashed=1" in style and "endArrow=open" in style,
    "dependency",
), ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"))
CLASS_AGGREGATION_STYLE = strip_style_properties(required_template_style(
    CLASS_TEMPLATE,
    lambda cell, style: cell.get("edge") == "1" and "startArrow=diamond" in style
    and "startFill=0" in style,
    "aggregation",
), ("entryX", "entryY", "entryDx", "entryDy", "entryPerimeter", "exitX", "exitY", "exitDx", "exitDy", "exitPerimeter"))


def geometry(wrapper: ET.Element) -> tuple[float, float, float, float] | None:
    node = wrapper.find("mxCell/mxGeometry")
    if node is None:
        return None
    try:
        return tuple(float(node.get(name, "0")) for name in ("x", "y", "width", "height"))
    except ValueError:
        return None


def edge_points(wrapper: ET.Element) -> list[tuple[float, float]]:
    return [
        (float(point.get("x", "0")), float(point.get("y", "0")))
        for point in wrapper.findall("mxCell/mxGeometry/Array[@as='points']/mxPoint")
    ]


def center(rectangle: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, width, height = rectangle
    return x + width / 2, y + height / 2


def segment_crosses_rectangle(
    start: tuple[float, float],
    end: tuple[float, float],
    rectangle: tuple[float, float, float, float],
) -> bool:
    x, y, width, height = rectangle
    x2, y2 = x + width, y + height
    if abs(start[0] - end[0]) < 0.01:
        line_x = start[0]
        low, high = sorted((start[1], end[1]))
        return x + 0.01 < line_x < x2 - 0.01 and high > y + 0.01 and low < y2 - 0.01
    if abs(start[1] - end[1]) < 0.01:
        line_y = start[1]
        low, high = sorted((start[0], end[0]))
        return y + 0.01 < line_y < y2 - 0.01 and high > x + 0.01 and low < x2 - 0.01
    raise ValueError(f"non-orthogonal stack segment {start} -> {end}")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def canonical_class_layout(path: Path) -> tuple:
    """Return layout/component data while ignoring the active language projection.

    The asset builder intentionally rewrites ``value`` attributes to the active
    language.  The template and editable source must still agree on every cell,
    style, endpoint, stable key, and nested geometry value.
    """

    def canonical_element(element: ET.Element) -> tuple:
        attributes = tuple(
            sorted(
                (name, value)
                for name, value in element.attrib.items()
                if name not in {"value", "labelEn", "labelMs"}
            )
        )
        return (
            element.tag,
            attributes,
            tuple(canonical_element(child) for child in element),
        )

    root = ET.parse(path).getroot()
    cells = root.findall(".//mxCell")
    return tuple(
        sorted(
            ((cell.get("id", ""), canonical_element(cell)) for cell in cells),
            key=lambda item: item[0],
        )
    )


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))["diagrams"]
    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")

    if canonical_class_layout(CLASS_TEMPLATE) != canonical_class_layout(CLASS_DEFAULT_SOURCE):
        fail(errors, "default Core Domain layout drifted from Class Diagram Template")
    default_root = ET.parse(CLASS_DEFAULT_SOURCE).getroot()
    default_classes = {
        cell.get("petakerjaKey", ""): cell
        for cell in default_root.findall(".//mxCell")
        if cell.get("petakerjaKey", "").startswith("domain/")
        and cell.get("style", "").startswith("swimlane;")
    }
    if len(default_classes) != 15:
        fail(errors, f"default Core Domain expected 15 classes, got {len(default_classes)}")
    for key, expected_geometry in CLASS_DEFAULT_GEOMETRIES.items():
        cell = default_classes.get(key)
        node = cell.find("mxGeometry") if cell is not None else None
        actual_geometry = (
            tuple(float(node.get(name, "0")) for name in ("x", "y", "width", "height"))
            if node is not None else None
        )
        if actual_geometry != expected_geometry:
            fail(errors, f"default Core Domain {key} geometry drifted: {actual_geometry}")
    class_ids = {cell.get("id", "") for cell in default_classes.values()}
    for key, cell in default_classes.items():
        if f"fontSize={CLASS_TITLE_FONT_SIZE}" not in cell.get("style", ""):
            fail(errors, f"default Core Domain {key} title is not {CLASS_TITLE_FONT_SIZE}px")
        if f"font-size:{CLASS_STEREOTYPE_FONT_SIZE}px" not in cell.get("value", ""):
            fail(errors, f"default Core Domain {key} stereotype is not {CLASS_STEREOTYPE_FONT_SIZE}px")
    for member in default_root.findall(".//mxCell"):
        if (
            member.get("parent") in class_ids
            and member.get("vertex") == "1"
            and member.get("style", "").startswith("text;")
            and f"fontSize={CLASS_MEMBER_FONT_SIZE}" not in member.get("style", "")
        ):
            fail(errors, f"default Core Domain member {member.get('id')} is not {CLASS_MEMBER_FONT_SIZE}px")

    for order, (diagram_id, (source_name, page_id, svg_name, vanilla_id)) in enumerate(IDS.items(), 1):
        entry = manifest.get(diagram_id)
        if not entry:
            fail(errors, f"{diagram_id}: missing manifest entry")
            continue
        expected_xml = f"assets/editor/v2-georouting/{source_name}"
        expected_svg = f"assets/diagrams/v2-georouting/{svg_name}"
        if entry != {"xml": expected_xml, "svg": expected_svg, "pageId": page_id}:
            fail(errors, f"{diagram_id}: unexpected manifest mapping {entry}")
        source = ROOT / expected_xml
        if not source.exists():
            fail(errors, f"{diagram_id}: missing editable source")
            continue
        page = ET.parse(source).getroot().find("diagram")
        if page is None or page.get("id") != page_id:
            fail(errors, f"{diagram_id}: expected page id {page_id}")
            continue
        wrappers = {item.get("id", ""): item for item in page.findall(".//object")}
        stable_keys: set[str] = set()
        for wrapper_id, wrapper in wrappers.items():
            key = wrapper.get("petakerjaKey", "")
            if not key or key in stable_keys:
                fail(errors, f"{diagram_id}:{wrapper_id}: missing or duplicate stable key")
            stable_keys.add(key)
            if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
                fail(errors, f"{diagram_id}:{wrapper_id}: missing bilingual label")
            cell = wrapper.find("mxCell")
            if cell is not None and cell.get("edge") == "1":
                is_fragment_divider = wrapper.get("fragmentDivider") == "1"
                if not is_fragment_divider and (cell.get("source") not in wrappers or cell.get("target") not in wrappers):
                    fail(errors, f"{diagram_id}:{wrapper_id}: disconnected edge endpoint")
                if diagram_id in SEQUENCES and wrapper.get("message") == "1":
                    for attribute in ("simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs"):
                        if not wrapper.get(attribute):
                            fail(errors, f"{diagram_id}:{wrapper_id}: missing {attribute}")

        if diagram_id == "v2-geo-usecase":
            for actor_id in ("uc-user", "uc-seeker", "uc-valhalla", "uc-nominatim"):
                actor_geometry = geometry(wrappers[actor_id])
                if actor_geometry is None or actor_geometry[2:] != ACTOR_SIZE:
                    fail(errors, f"{diagram_id}:{actor_id}: expected template actor size 70x140, got {actor_geometry}")
            for wrapper_id, wrapper in wrappers.items():
                if wrapper.get("petakerjaKey", "").startswith("usecase/"):
                    usecase_geometry = geometry(wrapper)
                    if usecase_geometry is None or usecase_geometry[3] != USECASE_HEIGHT:
                        fail(errors, f"{diagram_id}:{wrapper_id}: expected 62px template use-case height")

        if diagram_id in CLASS_PAGE_SIZES:
            model = page.find("mxGraphModel")
            expected_page_size = CLASS_PAGE_SIZES[diagram_id]
            actual_page_size = (
                float(model.get("pageWidth", "0")) if model is not None else 0.0,
                float(model.get("pageHeight", "0")) if model is not None else 0.0,
            )
            if actual_page_size != expected_page_size:
                fail(errors, f"{diagram_id}: expected class canvas {expected_page_size}, got {actual_page_size}")

            uml_classes = [wrapper for wrapper in wrappers.values() if wrapper.get("umlClass") == "1"]
            uml_packages = [wrapper for wrapper in wrappers.values() if wrapper.get("umlPackage") == "1"]
            relationships = [wrapper for wrapper in wrappers.values() if wrapper.get("umlRelationship")]
            expected_class_keys = DOMAIN_CLASS_KEYS if diagram_id == "v2-geo-domain" else IMPLEMENTATION_CLASS_KEYS
            actual_class_keys = {wrapper.get("petakerjaKey", "") for wrapper in uml_classes}
            if len(uml_classes) != CLASS_COUNTS[diagram_id] or actual_class_keys != expected_class_keys:
                fail(errors, f"{diagram_id}: unexpected UML class set {sorted(actual_class_keys)}")
            if len(uml_packages) != 4:
                fail(errors, f"{diagram_id}: expected four template-style UML packages")

            for package in uml_packages:
                tone = package.get("tone", "")
                if tone not in CLASS_PACKAGE_STYLES or cell_style(package) != CLASS_PACKAGE_STYLES.get(tone):
                    fail(errors, f"{diagram_id}:{package.get('id')}: package style drifted from class template")

            for wrapper in uml_classes:
                wrapper_id = wrapper.get("id", "")
                stable_key = wrapper.get("petakerjaKey", "")
                tone = wrapper.get("tone", "")
                class_geometry = geometry(wrapper)
                if tone not in CLASS_CARD_STYLES or cell_style(wrapper) != CLASS_CARD_STYLES.get(tone):
                    fail(errors, f"{diagram_id}:{wrapper_id}: class style drifted from class template")
                if "startSize=46" not in cell_style(wrapper):
                    fail(errors, f"{diagram_id}:{wrapper_id}: class header is not exactly 46px")
                if f"fontSize={CLASS_TITLE_FONT_SIZE}" not in cell_style(wrapper):
                    fail(errors, f"{diagram_id}:{wrapper_id}: class title is not {CLASS_TITLE_FONT_SIZE}px")
                if f"font-size:{CLASS_STEREOTYPE_FONT_SIZE}px" not in wrapper.get("labelEn", ""):
                    fail(errors, f"{diagram_id}:{wrapper_id}: stereotype is not {CLASS_STEREOTYPE_FONT_SIZE}px")
                if class_geometry is None or class_geometry[3] % 10 != 0:
                    fail(errors, f"{diagram_id}:{wrapper_id}: class height is not on the 10px template grid")
                if wrapper.get("labelEn") != wrapper.get("labelMs"):
                    fail(errors, f"{diagram_id}:{wrapper_id}: code symbol or stereotype changed between languages")

                attributes = wrappers.get(f"{wrapper_id}-attributes")
                if attributes is None:
                    fail(errors, f"{diagram_id}:{wrapper_id}: missing typed attribute compartment")
                    continue
                attr_geometry = geometry(attributes)
                attr_cell = attributes.find("mxCell")
                if (
                    attributes.get("petakerjaKey") != f"{stable_key}/attributes"
                    or attributes.get("umlCompartment") != "attributes"
                    or attr_cell is None or attr_cell.get("parent") != wrapper_id
                    or cell_style(attributes) != CLASS_MEMBER_STYLE
                    or f"fontSize={CLASS_MEMBER_FONT_SIZE}" not in cell_style(attributes)
                    or attr_geometry is None or attr_geometry[1] != 46.0
                ):
                    fail(errors, f"{diagram_id}:{wrapper_id}: invalid deterministic attribute compartment")
                if (
                    attributes.get("labelEn") != attributes.get("labelMs")
                    or (attributes.get("labelEn", "") and ":" not in attributes.get("labelEn", ""))
                ):
                    fail(errors, f"{diagram_id}:{wrapper_id}: attributes are not typed or language-stable")

                operations = wrappers.get(f"{wrapper_id}-operations")
                divider = wrappers.get(f"{wrapper_id}-divider")
                if operations is not None:
                    operation_cell = operations.find("mxCell")
                    divider_cell = divider.find("mxCell") if divider is not None else None
                    divider_geometry = geometry(divider) if divider is not None else None
                    if (
                        operations.get("petakerjaKey") != f"{stable_key}/operations"
                        or operations.get("umlCompartment") != "operations"
                        or operation_cell is None or operation_cell.get("parent") != wrapper_id
                        or cell_style(operations) != CLASS_MEMBER_STYLE
                        or f"fontSize={CLASS_MEMBER_FONT_SIZE}" not in cell_style(operations)
                        or operations.get("labelEn") != operations.get("labelMs")
                        or "+ " not in operations.get("labelEn", "")
                    ):
                        fail(errors, f"{diagram_id}:{wrapper_id}: invalid public-operation compartment")
                    if (
                        divider is None or divider.get("petakerjaKey") != f"{stable_key}/divider"
                        or divider.get("umlCompartment") != "divider"
                        or divider_cell is None or divider_cell.get("parent") != wrapper_id
                        or cell_style(divider) != CLASS_DIVIDER_STYLE
                        or divider_geometry is None or divider_geometry[3] != 8.0
                    ):
                        fail(errors, f"{diagram_id}:{wrapper_id}: invalid 8px template divider")
                elif divider is not None:
                    fail(errors, f"{diagram_id}:{wrapper_id}: divider exists without operations")

                if diagram_id == "v2-geo-domain" and wrapper.get("stereotype", "").startswith("entity:"):
                    if operations is not None:
                        fail(errors, f"{diagram_id}:{wrapper_id}: passive database entity has fabricated operations")

            relation_styles = {
                "association": CLASS_ASSOCIATION_STYLE,
                "dependency": CLASS_DEPENDENCY_STYLE,
                "aggregation": CLASS_AGGREGATION_STYLE,
            }
            relation_kinds = {wrapper.get("umlRelationship", "") for wrapper in relationships}
            if relation_kinds != set(relation_styles):
                fail(errors, f"{diagram_id}: expected association, dependency and aggregation relationships")
            class_ids = {wrapper.get("id", "") for wrapper in uml_classes}
            for relation in relationships:
                relation_id = relation.get("id", "")
                kind = relation.get("umlRelationship", "")
                cell = relation.find("mxCell")
                if (
                    cell is None or cell.get("source") not in class_ids or cell.get("target") not in class_ids
                    or cell_style(relation) != relation_styles.get(kind)
                ):
                    fail(errors, f"{diagram_id}:{relation_id}: invalid template-derived {kind} relationship")
                labels = [
                    child for child in wrappers.values()
                    if child.find("mxCell") is not None and child.find("mxCell").get("parent") == relation_id
                ]
                for label in labels:
                    role = label.get("umlRelationLabel", "")
                    if cell_style(label) != CLASS_RELATION_LABEL_STYLE:
                        fail(errors, f"{diagram_id}:{label.get('id')}: relationship label style drifted")
                    if role in {"source-multiplicity", "target-multiplicity"}:
                        if label.get("labelEn") not in {"1", "0..1", "0..*", "1..*"}:
                            fail(errors, f"{diagram_id}:{label.get('id')}: invalid UML multiplicity")
                    elif role == "role" and (not label.get("labelEn") or not label.get("labelMs")):
                        fail(errors, f"{diagram_id}:{label.get('id')}: missing bilingual relationship description")

            if diagram_id == "v2-geo-implementation":
                implementation_text = ET.tostring(page, encoding="unicode")
                for fact in ("Nominatim", "disabled", "non-navigable"):
                    if fact not in implementation_text:
                        fail(errors, f"{diagram_id}: missing implementation constraint {fact}")

        if diagram_id in STACK_DIAGRAMS:
            model = page.find("mxGraphModel")
            actual_page_size = (
                float(model.get("pageWidth", "0")) if model is not None else 0.0,
                float(model.get("pageHeight", "0")) if model is not None else 0.0,
            )
            if actual_page_size != STACK_PAGE_SIZE:
                fail(errors, f"{diagram_id}: expected Stack Template canvas {STACK_PAGE_SIZE}, got {actual_page_size}")

            roles: dict[str, list[ET.Element]] = {}
            ordered_wrappers = page.findall(".//object")
            for wrapper in ordered_wrappers:
                roles.setdefault(wrapper.get("stackRole", ""), []).append(wrapper)
            expected_role_counts = {
                "title": 1, "subtitle": 1, "depth": 5, "layer": 5, "card": 14,
                "callout": 7, "flow": 12, "anchor": 4, "rail": 2,
                "rail-label": 2, "footer": 1,
            }
            actual_role_counts = {role: len(roles.get(role, [])) for role in expected_role_counts}
            if actual_role_counts != expected_role_counts:
                fail(errors, f"{diagram_id}: unexpected stack-role counts {actual_role_counts}")

            depth_slots = {wrapper.get("templateSlot", "") for wrapper in roles.get("depth", [])}
            layer_slots = {wrapper.get("templateSlot", "") for wrapper in roles.get("layer", [])}
            card_slots = {wrapper.get("templateSlot", "") for wrapper in roles.get("card", [])}
            callout_slots = {wrapper.get("templateSlot", "") for wrapper in roles.get("callout", [])}
            if depth_slots != set(STACK_DEPTH_SLOTS) or layer_slots != set(STACK_LAYER_SLOTS):
                fail(errors, f"{diagram_id}: stack layer/depth slots drifted from template")
            if card_slots != STACK_CARD_SLOTS:
                fail(errors, f"{diagram_id}: fixed stack card slots drifted: {sorted(card_slots)}")
            if callout_slots != STACK_CALLOUT_SLOTS:
                fail(errors, f"{diagram_id}: callout column slots drifted: {sorted(callout_slots)}")

            exact_template_roles = {
                "title", "subtitle", "depth", "layer", "card", "callout",
                "anchor", "rail", "rail-label", "footer",
            }
            for role in exact_template_roles:
                for wrapper in roles.get(role, []):
                    template_slot = wrapper.get("templateSlot", "")
                    expected_style = stack_template_style(template_slot)
                    if cell_style(wrapper) != expected_style:
                        fail(errors, f"{diagram_id}:{wrapper.get('id')}: {role} style drifted from Stack Template")
                    if "light-dark(" not in expected_style and role != "anchor":
                        fail(errors, f"{diagram_id}:{wrapper.get('id')}: missing theme-aware stack color")
                    if role not in {"rail"}:
                        expected_geometry = template_geometry(STACK_TEMPLATE, template_slot)
                        if geometry(wrapper) != expected_geometry:
                            fail(errors, f"{diagram_id}:{wrapper.get('id')}: geometry drifted from {template_slot}")

            depth_by_layer = {wrapper.get("stackLayer", ""): wrapper for wrapper in roles.get("depth", [])}
            foreground_by_layer = {wrapper.get("stackLayer", ""): wrapper for wrapper in roles.get("layer", [])}
            for layer_key, foreground in foreground_by_layer.items():
                depth = depth_by_layer.get(layer_key)
                foreground_geometry = geometry(foreground)
                depth_geometry = geometry(depth) if depth is not None else None
                if (
                    foreground_geometry is None or depth_geometry is None
                    or depth_geometry[0] - foreground_geometry[0] != 12.0
                    or depth_geometry[1] - foreground_geometry[1] != 12.0
                    or depth_geometry[2:] != foreground_geometry[2:]
                ):
                    fail(errors, f"{diagram_id}:{layer_key}: depth copy is not the required 12px offset")
            wrapper_positions = {wrapper.get("id", ""): index for index, wrapper in enumerate(ordered_wrappers)}
            if roles.get("depth") and roles.get("layer") and max(wrapper_positions[item.get("id", "")] for item in roles["depth"]) > min(wrapper_positions[item.get("id", "")] for item in roles["layer"]):
                fail(errors, f"{diagram_id}: depth copies must render before all foreground layers")
            if roles.get("flow") and roles.get("callout") and max(wrapper_positions[item.get("id", "")] for item in roles["flow"]) > min(wrapper_positions[item.get("id", "")] for item in roles["callout"]):
                fail(errors, f"{diagram_id}: callouts must render above connector paths")

            rail_directions = {wrapper.get("stackDirection", "") for wrapper in roles.get("anchor", [])}
            if rail_directions != {"request", "response"}:
                fail(errors, f"{diagram_id}: request/response anchors are incomplete")
            for rail in roles.get("rail", []):
                cell = rail.find("mxCell")
                source = wrappers.get(cell.get("source", "")) if cell is not None else None
                target = wrappers.get(cell.get("target", "")) if cell is not None else None
                if source is None or target is None or source.get("stackRole") != "anchor" or target.get("stackRole") != "anchor":
                    fail(errors, f"{diagram_id}:{rail.get('id')}: rail is not connected to template anchors")

            cards = {wrapper.get("id", ""): wrapper for wrapper in roles.get("card", [])}
            card_rectangles = {identifier: geometry(wrapper) for identifier, wrapper in cards.items()}
            for flow in roles.get("flow", []):
                flow_id = flow.get("id", "")
                cell = flow.find("mxCell")
                source_id = cell.get("source", "") if cell is not None else ""
                target_id = cell.get("target", "") if cell is not None else ""
                points = edge_points(flow)
                if not points:
                    fail(errors, f"{diagram_id}:{flow_id}: missing explicit orthogonal waypoints")
                    continue
                if flow.get("templateSlot") == "gateway-fallback-branch":
                    if cell_style(flow) != stack_template_style("gateway-fallback-branch"):
                        fail(errors, f"{diagram_id}:{flow_id}: fallback edge drifted from template")
                elif cell_style(flow) != STACK_INTERNAL_FLOW_STYLE:
                    fail(errors, f"{diagram_id}:{flow_id}: internal flow style drifted")
                source_geometry = geometry(wrappers.get(source_id)) if wrappers.get(source_id) is not None else None
                target_geometry = geometry(wrappers.get(target_id)) if wrappers.get(target_id) is not None else None
                if source_geometry is None or target_geometry is None:
                    continue
                route = [center(source_geometry), *points, center(target_geometry)]
                for segment_start, segment_end in zip(route, route[1:]):
                    try:
                        for card_id, rectangle in card_rectangles.items():
                            if card_id in {source_id, target_id} or rectangle is None:
                                continue
                            if segment_crosses_rectangle(segment_start, segment_end, rectangle):
                                fail(errors, f"{diagram_id}:{flow_id}: segment crosses {card_id} text region")
                    except ValueError as error:
                        fail(errors, f"{diagram_id}:{flow_id}: {error}")

            stack_text = "\n".join(
                wrapper.get("labelEn", "") for wrapper in wrappers.values()
            )
            if diagram_id == "v2-geo-architecture":
                for fact in ("matrix", "isochrone", "boundary", "Workplace", "Geo Studio", "Valhalla · enabled", "Nominatim · disabled"):
                    if fact not in stack_text:
                        fail(errors, f"{diagram_id}: broad architecture is missing {fact}")
                stable_symbols = {
                    "arch-nav": "GeoNavigationManager", "arch-api": "/api/geo/*",
                    "arch-valhalla": "Valhalla", "arch-nominatim": "Nominatim",
                }
            else:
                for fact in ("Origin A", "Destination B", "REQUEST", "RESPONSE", "Haversine", "No ETA", "No navigable-route claim", "traffic-independent"):
                    if fact not in stack_text:
                        fail(errors, f"{diagram_id}: focused routing stack is missing {fact}")
                for out_of_scope in ("isochrone", "matrix"):
                    if out_of_scope in stack_text.lower():
                        fail(errors, f"{diagram_id}: focused routing stack unexpectedly includes {out_of_scope}")
                stable_symbols = {
                    "stack-nav": "GeoNavigationManager", "stack-renderer": "GeoRouteRenderer",
                    "stack-client": "src/services/geo.ts", "stack-api": "/api/geo/route",
                    "stack-valhalla": "Valhalla", "stack-nominatim": "Nominatim",
                }
            for wrapper_id, symbol in stable_symbols.items():
                wrapper = wrappers.get(wrapper_id)
                if wrapper is None or symbol not in wrapper.get("labelEn", "") or symbol not in wrapper.get("labelMs", ""):
                    fail(errors, f"{diagram_id}:{wrapper_id}: code symbol {symbol} changed between languages")

        if diagram_id in SEQUENCES:
            participants = [
                wrapper for wrapper_id, wrapper in wrappers.items()
                if re.fullmatch(r"(?:route|travel|jobroute)-participant-[a-z]+", wrapper_id)
            ]
            lifelines = [wrapper for wrapper_id, wrapper in wrappers.items() if "-lifeline-" in wrapper_id]
            if len(participants) != 9 or len(lifelines) != 9:
                fail(errors, f"{diagram_id}: expected nine participant lanes and nine lifelines")
            actors = [wrapper for wrapper in participants if "shape=umlActor" in cell_style(wrapper)]
            systems = [wrapper for wrapper in participants if "shape=umlLifeline" in cell_style(wrapper)]
            if len(actors) != 1 or len(systems) != 8:
                fail(errors, f"{diagram_id}: expected one human actor and eight system participants")
            for wrapper in actors:
                participant_geometry = geometry(wrapper)
                if participant_geometry is None or participant_geometry[2:] != SEQUENCE_ACTOR_SIZE:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: expected 20x40 template actor")
                if cell_style(wrapper) != TEMPLATE_ACTOR:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: actor style drifted from template")
            for wrapper in systems:
                participant_geometry = geometry(wrapper)
                if participant_geometry is None or participant_geometry[2:] != PARTICIPANT_SIZE:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: expected 100x60 template participant")
                if cell_style(wrapper) != TEMPLATE_PARTICIPANT:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: participant style drifted from template")
            for wrapper in lifelines:
                lifeline_geometry = geometry(wrapper)
                if lifeline_geometry is None or lifeline_geometry[2] != LIFELINE_WIDTH:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: expected separate 10px lifeline")
                if cell_style(wrapper) != TEMPLATE_ACTIVATION:
                    fail(errors, f"{diagram_id}:{wrapper.get('id')}: activation style drifted from template")
            actor = actors[0] if actors else None
            if actor is not None:
                actor_prefix = actor.get("id", "")
                actor_label = wrappers.get(f"{actor_prefix}-label")
                actor_stem = wrappers.get(f"{actor_prefix}-stem")
                if actor_label is None:
                    fail(errors, f"{diagram_id}: missing separate actor label")
                if actor_stem is None or cell_style(actor_stem) != TEMPLATE_STEM:
                    fail(errors, f"{diagram_id}: missing template actor stem")
            lane_centers: list[float] = []
            for wrapper in participants:
                participant_geometry = geometry(wrapper)
                if participant_geometry is not None:
                    lane_centers.append(participant_geometry[0] + participant_geometry[2] / 2)
            if sorted(lane_centers) != [90.0 + 200.0 * index for index in range(9)]:
                fail(errors, f"{diagram_id}: participant lanes do not use the 200px template grid")

            fragments = {
                wrapper.get("petakerjaKey", ""): wrapper
                for wrapper in wrappers.values()
                if "/fragment-" in wrapper.get("petakerjaKey", "")
            }
            if set(fragments) != set(SEQUENCE_FRAGMENTS[diagram_id]):
                fail(errors, f"{diagram_id}: unexpected fragment set {sorted(fragments)}")
            for key, kind in SEQUENCE_FRAGMENTS[diagram_id].items():
                wrapper = fragments.get(key)
                if wrapper is None:
                    continue
                if wrapper.get("label") != kind or wrapper.get("labelMs") != kind:
                    fail(errors, f"{diagram_id}:{key}: expected bilingual {kind} fragment label")
                if cell_style(wrapper) != TEMPLATE_FRAME:
                    fail(errors, f"{diagram_id}:{key}: fragment style drifted from template")

            message_rows: list[tuple[int, float]] = []
            for wrapper_id, wrapper in wrappers.items():
                if wrapper.get("message") != "1":
                    continue
                match_id = re.search(r"-(\d+)$", wrapper_id)
                cell = wrapper.find("mxCell")
                match_y = re.search(r"exitY=([0-9.]+)", cell.get("style", "") if cell is not None else "")
                if match_id and match_y:
                    source = wrappers.get(cell.get("source", "")) if cell is not None else None
                    source_geometry = geometry(source) if source is not None else None
                    if source_geometry is not None:
                        message_y = source_geometry[1] + float(match_y.group(1)) * source_geometry[3]
                        message_rows.append((int(match_id.group(1)), message_y))
                style = cell.get("style", "") if cell is not None else ""
                if "labelBackgroundColor=none" not in style:
                    fail(errors, f"{diagram_id}:{wrapper_id}: message label background differs from template")
                if "dashed=1" in style:
                    if "endArrow=open" not in style or "endFill=0" not in style:
                        fail(errors, f"{diagram_id}:{wrapper_id}: invalid template return arrow")
                elif "endArrow=classic" not in style or "endFill=1" not in style:
                    fail(errors, f"{diagram_id}:{wrapper_id}: invalid template call arrow")
            ordered_rows = [row for _, row in sorted(message_rows)]
            if len(ordered_rows) != len(set(ordered_rows)) or ordered_rows != sorted(ordered_rows):
                fail(errors, f"{diagram_id}: sequence messages do not occupy unique ascending rows")
            expected_rows = SEQUENCE_ROWS[diagram_id]
            if len(ordered_rows) != len(expected_rows) or any(abs(actual - expected) > 0.2 for actual, expected in zip(ordered_rows, expected_rows)):
                fail(errors, f"{diagram_id}: sequence messages drifted from the approved 50px row grid")

        expected_group = COLLECTION_GROUPS[diagram_id]
        metadata_pattern = rf"id: '{re.escape(diagram_id)}'.*?collectionId: 'v2-georouting', collectionGroupId: '{re.escape(expected_group)}', collectionOrder: {order}, versionTag: 'V2'"
        if not re.search(metadata_pattern, architecture, re.DOTALL):
            fail(errors, f"{diagram_id}: missing ordered collection metadata")
        if vanilla_id and f"basedOnDiagramId: '{vanilla_id}'" not in re.search(rf"id: '{re.escape(diagram_id)}'.*?columns:", architecture, re.DOTALL).group(0):
            fail(errors, f"{diagram_id}: missing vanilla comparison mapping")
        for registration in (editor, translations):
            if diagram_id not in registration:
                fail(errors, f"{diagram_id}: missing editor or translation registration")

    supabase_text = (ROOT / "assets" / "editor" / "v2-georouting" / "supabase.drawio").read_text(encoding="utf-8")
    table_names = set(re.findall(r"[a-z][a-z0-9_]+", supabase_text))
    if not GEO_TABLES.issubset(table_names):
        fail(errors, f"Supabase snapshot is missing geo tables: {sorted(GEO_TABLES - table_names)}")
    if "87 public tables" not in supabase_text or "119 foreign keys" not in supabase_text:
        fail(errors, "Supabase snapshot is missing the dated 87-table/119-FK totals")
    for runtime_fact in ("Valhalla enabled and available", "cache available", "Nominatim disabled"):
        if runtime_fact not in "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "assets" / "editor" / "v2-georouting").glob("*.drawio")):
            fail(errors, f"collection is missing runtime fact: {runtime_fact}")
    actual_group_counts = {
        group_id: list(COLLECTION_GROUPS.values()).count(group_id)
        for group_id in set(COLLECTION_GROUPS.values())
    }
    if actual_group_counts != GROUP_COUNTS:
        fail(errors, f"unexpected V2 collection subgroup counts: {actual_group_counts}")
    for label in (
        "Use Case Diagrams", "Flowcharts", "Sequence Diagrams", "Class Diagrams",
        "Architecture & Modules", "Data Diagrams",
    ):
        if label not in translations:
            fail(errors, f"translations are missing collection subgroup label: {label}")
    for label in ("Rajah Kes Guna", "Carta Alir", "Rajah Jujukan", "Rajah Kelas", "Seni Bina & Modul", "Rajah Data"):
        if label not in app:
            fail(errors, f"app.js is missing Malay collection subgroup label: {label}")
    for marker in (
        "petakerja-explorer-diagram-collections", "petakerja-explorer-diagram-collection-groups",
        "data-diagram-collection", "data-diagram-collection-group", "data-open-comparison",
    ):
        if marker not in app:
            fail(errors, f"app.js is missing collection marker {marker}")
    if "diagram.collectionId === 'v2-georouting'" not in app or "{ tables: 87, foreignKeys: 119" not in app:
        fail(errors, "V2 collection details do not project the dated schema totals")

    if errors:
        print("V2 Georouting collection checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("V2 Georouting checks passed for 13 editable bilingual diagrams and their Explorer collection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
