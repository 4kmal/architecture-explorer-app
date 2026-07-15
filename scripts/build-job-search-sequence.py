#!/usr/bin/env python3
"""Build the focused PetaKerja Daily Index job-search sequence diagram.

The supplied Sequence Diagram Template.drawio is read only for its UML actor,
lifeline, activation, frame and message styles. The generated source is also
copied into the Explorer so View and Edit modes share identical geometry.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import apply_label_modes_to_file


DIAGRAMS = Path(r"C:\Users\iamal\Desktop\Semester 8\TTTM4172 Usulan Projek\Akmal\Diagrams")
TEMPLATE = DIAGRAMS / "Sequence Diagram Template.drawio"
OUTPUT = DIAGRAMS / "Sequence Diagram PetaKerja - Search Jobs.drawio"
EXPLORER = Path(__file__).resolve().parents[1]
EDITOR_OUTPUT = EXPLORER / "assets" / "editor" / "sequence-job-search.drawio"

PAGE_ID = "petakerja_job_search_sequence"
KEY_PREFIX = "sequence"
ROOT_ID = "job-search-sequence-root"
LAYER_ID = "job-search-sequence-layer"
ACTIVATION_Y = 130.0
ACTIVATION_HEIGHT = 925.0


def template_style(predicate) -> str:
    root = ET.parse(TEMPLATE).getroot()
    for cell in root.findall(".//mxCell"):
        style = cell.get("style", "")
        if predicate(cell, style):
            return style
    raise RuntimeError("Required style was not found in the sequence template")


ACTOR_STYLE = template_style(lambda _cell, style: "shape=umlActor" in style)
LIFELINE_STYLE = template_style(lambda _cell, style: "shape=umlLifeline" in style)
ACTIVATION_STYLE = template_style(
    lambda cell, style: cell.get("vertex") == "1" and "targetShapes=umlLifeline" in style
)
FRAME_STYLE = template_style(lambda _cell, style: "shape=umlFrame" in style)
TEMPLATE_CALL_STYLE = template_style(
    lambda cell, style: cell.get("edge") == "1" and "startArrow=classic" in style
)
TEMPLATE_RETURN_STYLE = template_style(
    lambda cell, style: cell.get("edge") == "1" and "endArrow=open" in style and "dashed=1" in style
)


def normalise_call_style(style: str) -> str:
    for property_name in (
        "startArrow", "startFill", "endArrow", "endFill",
        "entryX", "entryY", "entryDx", "entryDy",
        "exitX", "exitY", "exitDx", "exitDy",
    ):
        style = re.sub(rf"(?:^|;){property_name}=[^;]*;?", ";", style)
    return style.strip(";") + ";endArrow=classic;endFill=1;strokeWidth=1;fontSize=10;"


def normalise_return_style(style: str) -> str:
    for property_name in (
        "entryX", "entryY", "entryDx", "entryDy",
        "exitX", "exitY", "exitDx", "exitDy",
    ):
        style = re.sub(rf"(?:^|;){property_name}=[^;]*;?", ";", style)
    return style.strip(";") + ";strokeWidth=1;fontSize=10;"


CALL_STYLE = normalise_call_style(TEMPLATE_CALL_STYLE)
RETURN_STYLE = normalise_return_style(TEMPLATE_RETURN_STYLE)
TEXT_STYLE = "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;"


def add_geometry(cell: ET.Element, *, x: float | None = None, y: float | None = None,
                 width: float | None = None, height: float | None = None,
                 relative: bool = False) -> ET.Element:
    attrs = {"as": "geometry"}
    if relative:
        attrs["relative"] = "1"
    geometry = ET.SubElement(cell, "mxGeometry", attrs)
    for name, value in (("x", x), ("y", y), ("width", width), ("height", height)):
        if value is not None:
            geometry.set(name, f"{value:g}")
    return geometry


def add_object(root: ET.Element, *, key: str | None, cell_id: str, label: str, style: str,
               vertex: bool = False, edge: bool = False, source: str | None = None,
               target: str | None = None, geometry: dict | None = None) -> ET.Element:
    wrapper_attrs = {"label": label, "id": cell_id}
    if key:
        wrapper_attrs["petakerjaKey"] = key
    wrapper = ET.SubElement(root, "object", wrapper_attrs)
    attrs = {"parent": LAYER_ID, "style": style}
    if vertex:
        attrs["vertex"] = "1"
    if edge:
        attrs["edge"] = "1"
    if source:
        attrs["source"] = source
    if target:
        attrs["target"] = target
    cell = ET.SubElement(wrapper, "mxCell", attrs)
    add_geometry(cell, **(geometry or {}))
    return cell


def ratio(y: float) -> float:
    return max(0.0, min(1.0, (y - ACTIVATION_Y) / ACTIVATION_HEIGHT))


def message_style(base: str, y: float, *, source: str, target: str,
                  self_message: bool = False) -> str:
    if self_message:
        return (
            base
            + "edgeStyle=orthogonalEdgeStyle;loopSize=42;align=left;spacingLeft=4;"
              f"exitX=1;exitY={ratio(y - 6):.6f};exitPerimeter=0;"
              f"entryX=1;entryY={ratio(y + 8):.6f};entryPerimeter=0;"
        )
    left_to_right = PARTICIPANT_CENTRES[target] > PARTICIPANT_CENTRES[source]
    exit_x, entry_x = (1, 0) if left_to_right else (0, 1)
    return base + (
        f"exitX={exit_x};exitY={ratio(y):.6f};exitPerimeter=0;"
        f"entryX={entry_x};entryY={ratio(y):.6f};entryPerimeter=0;"
        "labelBackgroundColor=none;"
    )


def add_message(root: ET.Element, *, index: int, label: str, source: str,
                target: str, y: float, returned: bool = False,
                self_message: bool = False) -> None:
    key = f"{KEY_PREFIX}/message-{index:02d}"
    cell_id = f"job-search-message-{index:02d}"
    base = RETURN_STYLE if returned else CALL_STYLE
    cell = add_object(
        root,
        key=key,
        cell_id=cell_id,
        label=label,
        style=message_style(base, y, source=source, target=target, self_message=self_message),
        edge=True,
        source=source,
        target=target,
        geometry={"relative": True},
    )
    if self_message:
        geometry = cell.find("mxGeometry")
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        centre_x = PARTICIPANT_CENTRES[source]
        ET.SubElement(points, "mxPoint", {"x": f"{centre_x + 72:g}", "y": f"{y - 6:g}"})
        ET.SubElement(points, "mxPoint", {"x": f"{centre_x + 72:g}", "y": f"{y + 8:g}"})


def add_divider(root: ET.Element, *, key: str, y: float, x1: float, x2: float) -> None:
    wrapper = ET.SubElement(root, "object", {"label": "", "petakerjaKey": key, "id": key.replace("/", "-")})
    cell = ET.SubElement(wrapper, "mxCell", {
        "edge": "1", "parent": LAYER_ID,
        "style": "endArrow=none;dashed=1;html=1;rounded=0;strokeWidth=1;",
    })
    geometry = add_geometry(cell, relative=True)
    ET.SubElement(geometry, "mxPoint", {"x": f"{x1:g}", "y": f"{y:g}", "as": "sourcePoint"})
    ET.SubElement(geometry, "mxPoint", {"x": f"{x2:g}", "y": f"{y:g}", "as": "targetPoint"})


def add_operand(root: ET.Element, *, key: str, label: str, x: float, y: float,
                width: float = 250) -> None:
    add_object(
        root,
        key=key,
        cell_id=key.replace("/", "-"),
        label=label,
        style=TEXT_STYLE + "align=left;fontStyle=2;fontSize=10;",
        vertex=True,
        geometry={"x": x, "y": y, "width": width, "height": 20},
    )


PARTICIPANTS = [
    ("user", "User", 90, "pengguna"),
    ("ui", "PetaKerja Job Finder UI", 280, "job-finder-ui"),
    ("manager", "<font style=\"font-size: 9px;\">JobFinderManager</font>", 480, "job-manager"),
    ("client", "supa-api.ts", 680, "jobs-api"),
    ("route", "Supa Jobs Route<div><font style=\"font-size: 8px;\">GET /api/jobs/supa</font></div>", 880, "supa-jobs-route"),
    ("database", "Supabase / PostgreSQL<div><font style=\"font-size: 8px;\">public.scraped_jobs</font></div>", 1080, "supabase-db"),
    ("relevance", "<font style=\"font-size: 9px;\">jobSearchRelevance</font>", 1280, "job-search-relevance"),
    ("results", "Job Results / MapLibre", 1480, "job-results-ui"),
]
PARTICIPANT_CENTRES = {f"job-search-activation-{slug}": centre for slug, _label, centre, _node in PARTICIPANTS}


MESSAGES = [
    (1, "1. Enter query, location and filters", "user", "ui", 150, False, False),
    (2, "2. Select Search", "user", "ui", 175, False, False),
    (3, "3. executeSearch()", "ui", "manager", 200, False, False),
    (4, "4. Show loading; clear results", "manager", "ui", 225, False, False),
    (5, "5. executeSupaSearch(query, location)", "manager", "manager", 250, False, True),
    (6, "6. searchSupaJobs(params)", "manager", "client", 275, False, False),
    (7, "7. GET /api/jobs/supa?query + filters", "client", "route", 300, False, False),
    (8, "8. readParams(); cacheKey()", "route", "route", 325, False, True),
    (9, "Cached JobGrepResponse", "route", "client", 365, True, False),
    (10, "9. SELECT public.scraped_jobs with filters", "route", "database", 420, False, False),
    (11, "Rows and exact count", "database", "route", 445, True, False),
    (12, "10. Normalize rows; apply Malaysia, tech and salary filters", "route", "route", 470, False, True),
    (13, "11. filterJobsBySearchQuery(jobs, query)", "route", "relevance", 505, False, False),
    (14, "Ranked jobs", "relevance", "route", 530, True, False),
    (15, "12. Paginate and build source breakdown", "route", "route", 555, False, True),
    (16, "JobGrepResponse (cached=false)", "route", "client", 580, True, False),
    (17, "13. Catch fetch failure", "route", "route", 625, False, True),
    (18, "Stale JobGrepResponse (cached=true, stale=true)", "route", "client", 655, True, False),
    (19, "JobGrepResponse", "client", "manager", 735, True, False),
    (20, "14. applyMatchScoring(); applyClientFilters()", "manager", "manager", 760, False, True),
    (21, "15. renderResults(); renderSourceBar()", "manager", "results", 785, False, False),
    (22, "16. renderJobMarkers(); setData()", "manager", "results", 810, False, False),
    (23, "Display job cards, result count and markers", "results", "user", 835, True, False),
    (24, "Empty JobGrepResponse", "client", "manager", 885, True, False),
    (25, "17. renderResults([])", "manager", "results", 910, False, False),
    (26, "Display no matching jobs", "results", "user", 930, True, False),
    (27, "HTTP 502 / network error", "route", "client", 975, True, False),
    (28, "Throw Daily Index failed", "client", "manager", 995, True, False),
    (29, "18. setStatus(Daily Index error)", "manager", "ui", 1015, False, False),
    (30, "Display error; remain in guest state", "ui", "user", 1035, True, False),
    (31, "19. Clear loading state and hide overlay", "manager", "ui", 1048, False, False),
]


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {
        "host": "Electron",
        "agent": "PetaKerja Architecture Explorer",
        "version": "27.0.2",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"name": "Search Jobs", "id": PAGE_ID})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1600", "dy": "1100", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": "1600", "pageHeight": "1100", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": ROOT_ID})
    ET.SubElement(root, "mxCell", {"id": LAYER_ID, "parent": ROOT_ID})
    background = ET.SubElement(root, "mxCell", {
        "id": "job-search-page-background", "parent": LAYER_ID, "vertex": "1",
        "style": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=none;locked=1;pointerEvents=0;",
    })
    add_geometry(background, x=0, y=0, width=1600, height=1100)

    add_object(
        root,
        key=f"{KEY_PREFIX}/title",
        cell_id="job-search-title",
        label="PetaKerja Search Jobs Sequence",
        style=TEXT_STYLE + "fontSize=18;fontStyle=1;",
        vertex=True,
        geometry={"x": 500, "y": 20, "width": 600, "height": 30},
    )

    activation_ids: dict[str, str] = {}
    for slug, label, centre, _node in PARTICIPANTS:
        participant_key = f"{KEY_PREFIX}/participant-{slug}"
        if slug == "user":
            add_object(
                root, key=participant_key, cell_id="job-search-participant-user", label="",
                style=ACTOR_STYLE, vertex=True,
                geometry={"x": centre - 10, "y": 72, "width": 20, "height": 40},
            )
            add_object(
                root, key=None, cell_id="job-search-participant-user-label",
                label="User", style=TEXT_STYLE, vertex=True,
                geometry={"x": centre - 35, "y": 110, "width": 70, "height": 20},
            )
        else:
            add_object(
                root, key=participant_key, cell_id=f"job-search-participant-{slug}", label=label,
                style=LIFELINE_STYLE, vertex=True,
                geometry={"x": centre - 50, "y": 70, "width": 100, "height": 60},
            )
        activation_id = f"job-search-activation-{slug}"
        activation_ids[slug] = activation_id
        add_object(
            root, key=participant_key + "-activation", cell_id=activation_id, label="",
            style=ACTIVATION_STYLE, vertex=True,
            geometry={"x": centre - 5, "y": ACTIVATION_Y, "width": 10, "height": ACTIVATION_HEIGHT},
        )

    for key, label, x, y, width, height in (
        ("fragment-cache", "alt", 620, 310, 760, 385),
        ("fragment-query", "opt", 825, 485, 510, 65),
        ("fragment-results", "alt", 55, 705, 1460, 345),
    ):
        add_object(
            root, key=f"{KEY_PREFIX}/{key}", cell_id=f"job-search-{key}",
            label=label, style=FRAME_STYLE, vertex=True,
            geometry={"x": x, "y": y, "width": width, "height": height},
        )

    for index, label, source, target, y, returned, self_message in MESSAGES:
        add_message(
            root, index=index, label=label,
            source=activation_ids[source], target=activation_ids[target], y=y,
            returned=returned, self_message=self_message,
        )

    add_divider(root, key=f"{KEY_PREFIX}/cache-divider-1", y=390, x1=620, x2=1380)
    add_divider(root, key=f"{KEY_PREFIX}/cache-divider-2", y=600, x1=620, x2=1380)
    add_operand(root, key=f"{KEY_PREFIX}/cache-hit", label="[fresh 60-second cache]", x=690, y=315)
    add_operand(root, key=f"{KEY_PREFIX}/cache-miss", label="[cache miss or refresh]", x=635, y=392)
    add_operand(root, key=f"{KEY_PREFIX}/cache-stale", label="[fetch failure and stale cache exists]", x=635, y=602, width=300)
    add_operand(root, key=f"{KEY_PREFIX}/query-present", label="[query supplied]", x=880, y=487, width=190)

    add_divider(root, key=f"{KEY_PREFIX}/result-divider-1", y=860, x1=55, x2=1515)
    add_divider(root, key=f"{KEY_PREFIX}/result-divider-2", y=950, x1=55, x2=1515)
    add_operand(root, key=f"{KEY_PREFIX}/results-found", label="[jobs returned]", x=125, y=710)
    add_operand(root, key=f"{KEY_PREFIX}/results-empty", label="[no matching jobs]", x=70, y=862)
    add_operand(root, key=f"{KEY_PREFIX}/results-error", label="[request fails without usable cache]", x=70, y=952, width=300)

    add_object(
        root,
        key=f"{KEY_PREFIX}/note",
        cell_id="job-search-note",
        label="Daily Index is public. Google sign-in is not required for this search path.",
        style=TEXT_STYLE + "fontSize=10;fontStyle=2;fontColor=#555555;",
        vertex=True,
        geometry={"x": 400, "y": 1072, "width": 800, "height": 18},
    )

    return ET.ElementTree(mxfile)


def main() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    tree = build()
    ET.indent(tree, space="  ")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    EDITOR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=False)
    tree.write(EDITOR_OUTPUT, encoding="utf-8", xml_declaration=False)
    apply_label_modes_to_file(OUTPUT)
    apply_label_modes_to_file(EDITOR_OUTPUT)
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {EDITOR_OUTPUT}")


if __name__ == "__main__":
    main()
