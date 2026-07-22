#!/usr/bin/env python3
"""Generate the editable bilingual PetaKerja Live Search workflow diagram."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import html
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "assets" / "editor" / "live-search-workflow.drawio"
BRANDS = ROOT / "assets" / "brands"
PAGE_ID = "petakerja_live_search_workflow"
PAGE_WIDTH = 1920
PAGE_HEIGHT = 900


TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=28;fontStyle=1;fontColor=light-dark(#172033,#edf2fb);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=13;fontColor=light-dark(#667085,#aeb8c8);"
CARD_BASE = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1b2029);strokeWidth=1.5;fontColor=light-dark(#172033,#edf2fb);fontFamily=Arial;fontSize=14;align=left;verticalAlign=top;spacingTop=132;spacingLeft=20;spacingRight=16;shadow=1;"
CARD_BROWSER = CARD_BASE + "strokeColor=light-dark(#2f6bb2,#70a8e6);"
CARD_AUTH = CARD_BASE + "strokeColor=light-dark(#c58a22,#e0ad4f);"
CARD_SERVER = CARD_BASE + "strokeColor=light-dark(#59636f,#aeb8c8);"
CARD_FANOUT = CARD_BASE + "strokeColor=light-dark(#cf7025,#ee9a55);"
CARD_RESULT = CARD_BASE + "strokeColor=light-dark(#168a83,#55c7be);"
LOGO_TILE = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=#10141b;strokeColor=light-dark(#d0d5dd,#667085);strokeWidth=1;shadow=0;"
IMAGE = "shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;strokeColor=none;fillColor=none;"
NUMBER = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=light-dark(#253858,#4f6591);strokeColor=none;fontColor=#ffffff;fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=middle;"
SOURCE_GROUP = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8f1,#211b18);strokeColor=light-dark(#cf7025,#ee9a55);strokeWidth=1.2;fontColor=light-dark(#6b3410,#ffe4d0);fontFamily=Arial;fontSize=13;fontStyle=1;align=left;verticalAlign=top;spacingTop=12;spacingLeft=16;"
SOURCE_LABEL = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=9;fontColor=light-dark(#66462f,#efd1bb);"
COMPARISON_FRAME = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f8fafc,#171c24);strokeColor=light-dark(#b8c4d4,#596579);strokeWidth=1.2;fontColor=light-dark(#344054,#e1e7f0);fontFamily=Arial;fontSize=14;fontStyle=1;align=left;verticalAlign=top;spacingTop=12;spacingLeft=16;"
COMPARE_LIVE = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=light-dark(#eef4ff,#182338);strokeColor=light-dark(#7ea6df,#5e83ba);strokeWidth=1;fontColor=light-dark(#17375e,#e8f1ff);fontFamily=Arial;fontSize=12;align=left;verticalAlign=top;spacing=12;"
COMPARE_DAILY = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=light-dark(#ecfdf3,#17291f);strokeColor=light-dark(#68b88a,#4f9e73);strokeWidth=1;fontColor=light-dark(#14532d,#d8f7e5);fontFamily=Arial;fontSize=12;align=left;verticalAlign=top;spacing=12;"
NOTE_FAILURE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8e8,#2a2417);strokeColor=light-dark(#d8a441,#b8862d);strokeWidth=1.2;fontColor=light-dark(#5f430d,#fff0c4);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeWidth=1.7;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
EDGE_BLUE = EDGE + "strokeColor=light-dark(#2f6bb2,#70a8e6);"
EDGE_AMBER = EDGE + "strokeColor=light-dark(#c58a22,#e0ad4f);"
EDGE_ORANGE = EDGE + "strokeColor=light-dark(#cf7025,#ee9a55);"
EDGE_TEAL = EDGE + "strokeColor=light-dark(#168a83,#55c7be);"
EDGE_BYPASS = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#168a83,#55c7be);"


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
    style: str
    points: tuple[tuple[int, int], ...] = ()


def rich(title: str, *lines: str) -> str:
    return f"<b>{html.escape(title)}</b>" + ("<br>" + "<br>".join(html.escape(line) for line in lines) if lines else "")


def attrs(label_en: str, label_ms: str, key: str, node_ids: str = "", hotspots: str = "", **extra: str) -> dict[str, str]:
    result = {
        "label": label_en,
        "labelEn": label_en,
        "labelMs": label_ms,
        "petakerjaKey": f"live-search-workflow/{key}",
        **extra,
    }
    if node_ids:
        result.update({"nodeIds": node_ids, "component": "1"})
    if hotspots:
        result["uiHotspots"] = hotspots
    return result


def add_vertex(root: ET.Element, spec: Vertex) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(spec.label_en, spec.label_ms, spec.key, spec.node_ids, spec.hotspots, workflowRole=spec.role),
    })
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": spec.style})
    ET.SubElement(cell, "mxGeometry", {
        "x": str(spec.x), "y": str(spec.y), "width": str(spec.width), "height": str(spec.height), "as": "geometry",
    })
    return spec.identifier


def add_raw_vertex(root: ET.Element, identifier: str, value: str, x: int, y: int, width: int, height: int, style: str) -> str:
    attributes = {"id": identifier, "value": value, "parent": "1", "vertex": "1", "style": style}
    if value:
        attributes.update({"labelEn": value, "labelMs": value})
    cell = ET.SubElement(root, "mxCell", attributes)
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry",
    })
    return identifier


def add_flow(root: ET.Element, spec: Flow) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(spec.label_en, spec.label_ms, spec.key, workflowRole="flow"),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": spec.source, "target": spec.target, "style": spec.style,
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


def add_logo(root: ET.Element, key: str, path: Path, x: int, y: int, width: int = 66, height: int = 66, tile: bool = True) -> None:
    if tile:
        add_raw_vertex(root, f"live-logo-tile-{key}", "", x - 6, y - 6, width + 12, height + 12, LOGO_TILE)
    add_raw_vertex(root, f"live-logo-{key}", "", x, y, width, height, IMAGE + f"image={image_data_uri(path)};")


def build_document() -> ET.Element:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja Live Search Workflow Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaLayoutStandard": "live-search-workflow-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": PAGE_ID, "name": "Live Search Workflow"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH), "dy": str(PAGE_HEIGHT), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": str(PAGE_WIDTH), "pageHeight": str(PAGE_HEIGHT),
        "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    vertices = [
        Vertex("title", "live-title", "Live Search Workflow", "Aliran Kerja Carian Langsung", 50, 20, 1820, 42, TITLE, role="title"),
        Vertex("subtitle", "live-subtitle", "Authenticated request-time search across Malaysian job sources", "Carian masa permintaan berautentikasi merentasi sumber pekerjaan Malaysia", 50, 64, 1820, 26, SUBTITLE, role="subtitle"),
        Vertex("stage-request", "live-stage-request", rich("PetaKerja Live Search", "Signed-in query + location + filters", "JobFinderManager.executeLiveSearch()"), rich("Carian Langsung PetaKerja", "Pertanyaan + lokasi + penapis pengguna log masuk", "JobFinderManager.executeLiveSearch()"), 30, 125, 330, 285, CARD_BROWSER, "job-manager,browser,jobs-api", "jobs-search"),
        Vertex("stage-auth", "live-stage-auth", rich("Authenticated request", "searchJobs() + authenticatedFetch()", "Better Auth cookie · requireAuth"), rich("Permintaan berautentikasi", "searchJobs() + authenticatedFetch()", "Cookie Better Auth · requireAuth"), 400, 125, 330, 285, CARD_AUTH, "better-auth,jobs-api,auth-client", "auth-modal,jobs-search"),
        Vertex("stage-server", "live-stage-server", rich("Vercel + Express", "GET /api/search-jobs", "5 min cache · 256 max · single-flight"), rich("Vercel + Express", "GET /api/search-jobs", "Cache 5 min · maksimum 256 · single-flight"), 770, 125, 330, 285, CARD_SERVER, "live-search-route,express-app,vercel-runtime"),
        Vertex("stage-fanout", "live-stage-fanout", rich("Parallel source fan-out", "7 scrapers + optional Careerjet API", "7 s timeout per source"), rich("Fan-keluar sumber selari", "7 scraper + API Careerjet pilihan", "Had masa 7 s setiap sumber"), 1140, 125, 330, 285, CARD_FANOUT, "live-search-job-sources"),
        Vertex("stage-result", "live-stage-result", rich("Normalize and render", "Sanitize · enrich · merge · filter", "Jobs + sources + health → cards + map"), rich("Normalisasi dan papar", "Sanitasi · perkaya · gabung · tapis", "Kerja + sumber + kesihatan → kad + peta"), 1510, 125, 380, 285, CARD_RESULT, "job-search-relevance,job-entity,job-manager,map-manager,browser", "jobs-cards,jobs-map"),
        Vertex("job-sources", "live-job-sources", "Eight request-time job sources", "Lapan sumber kerja masa permintaan", 1080, 455, 790, 135, SOURCE_GROUP, "live-search-job-sources", role="source-group"),
        Vertex("comparison", "live-comparison", "Live Search versus Daily Index", "Carian Langsung berbanding Indeks Harian", 35, 625, 1210, 230, COMPARISON_FRAME, role="comparison"),
        Vertex("comparison-live", "live-comparison-live", rich("Live Search", "Sign-in required · queries sources now", "Up to 8 upstream requests on cache miss", "5 min per-filter cache + single-flight", "7 s timeout/source · no job-table access"), rich("Carian Langsung", "Log masuk diperlukan · sumber ditanya sekarang", "Sehingga 8 permintaan huluan apabila cache luput", "Cache setiap penapis 5 min + single-flight", "Had masa 7 s/sumber · tiada akses jadual kerja"), 60, 675, 555, 155, COMPARE_LIVE, role="comparison-column"),
        Vertex("comparison-daily", "live-comparison-daily", rich("Daily Index", "Public · last scheduled snapshot", "No upstream request per user search", "60 s serving cache · reads public.scraped_jobs", "Refreshed at 02:00 UTC or manual run"), rich("Indeks Harian", "Awam · snapshot berjadual terakhir", "Tiada permintaan huluan bagi setiap carian", "Cache penyampaian 60 s · baca public.scraped_jobs", "Disegar pada 02:00 UTC atau larian manual"), 640, 675, 575, 155, COMPARE_DAILY, role="comparison-column"),
        Vertex("note-failure", "live-note-failure", rich("Failure behavior", "Partial source failures preserve usable results.", "All-empty or fatal runs fall back to demo jobs.", "Fatal error responses are not cached."), rich("Tingkah laku kegagalan", "Kegagalan separa sumber mengekalkan hasil yang boleh digunakan.", "Larian kosong sepenuhnya atau fatal menggunakan kerja demo.", "Respons ralat fatal tidak dicache."), 1280, 640, 590, 190, NOTE_FAILURE, "live-search-route,live-search-job-sources", role="note"),
    ]
    ids = {vertex.key: add_vertex(root, vertex) for vertex in vertices}

    for number, x in enumerate((30, 400, 770, 1140, 1510), 1):
        add_raw_vertex(root, f"live-number-{number}", str(number), x + 16, 141, 34, 34, NUMBER)

    petakerja = REPOSITORY_ROOT / "public" / "icon" / "android-chrome-192x192.png"
    add_logo(root, "petakerja-request", petakerja, 52, 190, 70, 70)
    add_logo(root, "better-auth", BRANDS / "better-auth.svg", 422, 190)
    add_logo(root, "vercel", BRANDS / "vercel.svg", 790, 194, 58, 58)
    add_logo(root, "express", BRANDS / "express.svg", 870, 194, 58, 58)
    add_logo(root, "typescript", BRANDS / "typescript.svg", 1162, 190)
    add_logo(root, "petakerja-result", petakerja, 1532, 190, 70, 70)

    source_names = ("Maukerja", "Hiredly", "Ricebowl", "Graduan", "Jora", "JobStreet", "Jobstore", "Careerjet")
    source_slugs = ("maukerja", "hiredly", "ricebowl", "graduan", "jora", "jobstreet", "jobstore", "careerjet")
    for index, (name, slug) in enumerate(zip(source_names, source_slugs)):
        x = 1110 + index * 92
        add_logo(root, f"source-{slug}", REPOSITORY_ROOT / "public" / "icons" / "job-sources" / f"{slug}.svg", x, 495, 42, 42, tile=False)
        add_raw_vertex(root, f"live-source-label-{slug}", name, x - 12, 540, 66, 20, SOURCE_LABEL)

    flows = [
        Flow("flow-submit", "live-flow-submit", ids["stage-request"], ids["stage-auth"], "Query + complete filters", "Pertanyaan + penapis lengkap", EDGE_BLUE),
        Flow("flow-session", "live-flow-session", ids["stage-auth"], ids["stage-server"], "Cookie + verified session", "Cookie + sesi disahkan", EDGE_AMBER),
        Flow("flow-cache-miss", "live-flow-cache-miss", ids["stage-server"], ids["stage-fanout"], "Cache miss", "Cache luput", EDGE_ORANGE),
        Flow("flow-fanout", "live-flow-fanout", ids["stage-fanout"], ids["job-sources"], "Concurrent requests", "Permintaan serentak", EDGE_ORANGE, ((1305, 435),)),
        Flow("flow-results", "live-flow-results", ids["job-sources"], ids["stage-result"], "Partial results allowed", "Hasil separa dibenarkan", EDGE_TEAL, ((1700, 610), (1880, 610), (1880, 430))),
        Flow("flow-bypass", "live-flow-bypass", ids["stage-server"], ids["stage-result"], "Cache hit / join single-flight", "Cache ditemui / sertai single-flight", EDGE_BYPASS, ((935, 435), (1040, 605), (1670, 605), (1670, 430))),
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
        raise ValueError("Live Search canvas must be exactly 1920 x 900")
    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if len(keys) != len(set(keys)) or not all(keys):
        raise ValueError("Live Search component keys must be present and unique")
    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            raise ValueError(f"{wrapper.get('id')} is missing bilingual labels")
    edges = [wrapper for wrapper in wrappers if (cell := wrapper.find("mxCell")) is not None and cell.get("edge") == "1"]
    if len(edges) != 6:
        raise ValueError(f"Expected 6 connected flows, found {len(edges)}")
    image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
    if len(image_cells) != 14:
        raise ValueError(f"Expected 14 embedded logos, found {len(image_cells)}")
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
