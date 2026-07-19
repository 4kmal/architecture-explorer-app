#!/usr/bin/env python3
"""Regression checks for the isolated V2 Georouting Explorer collection."""

from __future__ import annotations

import json
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


def cell_style(wrapper: ET.Element) -> str:
    cell = wrapper.find("mxCell")
    return cell.get("style", "") if cell is not None else ""


def required_template_style(predicate, description: str) -> str:
    for cell in ET.parse(SEQUENCE_TEMPLATE).getroot().findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError(f"Sequence template is missing {description}")


TEMPLATE_ACTOR = required_template_style(lambda _cell, style: "shape=umlActor" in style, "actor")
TEMPLATE_PARTICIPANT = required_template_style(lambda _cell, style: "shape=umlLifeline" in style, "participant")
TEMPLATE_ACTIVATION = required_template_style(
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style,
    "activation",
)
TEMPLATE_FRAME = required_template_style(lambda _cell, style: "shape=umlFrame" in style, "fragment")
TEMPLATE_STEM = required_template_style(
    lambda cell, style: cell.get("vertex") == "1" and style.startswith("line;") and cell.find("mxGeometry") is not None,
    "actor stem",
)


def geometry(wrapper: ET.Element) -> tuple[float, float, float, float] | None:
    node = wrapper.find("mxCell/mxGeometry")
    if node is None:
        return None
    try:
        return tuple(float(node.get(name, "0")) for name in ("x", "y", "width", "height"))
    except ValueError:
        return None


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))["diagrams"]
    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")

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
