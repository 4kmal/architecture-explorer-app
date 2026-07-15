#!/usr/bin/env python3
"""Correct and normalize the reorganized PetaKerja domain class diagram.

The transformation is intentionally narrow: it preserves the user's relative
layout, fixes verified model details and connector endpoints, adds stable
Explorer identities, and translates the complete drawing into positive page
coordinates. The original file is backed up once before any rewrite.
"""

from __future__ import annotations

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from paths import EDITOR, EXPORTS

SOURCE = EDITOR / "class-domain-petakerja-original.drawio"
BACKUP = EXPORTS / "Class Diagram PetaKerja - Before Corrections.drawio"
REVISION = "2026-07-14-core-domain-v1"

PAGE_WIDTH = 2650
PAGE_HEIGHT = 2860
SHIFT_X = 970
SHIFT_Y = 1060

CLASS_KEYS = {
    "JzSmHml7n7fI4_WiAD8F-8": "auth-identity",
    "JzSmHml7n7fI4_WiAD8F-12": "user-profile",
    "JzSmHml7n7fI4_WiAD8F-16": "state-entity",
    "JzSmHml7n7fI4_WiAD8F-18": "data-source-entity",
    "JzSmHml7n7fI4_WiAD8F-20": "poi-group-entity",
    "JzSmHml7n7fI4_WiAD8F-22": "poi-category-entity",
    "JzSmHml7n7fI4_WiAD8F-24": "poi-entity",
    "JzSmHml7n7fI4_WiAD8F-28": "highlight-entity",
    "JzSmHml7n7fI4_WiAD8F-32": "open-data-api",
    "JzSmHml7n7fI4_WiAD8F-36": "job-entity",
    "JzSmHml7n7fI4_WiAD8F-40": "job-state-entity",
    "JzSmHml7n7fI4_WiAD8F-44": "ai-credential-entity",
    "JzSmHml7n7fI4_WiAD8F-48": "ai-preference-entity",
    "JzSmHml7n7fI4_WiAD8F-52": "ai-usage-entity",
    "JzSmHml7n7fI4_WiAD8F-56": "audit-log-entity",
}

EDGE_ENDPOINTS = {
    # State -> UserProfile (previously targeted the operations compartment).
    "JzSmHml7n7fI4_WiAD8F-64": (
        "JzSmHml7n7fI4_WiAD8F-16", "JzSmHml7n7fI4_WiAD8F-12"
    ),
    # UserProfile -> AIProviderCredential (previously targeted attributes).
    "JzSmHml7n7fI4_WiAD8F-97": (
        "JzSmHml7n7fI4_WiAD8F-12", "JzSmHml7n7fI4_WiAD8F-44"
    ),
    # UserProfile -> AIUsageEvent (both endpoints were compartments).
    "JzSmHml7n7fI4_WiAD8F-103": (
        "JzSmHml7n7fI4_WiAD8F-12", "JzSmHml7n7fI4_WiAD8F-52"
    ),
    # UserProfile -> AdminAuditLog (previously targeted operations).
    "JzSmHml7n7fI4_WiAD8F-106": (
        "JzSmHml7n7fI4_WiAD8F-12", "JzSmHml7n7fI4_WiAD8F-56"
    ),
}


def number(value: str) -> float:
    return float(value)


def formatted(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:g}"


def shift_geometry(geometry: ET.Element, dx: int, dy: int) -> None:
    if geometry.get("x") is not None:
        geometry.set("x", formatted(number(geometry.get("x", "0")) + dx))
    if geometry.get("y") is not None:
        geometry.set("y", formatted(number(geometry.get("y", "0")) + dy))


def set_geometry(cell: ET.Element, **values: int | str) -> None:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        raise RuntimeError(f"Cell {cell.get('id')} has no mxGeometry")
    for key, value in values.items():
        geometry.set(key, str(value))


def make_text_cell(
    root: ET.Element,
    base_id: str,
    cell_id: str,
    value: str,
    style: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    existing = root.find(f"mxCell[@id='{cell_id}']")
    if existing is not None:
        root.remove(existing)
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "value": value, "style": style, "parent": base_id, "vertex": "1"},
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"},
    )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    if not BACKUP.exists():
        shutil.copy2(SOURCE, BACKUP)

    tree = ET.parse(SOURCE)
    mxfile = tree.getroot()
    diagrams = mxfile.findall("diagram")
    if len(diagrams) != 1:
        raise RuntimeError(f"Expected one diagram page, found {len(diagrams)}")

    diagram = diagrams[0]
    model = diagram.find("mxGraphModel")
    root = model.find("root") if model is not None else None
    if model is None or root is None:
        raise RuntimeError("The Draw.io page has no mxGraphModel/root")

    cells = {cell.get("id", ""): cell for cell in root.findall(".//mxCell")}
    missing = set(CLASS_KEYS) - set(cells)
    if missing:
        raise RuntimeError(f"Missing expected class cells: {sorted(missing)}")

    root_ids = [cell.get("id", "") for cell in root.findall("mxCell") if not cell.get("parent")]
    if len(root_ids) != 1:
        raise RuntimeError("Could not determine the Draw.io root cell")
    base_cells = [cell for cell in root.findall("mxCell") if cell.get("parent") == root_ids[0]]
    if len(base_cells) != 1:
        raise RuntimeError("Could not determine the Draw.io default layer")
    base_id = base_cells[0].get("id", "")

    # Preserve the user's layout exactly, applying one uniform translation only
    # when upgrading the unnormalised source.
    if diagram.get("petakerjaRevision") != REVISION:
        for cell in root.findall("mxCell"):
            if cell.get("parent") == base_id and cell.get("vertex") == "1":
                geometry = cell.find("mxGeometry")
                if geometry is not None:
                    shift_geometry(geometry, SHIFT_X, SHIFT_Y)
            if cell.get("edge") == "1":
                geometry = cell.find("mxGeometry")
                if geometry is not None:
                    for point in geometry.findall(".//mxPoint"):
                        shift_geometry(point, SHIFT_X, SHIFT_Y)

    # Stable, non-visual identities make the reorganized diagram resilient to
    # future Draw.io ID changes and enable exact Explorer matching.
    for cell_id, key in CLASS_KEYS.items():
        cells[cell_id].set("petakerjaKey", f"domain/{key}")

    # Verified TypeScript/Supabase content corrections.
    cells["JzSmHml7n7fI4_WiAD8F-23"].set(
        "value",
        "<div>- id : text</div><div>- group_id : text</div><div>- name : text</div>"
        "<div>- color : text</div><div>- icon : text</div>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-25"].set(
        "value",
        "<div>- id : uuid</div><div>- data_source_id : uuid</div>"
        "<div>- category : text</div><div>- state_id : text?</div>"
        "<div>- name : text?</div><div>- geom : geometry?</div><div>- address : text?</div>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-29"].set(
        "value",
        "<div>- id : string</div><div>- name : string</div>"
        "<div>- mode : polygon | box</div><div>- coordinates : [number, number][]</div>"
        "<div>- feature : GeoJSON.Feature | null</div><div>- pois : HighlightedPOIContext[]</div>",
    )
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-28"], height=248)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-29"], height=114)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-30"], y=160)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-31"], y=168)

    cells["JzSmHml7n7fI4_WiAD8F-33"].set(
        "value",
        "<div><u>- cache : Map {static}</u></div>"
        "<div><u>- regionCache : Map {static}</u></div>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-35"].set(
        "value",
        "<div><u>+ fetchDataset(type) {static}</u></div>"
        "<div><u>+ getLatestDataByRegion(type, dataKey) {static}</u></div>"
        "<div><u>+ warmLatestDataByRegion(type, dataKey) {static}</u></div>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-36"].set(
        "value",
        "<b>JobListing</b><br><span style=\"font-size:10px;color:#4b5563;\">"
        "&lt;&lt;interface&gt;&gt;</span>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-37"].set(
        "value",
        "<div>- id : string</div><div>- title : string</div><div>- company : string</div>"
        "<div>- location : string</div><div>- salary : string?</div>"
        "<div>- source : string</div><div>- applyLink : string</div>",
    )
    cells["JzSmHml7n7fI4_WiAD8F-49"].set(
        "value",
        "<div>- user_id : uuid</div>"
        "<div>- default_provider_id, default_model_id : text?</div>"
        "<div>- ask_provider_id, ask_model_id : text?</div>"
        "<div>- plan_provider_id, plan_model_id : text?</div>"
        "<div>- agent_provider_id, agent_model_id : text?</div>"
        "<div>- updated_at : timestamptz</div>",
    )
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-48"], height=214)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-49"], height=114)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-50"], y=160)
    set_geometry(cells["JzSmHml7n7fI4_WiAD8F-51"], y=168)

    for edge_id, (source, target) in EDGE_ENDPOINTS.items():
        edge = cells[edge_id]
        edge.set("source", source)
        edge.set("target", target)
    cells["JzSmHml7n7fI4_WiAD8F-109"].set("value", "dipadankan melalui provider_id")

    title_style = (
        "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
        "whiteSpace=wrap;fontFamily=Arial;fontSize=24;fontStyle=1;"
    )
    note_style = (
        "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
        "whiteSpace=wrap;fontFamily=Arial;fontSize=11;fontColor=#4b5563;"
    )
    legend_style = (
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "whiteSpace=wrap;fontFamily=Arial;fontSize=10;fontColor=#4b5563;"
    )
    make_text_cell(
        root, base_id, "petakerja-domain-title",
        "<b>Rajah Kelas Domain Teras Sistem PetaKerja</b>",
        title_style, 425, 35, 1800, 38,
    )
    make_text_cell(
        root, base_id, "petakerja-domain-subtitle",
        "Model domain berdasarkan kod TypeScript dan jadual Supabase langsung. "
        "Operasi pada entiti mewakili tanggungjawab aplikasi yang mengurus rekod, "
        "bukan kaedah ORM atau kaedah literal pada entiti.",
        note_style, 425, 78, 1800, 42,
    )
    make_text_cell(
        root, base_id, "petakerja-domain-legend",
        "Legenda: &lt;&lt;entity&gt;&gt; = rekod Supabase; &lt;&lt;service&gt;&gt; = servis TypeScript; "
        "&lt;&lt;interface&gt;&gt; = kontrak TypeScript; JobListing menormalkan rekod "
        "public.scraped_jobs; garisan putus-putus = hubungan logik atau dependency; "
        "berlian kosong = aggregation.",
        legend_style, 425, 2790, 1800, 46,
    )

    diagram.set("id", "petakerja_domain")
    diagram.set("name", "Rajah Kelas Domain Teras")
    diagram.set("petakerjaRevision", REVISION)
    model.set("pageWidth", str(PAGE_WIDTH))
    model.set("pageHeight", str(PAGE_HEIGHT))
    model.set("dx", str(PAGE_WIDTH))
    model.set("dy", str(PAGE_HEIGHT))

    # Structural verification before replacing the source.
    cells = {cell.get("id", ""): cell for cell in root.findall(".//mxCell")}
    ids = list(cells)
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate mxCell IDs found after correction")
    edges = [cell for cell in cells.values() if cell.get("edge") == "1"]
    class_ids = set(CLASS_KEYS)
    if len(edges) != 15:
        raise RuntimeError(f"Expected 15 relationships, found {len(edges)}")
    invalid_edges = [
        edge.get("id") for edge in edges
        if edge.get("source") not in class_ids or edge.get("target") not in class_ids
    ]
    if invalid_edges:
        raise RuntimeError(f"Relationships not attached to outer classes: {invalid_edges}")
    for cell in root.findall("mxCell"):
        if cell.get("parent") != base_id or cell.get("vertex") != "1":
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            continue
        if number(geometry.get("x", "0")) < 0 or number(geometry.get("y", "0")) < 0:
            raise RuntimeError(f"Negative page geometry remains on {cell.get('id')}")

    ET.indent(tree, space="  ")
    temporary = SOURCE.with_suffix(".drawio.tmp")
    tree.write(temporary, encoding="utf-8", xml_declaration=False)
    temporary.replace(SOURCE)

    print(f"Corrected: {SOURCE}")
    print(f"Backup:    {BACKUP}")
    print(f"Classes:   {len(CLASS_KEYS)}")
    print(f"Edges:     {len(edges)}")


if __name__ == "__main__":
    main()
