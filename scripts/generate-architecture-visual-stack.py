#!/usr/bin/env python3
"""Generate the editable bilingual PetaKerja logo-based architecture stack."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import html
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "assets" / "editor" / "architecture-visual-stack.drawio"
BRANDS = ROOT / "assets" / "brands"
DIAGRAM_ID = "architecture-visual-stack"
PAGE_ID = "petakerja_layered_architecture_visual_stack"
PAGE_WIDTH = 1920
PAGE_HEIGHT = 900

TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=28;fontStyle=1;fontColor=light-dark(#172033,#edf2fb);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=13;fontColor=light-dark(#667085,#aeb8c8);"
TIER = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;strokeWidth=1.5;fontColor=light-dark(#172033,#edf2fb);fontFamily=Arial;fontSize=15;align=left;verticalAlign=top;spacingTop=18;spacingLeft=450;spacingRight=22;shadow=0;"
TIER_VIEW = TIER + "fillColor=light-dark(#eef5ff,#17243a);strokeColor=light-dark(#4b79b8,#7eabe6);"
TIER_CONTROLLER = TIER + "fillColor=light-dark(#f5f1ff,#251d35);strokeColor=light-dark(#8065ad,#b093df);"
TIER_SERVICE = TIER + "fillColor=light-dark(#fff8e8,#2b2518);strokeColor=light-dark(#c18a2d,#d8a74d);"
TIER_API = TIER + "fillColor=light-dark(#f4f5f7,#1d2229);strokeColor=light-dark(#697386,#aab3c2);"
TIER_DATA = TIER + "fillColor=light-dark(#edf9f4,#172c27);strokeColor=light-dark(#2c8d70,#63c1a2);"
NUMBER = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=light-dark(#253858,#4f6591);strokeColor=none;fontColor=#ffffff;fontFamily=Arial;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;"
LOGO_TILE = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=light-dark(#d0d5dd,#667085);strokeWidth=1;shadow=0;"
IMAGE = "shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;strokeColor=none;fillColor=none;"
SMALL_LABEL = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=10;fontColor=light-dark(#475467,#c7d0df);"
MAPPING = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f8fafc,#171c24);strokeColor=light-dark(#b8c4d4,#596579);strokeWidth=1.2;fontColor=light-dark(#344054,#e1e7f0);fontFamily=Arial;fontSize=13;fontStyle=1;align=center;verticalAlign=middle;spacing=12;"
NOTE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f8fafc,#171c24);strokeColor=light-dark(#b8c4d4,#596579);strokeWidth=1.2;fontColor=light-dark(#344054,#e1e7f0);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
NOTE_AMBER = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8e8,#2a2417);strokeColor=light-dark(#d8a441,#b8862d);strokeWidth=1.2;fontColor=light-dark(#5f430d,#fff0c4);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeWidth=1.8;strokeColor=light-dark(#566578,#9faabc);fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
EDGE_RETURN = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeWidth=1.8;dashed=1;dashPattern=7 4;strokeColor=light-dark(#168a83,#55c7be);fontColor=light-dark(#285b50,#bfece0);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);exitX=0;exitY=0.5;entryX=0;entryY=0.5;"


@dataclass(frozen=True)
class Tier:
    key: str
    identifier: str
    simple_en: str
    simple_ms: str
    code_en: str
    code_ms: str
    y: int
    style: str
    node_ids: str
    source_files: str = ""
    routes: str = ""
    tables: str = ""
    hotspots: str = ""


@dataclass(frozen=True)
class Flow:
    key: str
    identifier: str
    source: str
    target: str
    simple_en: str
    simple_ms: str
    code_en: str
    code_ms: str
    style: str = EDGE
    points: tuple[tuple[int, int], ...] = ()


def rich(title: str, detail: str) -> str:
    return f"<b>{html.escape(title)}</b><br>{html.escape(detail)}"


def object_attrs(label_en: str, label_ms: str, key: str, **extra: str) -> dict[str, str]:
    return {
        "label": label_en,
        "labelEn": label_en,
        "labelMs": label_ms,
        "petakerjaKey": f"{DIAGRAM_ID}/{key}",
        **{name: value for name, value in extra.items() if value},
    }


def add_tier(root: ET.Element, spec: Tier) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **object_attrs(
            spec.simple_en,
            spec.simple_ms,
            spec.key,
            simpleLabelEn=spec.simple_en,
            simpleLabelMs=spec.simple_ms,
            codeLabelEn=spec.code_en,
            codeLabelMs=spec.code_ms,
            nodeIds=spec.node_ids,
            sourceFiles=spec.source_files,
            routePaths=spec.routes,
            tableName=spec.tables,
            uiHotspots=spec.hotspots,
            component="1",
            architectureRole="tier",
        ),
    })
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": spec.style})
    ET.SubElement(cell, "mxGeometry", {"x": "180", "y": str(spec.y), "width": "1460", "height": "104", "as": "geometry"})
    return spec.identifier


def add_text_object(root: ET.Element, identifier: str, key: str, label_en: str, label_ms: str, x: int, y: int, width: int, height: int, style: str, role: str) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": identifier,
        **object_attrs(label_en, label_ms, key, architectureRole=role),
    })
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": style})
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return identifier


def add_raw_vertex(root: ET.Element, identifier: str, value: str, x: int, y: int, width: int, height: int, style: str) -> str:
    attrs = {"id": identifier, "value": value, "parent": "1", "vertex": "1", "style": style}
    if value:
        attrs.update({"labelEn": value, "labelMs": value})
    cell = ET.SubElement(root, "mxCell", attrs)
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return identifier


def add_flow(root: ET.Element, spec: Flow) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **object_attrs(
            spec.simple_en,
            spec.simple_ms,
            spec.key,
            simpleLabelEn=spec.simple_en,
            simpleLabelMs=spec.simple_ms,
            codeLabelEn=spec.code_en,
            codeLabelMs=spec.code_ms,
            architectureRole="flow",
        ),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": spec.source, "target": spec.target, "style": spec.style,
    })
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if spec.points:
        points = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in spec.points:
            ET.SubElement(points, "mxPoint", {"x": str(x), "y": str(y)})
    return spec.identifier


def image_data_uri(path: Path) -> str:
    if path.suffix.lower() == ".svg":
        return "data:image/svg+xml," + quote(path.read_text(encoding="utf-8"), safe="")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{path.suffix.lower().lstrip('.')},{encoded}"


def add_logo(root: ET.Element, key: str, path: Path, x: int, y: int, label: str) -> None:
    add_raw_vertex(root, f"avs-logo-tile-{key}", "", x - 5, y - 5, 60, 60, LOGO_TILE)
    add_raw_vertex(root, f"avs-logo-{key}", "", x, y, 50, 50, IMAGE + f"image={image_data_uri(path)};")
    add_raw_vertex(root, f"avs-logo-label-{key}", label, x - 18, y + 56, 86, 16, SMALL_LABEL)


def new_document() -> tuple[ET.Element, ET.Element]:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja Architecture Visual Stack Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaDiagramLabelMode": "simple",
        "petakerjaLayoutStandard": "architecture-visual-stack-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": PAGE_ID, "name": "PetaKerja Architecture Visual Stack"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH), "dy": str(PAGE_HEIGHT), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": str(PAGE_WIDTH), "pageHeight": str(PAGE_HEIGHT),
        "math": "0", "shadow": "0", "background": "light-dark(#fbfcfe,#0b1118)",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return mxfile, root


def build_document() -> ET.Element:
    document, root = new_document()
    add_text_object(root, "avs-title", "title", "PetaKerja Architecture Visual Stack", "Susunan Visual Seni Bina PetaKerja", 50, 18, 1820, 40, TITLE, "title")
    add_text_object(root, "avs-subtitle", "subtitle", "A logo-led view of the real layers and their MVC-inspired responsibilities", "Paparan berlogo bagi lapisan sebenar dan tanggungjawab berinspirasikan MVC", 50, 58, 1820, 24, SUBTITLE, "subtitle")

    tiers = (
        Tier("view", "avs-tier-view", rich("Browser and View", "What users see and interact with"), rich("Pelayar dan View", "Perkara yang dilihat dan digunakan oleh pengguna"), rich("Browser UI", "src/main.ts · MyPetaApp · templates.ts · MapLibre GL JS"), rich("UI pelayar", "src/main.ts · MyPetaApp · templates.ts · MapLibre GL JS"), 105, TIER_VIEW, "browser,index-html,main-ts,ui-templates,maplibre-gl", "index.html,src/main.ts,src/MyPetaApp.ts,src/ui/templates.ts", hotspots="ribbon,map-canvas,contents-pane"),
        Tier("application", "avs-tier-application", rich("Application coordination", "Managers turn UI intent into feature work"), rich("Penyelarasan aplikasi", "Pengurus menukar hasrat UI kepada kerja ciri"), rich("Manager layer", "MyPetaApp · MapManager · JobFinderManager · SearchManager · GeoNavigationManager · AuthManager"), rich("Lapisan pengurus", "MyPetaApp · MapManager · JobFinderManager · SearchManager · GeoNavigationManager · AuthManager"), 219, TIER_CONTROLLER, "mypeta-app,map-manager,poi-manager,search-manager,job-manager,geo-navigation-manager,auth-manager", "src/MyPetaApp.ts,src/managers/MapManager.ts,src/managers/SearchManager.ts,src/managers/GeoNavigationManager.ts,src/modes/jobs/manager.ts", hotspots="map-search,jobs-search,map-canvas"),
        Tier("clients", "avs-tier-clients", rich("Service clients", "Typed clients request application data and same-origin APIs"), rich("Klien perkhidmatan", "Klien berjenis meminta data aplikasi dan API origin sama"), rich("Client modules", "supabase.ts · jobs/api.ts · services/geo.ts · authenticatedFetch()"), rich("Modul klien", "supabase.ts · jobs/api.ts · services/geo.ts · authenticatedFetch()"), 333, TIER_SERVICE, "supabase-module,jobs-api,geo-api,open-data-api,auth-client", "src/services/supabase.ts,src/modes/jobs/api.ts,src/services/geo.ts,src/services/authenticatedFetch.ts", routes="/api/jobs/supa,/api/search-jobs,/api/geo/*"),
        Tier("api", "avs-tier-api", rich("API backend", "Vercel runs Express routes and Better Auth guards"), rich("Bahagian belakang API", "Vercel menjalankan laluan Express dan kawalan Better Auth"), rich("Server boundary", "Vercel Node · server/app.ts · /api/* · requireAuth · route handlers"), rich("Sempadan pelayan", "Vercel Node · server/app.ts · /api/* · requireAuth · pengendali laluan"), 447, TIER_API, "vercel-runtime,express-app,better-auth", "server/app.ts,server/auth/requireAuth.ts,api/index.ts", routes="/api/*"),
        Tier("data", "avs-tier-data", rich("Model, data and external services", "Tables, records, caches and provider data"), rich("Model, data dan perkhidmatan luaran", "Jadual, rekod, cache dan data penyedia"), rich("Data responsibilities", "Supabase PostgreSQL/PostGIS · public.scraped_jobs · public.pois · public.users · api.data.gov.my"), rich("Tanggungjawab data", "Supabase PostgreSQL/PostGIS · public.scraped_jobs · public.pois · public.users · api.data.gov.my"), 561, TIER_DATA, "supabase-db,job-entity,poi-entity,data-gov", tables="scraped_jobs,pois,users,geo_route_cache,geo_geocode_cache"),
    )
    tier_ids = {tier.key: add_tier(root, tier) for tier in tiers}
    for number, tier in enumerate(tiers, 1):
        add_raw_vertex(root, f"avs-number-{number}", str(number), 196, tier.y + 14, 30, 30, NUMBER)

    petakerja = REPOSITORY_ROOT / "public" / "icon" / "android-chrome-192x192.png"
    logo_rows = (
        (("petakerja", petakerja, "PetaKerja"), ("vite", BRANDS / "vite.svg", "Vite"), ("typescript-view", BRANDS / "typescript.svg", "TypeScript"), ("maplibre", BRANDS / "maplibre.svg", "MapLibre")),
        (("typescript-app", BRANDS / "typescript.svg", "TypeScript"),),
        (("supabase-client", BRANDS / "supabase.svg", "Supabase"),),
        (("vercel", BRANDS / "vercel.svg", "Vercel"), ("express", BRANDS / "express.svg", "Express"), ("better-auth", BRANDS / "better-auth.svg", "Better Auth")),
        (("supabase-data", BRANDS / "supabase.svg", "Supabase"), ("postgresql", BRANDS / "postgresql.svg", "PostgreSQL")),
    )
    for tier, logos in zip(tiers, logo_rows):
        start_x = 250
        if len(logos) == 4:
            start_x = 230
        elif len(logos) == 3:
            start_x = 250
        elif len(logos) == 2:
            start_x = 290
        for index, (key, path, label) in enumerate(logos):
            add_logo(root, key, path, start_x + index * 92, tier.y + 13, label)

    add_text_object(root, "avs-mvc-view", "mvc-view", "VIEW", "VIEW", 1665, 105, 205, 104, MAPPING, "mvc-mapping")
    add_text_object(root, "avs-mvc-controller", "mvc-controller", "CONTROLLER-LIKE\ncoordination", "PENYELARASAN\nSEPERTI CONTROLLER", 1665, 219, 205, 332, MAPPING, "mvc-mapping")
    add_text_object(root, "avs-mvc-model", "mvc-model", "MODEL / DATA", "MODEL / DATA", 1665, 561, 205, 104, MAPPING, "mvc-mapping")

    flows = (
        Flow("flow-interaction", "avs-flow-interaction", tier_ids["view"], tier_ids["application"], "User intent enters the application", "Hasrat pengguna memasuki aplikasi", "DOM events → MyPetaApp / managers", "Peristiwa DOM → MyPetaApp / pengurus"),
        Flow("flow-manager", "avs-flow-manager", tier_ids["application"], tier_ids["clients"], "Managers request data and capabilities", "Pengurus meminta data dan keupayaan", "manager methods → typed service clients", "kaedah pengurus → klien perkhidmatan berjenis"),
        Flow("flow-api", "avs-flow-api", tier_ids["clients"], tier_ids["api"], "Same-origin requests cross the API boundary", "Permintaan origin sama merentasi sempadan API", "fetch('/api/*') → Express", "fetch('/api/*') → Express"),
        Flow("flow-data", "avs-flow-data", tier_ids["api"], tier_ids["data"], "Routes and services read data or providers", "Laluan dan perkhidmatan membaca data atau penyedia", "handlers / services → Supabase / providers", "pengendali / perkhidmatan → Supabase / penyedia"),
        Flow("flow-return", "avs-flow-return", tier_ids["data"], tier_ids["view"], "Normalized results return to the interface", "Hasil ternormal kembali ke antara muka", "JSON / rows / GeoJSON → cards, panels and renderers", "JSON / baris / GeoJSON → kad, panel dan pemapar", EDGE_RETURN, ((120, 613), (120, 157))),
    )
    for flow in flows:
        add_flow(root, flow)

    add_text_object(root, "avs-note-mvc", "note-mvc", rich("MVC-inspired, not strict MVC", "Managers combine controller-like coordination, UI state and some direct DOM updates."), rich("Berinspirasikan MVC, bukan MVC ketat", "Pengurus menggabungkan penyelarasan seperti controller, keadaan UI dan beberapa kemas kini DOM secara terus."), 180, 705, 900, 120, NOTE_AMBER, "note")
    add_text_object(root, "avs-note-reading", "note-reading", rich("How to read this stack", "Logos identify the technologies; select a tier for exact source files, routes, tables and UI hotspots."), rich("Cara membaca susunan ini", "Logo mengenal pasti teknologi; pilih lapisan untuk fail sumber, laluan, jadual dan titik panas UI yang tepat."), 1100, 705, 770, 120, NOTE, "note")
    return document


def validate(document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise ValueError(f"missing page {PAGE_ID}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(PAGE_WIDTH), str(PAGE_HEIGHT)):
        raise ValueError("canvas must be exactly 1920 x 900")
    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if not all(keys) or len(keys) != len(set(keys)):
        raise ValueError("component keys must be present and unique")
    tiers = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "tier"]
    flows = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "flow"]
    if len(tiers) != 5 or len(flows) != 5:
        raise ValueError("visual stack must contain exactly five tiers and five flows")
    for wrapper in (*tiers, *flows):
        required = ("labelEn", "labelMs", "simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs")
        if any(not wrapper.get(name) for name in required):
            raise ValueError(f"{wrapper.get('id')} is missing bilingual label-mode metadata")
    images = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
    if len(images) != 11:
        raise ValueError(f"expected 11 embedded logos, found {len(images)}")
    vertices = {
        wrapper.get("id", "") for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    for wrapper in flows:
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("source") not in vertices or cell.get("target") not in vertices:
            raise ValueError(f"{wrapper.get('id')} has a disconnected endpoint")
    for cell in diagram.findall(".//mxCell"):
        style = cell.get("style", "")
        if "shape=image" in style and ("image=data:image/" not in style or "image=http" in style):
            raise ValueError(f"{cell.get('id')} does not use an embedded local image")
        if "gradientColor=" in style:
            raise ValueError(f"{cell.get('id')} uses a forbidden gradient")


def main() -> None:
    document = build_document()
    validate(document)
    ET.indent(document, space="  ")
    ET.ElementTree(document).write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
