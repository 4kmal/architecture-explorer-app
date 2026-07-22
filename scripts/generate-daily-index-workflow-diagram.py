#!/usr/bin/env python3
"""Generate the editable bilingual Daily Index workflow diagram.

The diagram documents the checked-in path from the scheduled GitHub Actions
workflow, through the TypeScript scraper and Supabase serving table, to the
same-origin Vercel/Express API and PetaKerja Job Finder frontend.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import html
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "assets" / "editor" / "daily-index-workflow.drawio"
BRANDS = ROOT / "assets" / "brands"
PAGE_ID = "petakerja_daily_index_workflow"
PAGE_WIDTH = 1920
PAGE_HEIGHT = 900


TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=28;fontStyle=1;fontColor=light-dark(#172033,#edf2fb);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=13;fontColor=light-dark(#667085,#aeb8c8);"
CARD_BASE = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1b2029);strokeWidth=1.5;fontColor=light-dark(#172033,#edf2fb);fontFamily=Arial;fontSize=15;align=left;verticalAlign=top;spacingTop=142;spacingLeft=22;spacingRight=18;shadow=1;"
CARD_GITHUB = CARD_BASE + "strokeColor=light-dark(#59636f,#8c98a5);"
CARD_SCRIPT = CARD_BASE + "strokeColor=light-dark(#3178c6,#6ba7dc);"
CARD_SUPABASE = CARD_BASE + "strokeColor=light-dark(#2fae72,#62d49b);"
CARD_VERCEL = CARD_BASE + "strokeColor=light-dark(#59636f,#aeb8c8);"
CARD_FRONTEND = CARD_BASE + "strokeColor=light-dark(#2f6bb2,#6fa7e6);"
LOGO_TILE = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=light-dark(#d0d5dd,#667085);strokeWidth=1;shadow=0;"
IMAGE = "shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;strokeColor=none;fillColor=none;"
NUMBER = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=light-dark(#253858,#4f6591);strokeColor=none;fontColor=#ffffff;fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=middle;"
SOURCE_GROUP = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#f8fafc,#171c24);strokeColor=light-dark(#b8c4d4,#596579);strokeWidth=1.2;fontColor=light-dark(#344054,#e1e7f0);fontFamily=Arial;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingTop=14;spacingLeft=18;"
SOURCE_LABEL = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=10;fontColor=light-dark(#475467,#cbd4e1);"
NOTE_SECURITY = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#eef4ff,#182338);strokeColor=light-dark(#7ea6df,#5e83ba);strokeWidth=1.2;fontColor=light-dark(#17375e,#e8f1ff);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=14;"
NOTE_FAILURE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8e8,#2a2417);strokeColor=light-dark(#d8a441,#b8862d);strokeWidth=1.2;fontColor=light-dark(#5f430d,#fff0c4);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=14;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=light-dark(#667085,#aeb8c8);strokeWidth=1.7;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=11;labelBackgroundColor=light-dark(#ffffff,#15191f);"
EDGE_DATA = EDGE + "strokeColor=light-dark(#2f6bb2,#70a8e6);"
EDGE_WRITE = EDGE + "strokeColor=light-dark(#2fae72,#62d49b);"
EDGE_SOURCE = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#59636f,#9ba8b8);"


@dataclass(frozen=True)
class Vertex:
    key: str
    identifier: str
    label_en: str
    label_ms: str
    x: int
    y: int
    width: int
    height: int
    style: str
    node_ids: str = ""
    table_name: str = ""
    hotspots: str = ""
    role: str = "stage"


@dataclass(frozen=True)
class Flow:
    key: str
    identifier: str
    source: str
    target: str
    label_en: str
    label_ms: str
    style: str = EDGE
    points: tuple[tuple[int, int], ...] = ()


def rich(title: str, *lines: str) -> str:
    detail = "<br>".join(html.escape(line) for line in lines)
    return f"<b>{html.escape(title)}</b>" + (f"<br>{detail}" if detail else "")


def attrs(label_en: str, label_ms: str, key: str, node_ids: str = "",
          table_name: str = "", hotspots: str = "", **extra: str) -> dict[str, str]:
    result = {
        "label": label_en,
        "labelEn": label_en,
        "labelMs": label_ms,
        "petakerjaKey": f"daily-index-workflow/{key}",
        **extra,
    }
    if node_ids:
        result.update({"nodeIds": node_ids, "component": "1"})
    if table_name:
        result["tableName"] = table_name
    if hotspots:
        result["uiHotspots"] = hotspots
    return result


def add_vertex(root: ET.Element, spec: Vertex) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(
            spec.label_en, spec.label_ms, spec.key, spec.node_ids,
            spec.table_name, spec.hotspots, workflowRole=spec.role,
        ),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "vertex": "1", "style": spec.style,
    })
    ET.SubElement(cell, "mxGeometry", {
        "x": str(spec.x), "y": str(spec.y), "width": str(spec.width),
        "height": str(spec.height), "as": "geometry",
    })
    return spec.identifier


def add_raw_vertex(root: ET.Element, identifier: str, value: str, x: int, y: int,
                   width: int, height: int, style: str) -> str:
    attributes = {
        "id": identifier, "value": value, "parent": "1", "vertex": "1", "style": style,
    }
    if value:
        attributes.update({"labelEn": value, "labelMs": value})
    cell = ET.SubElement(root, "mxCell", attributes)
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height),
        "as": "geometry",
    })
    return identifier


def add_flow(root: ET.Element, spec: Flow) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(spec.label_en, spec.label_ms, spec.key, workflowRole="flow"),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": spec.source,
        "target": spec.target, "style": spec.style,
    })
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if spec.points:
        array = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in spec.points:
            ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})
    return spec.identifier


def image_data_uri(path: Path) -> str:
    if path.suffix.lower() == ".svg":
        return "data:image/svg+xml," + quote(path.read_text(encoding="utf-8"), safe="")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{path.suffix.lower().lstrip('.')},{encoded}"


def add_logo(root: ET.Element, key: str, path: Path, x: int, y: int,
             size: int = 70, tile: bool = True) -> None:
    if tile:
        add_raw_vertex(root, f"daily-logo-tile-{key}", "", x - 6, y - 6, size + 12, size + 12, LOGO_TILE)
    add_raw_vertex(
        root, f"daily-logo-{key}", "", x, y, size, size,
        IMAGE + f"image={image_data_uri(path)};",
    )


def build_document() -> ET.Element:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja Daily Index Workflow Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaLayoutStandard": "daily-index-workflow-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": PAGE_ID,
        "name": "Daily Index Workflow",
    })
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH), "dy": str(PAGE_HEIGHT), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(PAGE_WIDTH),
        "pageHeight": str(PAGE_HEIGHT), "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    vertices = [
        Vertex("title", "daily-title", "Daily Index Workflow", "Aliran Kerja Indeks Harian", 50, 24, 1820, 42, TITLE, role="title"),
        Vertex("subtitle", "daily-subtitle", "GitHub Actions to Supabase to the PetaKerja Job Finder", "GitHub Actions ke Supabase hingga Pencari Kerja PetaKerja", 50, 70, 1820, 26, SUBTITLE, role="subtitle"),

        Vertex("stage-github", "daily-stage-github", rich("GitHub Actions", ".github/workflows/scrape-jobs.yml", "Daily 02:00 UTC · manual rerun"), rich("GitHub Actions", ".github/workflows/scrape-jobs.yml", "Harian 02:00 UTC · larian semula manual"), 50, 170, 320, 270, CARD_GITHUB, "github-actions"),
        Vertex("stage-script", "daily-stage-script", rich("TypeScript scraper", "scripts/scrape-jobs.ts", "Fetch · normalize · deduplicate"), rich("Scraper TypeScript", "scripts/scrape-jobs.ts", "Ambil · normalisasi · nyahpendua"), 425, 170, 320, 270, CARD_SCRIPT, "daily-index-scraper"),
        Vertex("stage-supabase", "daily-stage-supabase", rich("Supabase PostgreSQL", "public.scraped_jobs", "Upsert · stale cleanup"), rich("PostgreSQL Supabase", "public.scraped_jobs", "Upsert · pembersihan rekod lapuk"), 800, 170, 320, 270, CARD_SUPABASE, "supabase-db", "scraped_jobs"),
        Vertex("stage-api", "daily-stage-api", rich("Vercel + Express", "GET /api/jobs/supa", "Filter · paginate · cache 60 s"), rich("Vercel + Express", "GET /api/jobs/supa", "Tapis · halaman · cache 60 s"), 1175, 170, 320, 270, CARD_VERCEL, "vercel-runtime,express-app,supa-jobs-route"),
        Vertex("stage-frontend", "daily-stage-frontend", rich("PetaKerja Daily Index", "searchSupaJobs() → executeSupaSearch()", "Cards + map + refreshed time"), rich("Indeks Harian PetaKerja", "searchSupaJobs() → executeSupaSearch()", "Kad + peta + masa disegarkan"), 1550, 170, 320, 270, CARD_FRONTEND, "browser,job-manager,jobs-api", hotspots="jobs-search,jobs-cards,jobs-map"),

        Vertex("job-sources", "daily-job-sources", "Eight configured job sources", "Lapan sumber pekerjaan dikonfigurasikan", 395, 505, 760, 160, SOURCE_GROUP, "daily-index-job-sources", role="source-group"),
        Vertex("note-security", "daily-note-security", rich("Trusted CI boundary", "SUPABASE_SERVICE_ROLE_KEY stays in GitHub Actions and never enters the browser."), rich("Sempadan CI dipercayai", "SUPABASE_SERVICE_ROLE_KEY kekal dalam GitHub Actions dan tidak pernah masuk ke pelayar."), 70, 715, 825, 100, NOTE_SECURITY, "github-actions,daily-index-scraper", role="note"),
        Vertex("note-failure", "daily-note-failure", rich("Failure-safe serving", "A zero-result scrape keeps the previous Supabase snapshot; API failures use stale cache when available."), rich("Penyampaian tahan kegagalan", "Scrape sifar hasil mengekalkan snapshot Supabase terdahulu; kegagalan API menggunakan cache lapuk jika tersedia."), 1025, 715, 825, 100, NOTE_FAILURE, "daily-index-scraper,supa-jobs-route,supabase-db", "scraped_jobs", role="note"),
    ]

    ids: dict[str, str] = {}
    for vertex in vertices:
        ids[vertex.key] = add_vertex(root, vertex)

    stage_x = [50, 425, 800, 1175, 1550]
    for number, x in enumerate(stage_x, 1):
        add_raw_vertex(root, f"daily-number-{number}", str(number), x + 18, 188, 34, 34, NUMBER)

    add_logo(root, "github", ROOT / "vendor" / "drawio" / "images" / "github-logo.svg", 72, 232)
    add_logo(root, "typescript", BRANDS / "typescript.svg", 447, 232)
    add_logo(root, "supabase", BRANDS / "supabase.svg", 822, 232)
    add_logo(root, "vercel", BRANDS / "vercel.svg", 1197, 232)
    add_logo(root, "petakerja", REPOSITORY_ROOT / "public" / "icon" / "android-chrome-192x192.png", 1572, 232)

    source_names = ("Maukerja", "Hiredly", "Ricebowl", "Graduan", "Jora", "JobStreet", "Jobstore", "Careerjet")
    source_slugs = ("maukerja", "hiredly", "ricebowl", "graduan", "jora", "jobstreet", "jobstore", "careerjet")
    for index, (name, slug) in enumerate(zip(source_names, source_slugs)):
        x = 425 + index * 88
        add_logo(
            root, f"source-{slug}",
            REPOSITORY_ROOT / "public" / "icons" / "job-sources" / f"{slug}.svg",
            x, 550, size=42, tile=False,
        )
        add_raw_vertex(root, f"daily-source-label-{slug}", name, x - 12, 600, 66, 22, SOURCE_LABEL)

    flows = [
        Flow("flow-trigger", "daily-flow-trigger", ids["stage-github"], ids["stage-script"], "02:00 UTC or manual", "02:00 UTC atau manual", EDGE_DATA),
        Flow("flow-write", "daily-flow-write", ids["stage-script"], ids["stage-supabase"], "Upsert + cleanup", "Upsert + pembersihan", EDGE_WRITE),
        Flow("flow-read", "daily-flow-read", ids["stage-supabase"], ids["stage-api"], "SELECT + freshness", "SELECT + kesegaran", EDGE_DATA),
        Flow("flow-serve", "daily-flow-serve", ids["stage-api"], ids["stage-frontend"], "GET /api/jobs/supa", "GET /api/jobs/supa", EDGE_DATA),
        Flow("flow-sources", "daily-flow-sources", ids["job-sources"], ids["stage-script"], "Fetch public listings", "Ambil senarai awam", EDGE_SOURCE, ((585, 475),)),
    ]
    for flow in flows:
        add_flow(root, flow)

    return mxfile


def validate(document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise ValueError(f"Missing Draw.io page {PAGE_ID}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1920", "900"):
        raise ValueError("Daily Index canvas must be exactly 1920 x 900")
    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if len(keys) != len(set(keys)) or not all(keys):
        raise ValueError("Daily Index component keys must be present and unique")
    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            raise ValueError(f"{wrapper.get('id')} is missing bilingual labels")
    image_cells = [
        cell for cell in diagram.findall(".//mxCell")
        if "shape=image" in cell.get("style", "")
    ]
    if len(image_cells) != 13:
        raise ValueError(f"Expected 13 embedded logos, found {len(image_cells)}")
    for cell in image_cells:
        style = cell.get("style", "")
        if "image=data:image/" not in style or "image=http" in style:
            raise ValueError(f"{cell.get('id')} does not use an embedded image")


def main() -> None:
    document = build_document()
    validate(document)
    ET.indent(document, space="  ")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(document).write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
