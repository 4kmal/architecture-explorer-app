#!/usr/bin/env python3
"""Generate the four editable bilingual Map & Routing workflow explainers."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import html
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT_DIR = ROOT / "assets" / "editor" / "map-routing"
BRANDS = ROOT / "assets" / "brands"
PAGE_WIDTH = 1920
PAGE_HEIGHT = 900

DIAGRAMS = {
    "nominatim-valhalla-workflow": "petakerja_nominatim_valhalla_workflow",
    "nominatim-maplibre-workflow": "petakerja_nominatim_maplibre_workflow",
    "valhalla-maplibre-workflow": "petakerja_valhalla_maplibre_workflow",
    "geo-server-communication-workflow": "petakerja_geo_server_communication_workflow",
}

TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=28;fontStyle=1;fontColor=light-dark(#172033,#edf2fb);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=13;fontColor=light-dark(#667085,#aeb8c8);"
CARD = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1b2029);strokeWidth=1.6;fontColor=light-dark(#172033,#edf2fb);fontFamily=Arial;fontSize=14;align=left;verticalAlign=top;spacingTop=132;spacingLeft=20;spacingRight=16;shadow=1;"
CARD_BLUE = CARD + "strokeColor=light-dark(#285daa,#82b5f5);"
CARD_PURPLE = CARD + "strokeColor=light-dark(#7256a8,#ad91e0);"
CARD_PURPLE_GATED = CARD_PURPLE + "dashed=1;dashPattern=7 4;"
CARD_TEAL = CARD + "strokeColor=light-dark(#168a83,#55c7be);"
CARD_NEUTRAL = CARD + "strokeColor=light-dark(#59636f,#aeb8c8);"
CARD_CYAN = CARD + "strokeColor=light-dark(#1687a7,#5fc7e6);"
CARD_AMBER = CARD + "strokeColor=light-dark(#c58a22,#e0ad4f);"
NUMBER = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=light-dark(#253858,#4f6591);strokeColor=none;fontColor=#ffffff;fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=middle;"
LOGO_TILE = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=light-dark(#d0d5dd,#667085);strokeWidth=1;shadow=0;"
IMAGE = "shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;strokeColor=none;fillColor=none;"
PANEL = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f8fafc,#171c24);strokeColor=light-dark(#b8c4d4,#596579);strokeWidth=1.2;fontColor=light-dark(#344054,#e1e7f0);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
NOTE_AMBER = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8e8,#2a2417);strokeColor=light-dark(#d8a441,#b8862d);strokeWidth=1.2;fontColor=light-dark(#5f430d,#fff0c4);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
NOTE_BLUE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#eef4ff,#182338);strokeColor=light-dark(#7ea6df,#5e83ba);strokeWidth=1.2;fontColor=light-dark(#17375e,#e8f1ff);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
NOTE_PURPLE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f6f1ff,#241d31);strokeColor=light-dark(#9a7bc6,#a98cda);strokeWidth=1.2;fontColor=light-dark(#4b3370,#efe5ff);fontFamily=Arial;fontSize=13;align=left;verticalAlign=middle;spacing=16;"
SMALL_LABEL = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=10;fontColor=light-dark(#475467,#c7d0df);"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeWidth=1.8;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
EDGE_BLUE = EDGE + "strokeColor=light-dark(#285daa,#82b5f5);"
EDGE_PURPLE = EDGE + "strokeColor=light-dark(#7256a8,#ad91e0);"
EDGE_TEAL = EDGE + "strokeColor=light-dark(#168a83,#55c7be);"
EDGE_CYAN = EDGE + "strokeColor=light-dark(#1687a7,#5fc7e6);"
EDGE_AMBER = EDGE + "strokeColor=light-dark(#c58a22,#e0ad4f);"
EDGE_DASHED = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#7f8a9a,#8d99aa);"
EDGE_FUTURE = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#7256a8,#ad91e0);"


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
    tables: str = ""
    hotspots: str = ""
    source_files: str = ""
    routes: str = ""
    role: str = "stage"
    status: str = "current"


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
    status: str = "current"


def rich(title: str, *lines: str) -> str:
    return f"<b>{html.escape(title)}</b>" + ("<br>" + "<br>".join(html.escape(line) for line in lines) if lines else "")


def object_attrs(prefix: str, label_en: str, label_ms: str, key: str, **extra: str) -> dict[str, str]:
    return {
        "label": label_en,
        "labelEn": label_en,
        "labelMs": label_ms,
        "petakerjaKey": f"{prefix}/{key}",
        **{name: value for name, value in extra.items() if value},
    }


def add_vertex(root: ET.Element, prefix: str, spec: Vertex) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **object_attrs(
            prefix, spec.label_en, spec.label_ms, spec.key,
            nodeIds=spec.node_ids, tableName=spec.tables, uiHotspots=spec.hotspots,
            sourceFiles=spec.source_files, routePaths=spec.routes,
            workflowRole=spec.role, workflowStatus=spec.status,
            component="1" if spec.node_ids else "",
        ),
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
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return identifier


def add_flow(root: ET.Element, prefix: str, spec: Flow) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **object_attrs(prefix, spec.label_en, spec.label_ms, spec.key, workflowRole="flow", workflowStatus=spec.status),
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
    # mxGraph styles use semicolons as property delimiters, so Draw.io expects
    # raster data URIs in this style-safe form rather than `;base64,...`.
    return f"data:image/{path.suffix.lower().lstrip('.')},{encoded}"


def add_logo(root: ET.Element, prefix: str, key: str, path: Path, x: int, y: int, width: int = 64, height: int = 64, label: str = "") -> None:
    add_raw_vertex(root, f"{prefix}-logo-tile-{key}", "", x - 6, y - 6, width + 12, height + 12, LOGO_TILE)
    add_raw_vertex(root, f"{prefix}-logo-{key}", "", x, y, width, height, IMAGE + f"image={image_data_uri(path)};")
    if label:
        add_raw_vertex(root, f"{prefix}-logo-label-{key}", label, x - 22, y + height + 5, width + 44, 20, SMALL_LABEL)


def new_document(diagram_id: str, title: str) -> tuple[ET.Element, ET.Element]:
    page_id = DIAGRAMS[diagram_id]
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja Map Routing Workflow Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaLayoutStandard": "map-routing-workflows-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": page_id, "name": title})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH), "dy": str(PAGE_HEIGHT), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": str(PAGE_WIDTH), "pageHeight": str(PAGE_HEIGHT),
        "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return mxfile, root


def add_header(root: ET.Element, prefix: str, title_en: str, title_ms: str, subtitle_en: str, subtitle_ms: str) -> None:
    add_vertex(root, prefix, Vertex("title", f"{prefix}-title", title_en, title_ms, 50, 20, 1820, 42, TITLE, role="title"))
    add_vertex(root, prefix, Vertex("subtitle", f"{prefix}-subtitle", subtitle_en, subtitle_ms, 50, 64, 1820, 26, SUBTITLE, role="subtitle"))


def add_numbered_stages(root: ET.Element, prefix: str, stages: list[Vertex]) -> dict[str, str]:
    ids = {stage.key: add_vertex(root, prefix, stage) for stage in stages}
    for number, stage in enumerate(stages, 1):
        add_raw_vertex(root, f"{prefix}-number-{number}", str(number), stage.x + 16, stage.y + 16, 34, 34, NUMBER)
    return ids


def petakerja_logo() -> Path:
    return REPOSITORY_ROOT / "public" / "icon" / "android-chrome-192x192.png"


def build_nominatim_valhalla() -> ET.Element:
    diagram_id = "nominatim-valhalla-workflow"
    prefix = diagram_id
    document, root = new_document(diagram_id, "Nominatim + Valhalla Workflow")
    add_header(root, prefix, "Nominatim + Valhalla Workflow", "Aliran Kerja Nominatim + Valhalla", "Nominatim finds coordinates; Valhalla routes between them through separate GeoGateway calls", "Nominatim mencari koordinat; Valhalla menghala antaranya melalui panggilan GeoGateway berasingan")
    stages = [
        Vertex("stage-input", "nv-stage-input", rich("Choose places or points", "Search an address, use GPS or drop a pin", "Set route start A and destination B"), rich("Pilih tempat atau titik", "Cari alamat, guna GPS atau jatuhkan pin", "Tetapkan mula A dan destinasi B"), 30, 125, 330, 285, CARD_BLUE, "browser,search-manager,maplibre-gl", hotspots="map-search,map-canvas", source_files="src/managers/SearchManager.ts,src/managers/GeoNavigationManager.ts"),
        Vertex("stage-nominatim", "nv-stage-nominatim", rich("Geocode with Nominatim", "GET /api/geo/search · reverse · lookup", "GeoGateway + geo_geocode_cache"), rich("Geokod dengan Nominatim", "GET /api/geo/search · reverse · lookup", "GeoGateway + geo_geocode_cache"), 400, 125, 330, 285, CARD_PURPLE_GATED, "geo-api,geo-gateway,nominatim,geo-geocode-cache", "geo_geocode_cache", "map-search", "src/services/geo.ts,server/routes/geo.ts,server/geo/gateway.ts", "/api/geo/search,/api/geo/reverse,/api/geo/lookup", status="gated"),
        Vertex("stage-coordinates", "nv-stage-coordinates", rich("Assign A/B coordinates", "GeoPlace → latitude + longitude", "GeoNavigationManager stores the endpoints"), rich("Tetapkan koordinat A/B", "GeoPlace → latitud + longitud", "GeoNavigationManager menyimpan titik hujung"), 770, 125, 330, 285, CARD_BLUE, "geo-navigation-manager,geo-location", hotspots="map-canvas", source_files="src/managers/GeoNavigationManager.ts,src/geo/contracts.ts"),
        Vertex("stage-valhalla", "nv-stage-valhalla", rich("Route with Valhalla", "POST /api/geo/route", "GeoGateway + geo_route_cache"), rich("Halakan dengan Valhalla", "POST /api/geo/route", "GeoGateway + geo_route_cache"), 1140, 125, 330, 285, CARD_TEAL, "geo-api,geo-gateway,valhalla,geo-route-cache", "geo_route_cache", "map-canvas", "src/services/geo.ts,server/routes/geo.ts,server/geo/gateway.ts", "/api/geo/route"),
        Vertex("stage-result", "nv-stage-result", rich("Return a normalized route", "GeoJSON · distance · ETA · maneuvers", "Ready for GeoRouteRenderer + MapLibre"), rich("Pulangkan laluan ternormal", "GeoJSON · jarak · ETA · arahan", "Sedia untuk GeoRouteRenderer + MapLibre"), 1510, 125, 380, 285, CARD_TEAL, "geo-route,geo-route-renderer,maplibre-gl", hotspots="map-canvas", source_files="src/managers/GeoRouteRenderer.ts,src/geo/contracts.ts"),
    ]
    ids = add_numbered_stages(root, prefix, stages)
    add_logo(root, prefix, "petakerja", petakerja_logo(), 54, 194, 68, 68)
    add_logo(root, prefix, "nominatim", BRANDS / "openstreetmap.svg", 424, 194, label="Nominatim")
    add_logo(root, prefix, "typescript", BRANDS / "typescript.svg", 794, 194)
    add_logo(root, prefix, "valhalla", BRANDS / "valhalla.svg", 1164, 190, 72, 72)
    add_logo(root, prefix, "maplibre", BRANDS / "maplibre.svg", 1534, 190, 72, 72)
    control = Vertex("control-plane", "nv-control-plane", rich("Shared control plane", "Vercel + Express validate both requests; Supabase caches geocoding and routing independently."), rich("Kawalan bersama", "Vercel + Express mengesahkan kedua-dua permintaan; Supabase mencache geokod dan penghalaan secara berasingan."), 50, 505, 800, 125, PANEL, "vercel-runtime,express-app,geo-gateway,supabase-db", "geo_geocode_cache,geo_route_cache", source_files="vercel.json,server/app.ts,server/routes/geo.ts,server/geo/gateway.ts", role="support")
    add_vertex(root, prefix, control)
    add_logo(root, prefix, "vercel", BRANDS / "vercel.svg", 470, 530, 46, 46, "Vercel")
    add_logo(root, prefix, "express", BRANDS / "express.svg", 565, 530, 46, 46, "Express")
    add_logo(root, prefix, "supabase", BRANDS / "supabase.svg", 660, 530, 46, 46, "Supabase")
    add_vertex(root, prefix, Vertex("note-separation", "nv-note-separation", rich("Important boundary", "Nominatim and Valhalla never call each other.", "The selected coordinates connect their responsibilities."), rich("Sempadan penting", "Nominatim dan Valhalla tidak pernah saling memanggil.", "Koordinat yang dipilih menghubungkan tanggungjawab mereka."), 890, 490, 980, 140, NOTE_BLUE, "nominatim,valhalla,geo-navigation-manager", role="note"))
    add_vertex(root, prefix, Vertex("note-status", "nv-note-status", rich("Current status", "Valhalla routing is live on the pilot VPS. Nominatim remains feature-gated and disabled."), rich("Status semasa", "Penghalaan Valhalla aktif pada VPS rintis. Nominatim kekal berpagar ciri dan dinyahaktifkan."), 50, 675, 890, 135, NOTE_PURPLE, "digitalocean-geo-host,valhalla,nominatim", role="note", status="gated"))
    add_vertex(root, prefix, Vertex("note-fallback", "nv-note-fallback", rich("When Nominatim is unavailable", "GPS, a manual coordinate or a dropped pin can still supply A/B coordinates to Valhalla."), rich("Apabila Nominatim tidak tersedia", "GPS, koordinat manual atau pin yang dijatuhkan masih boleh membekalkan koordinat A/B kepada Valhalla."), 980, 675, 890, 135, NOTE_AMBER, "geo-navigation-manager,valhalla", hotspots="map-canvas", role="note"))
    flows = [
        Flow("flow-search", "nv-flow-search", ids["stage-input"], ids["stage-nominatim"], "Gated place/address query", "Pertanyaan tempat/alamat berpagar", EDGE_FUTURE, status="gated"),
        Flow("flow-place", "nv-flow-place", ids["stage-nominatim"], ids["stage-coordinates"], "Gated GeoPlace + coordinates", "GeoPlace + koordinat berpagar", EDGE_FUTURE, status="gated"),
        Flow("flow-route", "nv-flow-route", ids["stage-coordinates"], ids["stage-valhalla"], "A/B + travel profile", "A/B + profil perjalanan", EDGE_TEAL),
        Flow("flow-result", "nv-flow-result", ids["stage-valhalla"], ids["stage-result"], "Normalized GeoRoute", "GeoRoute ternormal", EDGE_TEAL),
        Flow("flow-coordinate-bypass", "nv-flow-coordinate-bypass", ids["stage-input"], ids["stage-coordinates"], "GPS / manual / dropped pin", "GPS / manual / pin dijatuhkan", EDGE_DASHED, ((195, 445), (935, 445))),
    ]
    for flow in flows:
        add_flow(root, prefix, flow)
    return document


def build_nominatim_maplibre() -> ET.Element:
    diagram_id = "nominatim-maplibre-workflow"
    prefix = diagram_id
    document, root = new_document(diagram_id, "Nominatim + MapLibre Workflow")
    add_header(root, prefix, "Nominatim + MapLibre Workflow", "Aliran Kerja Nominatim + MapLibre", "Nominatim supplies place data; MapLibre displays and interacts with it", "Nominatim membekalkan data tempat; MapLibre memapar dan berinteraksi dengannya")
    stages = [
        Vertex("stage-map-input", "nm-stage-map-input", rich("MapLibre input", "Type a query, move the viewport or drop a pin", "The map supplies viewbox or coordinates"), rich("Input MapLibre", "Taip pertanyaan, gerakkan viewport atau jatuhkan pin", "Peta membekalkan viewbox atau koordinat"), 30, 125, 330, 285, CARD_BLUE, "browser,maplibre-gl,map-manager", hotspots="map-search,map-canvas", source_files="src/managers/MapManager.ts,src/managers/GeoNavigationManager.ts"),
        Vertex("stage-search", "nm-stage-search", rich("SearchManager coordinates", "Debounce + stale-request protection", "Run PetaKerja POI and geo searches"), rich("SearchManager menyelaras", "Debounce + perlindungan permintaan lapuk", "Jalankan carian POI PetaKerja dan geo"), 400, 125, 330, 285, CARD_BLUE, "search-manager,geo-service,supabase-module", "pois", "map-search", "src/managers/SearchManager.ts,src/services/geo.ts,src/services/supabase.ts", "/api/geo/search,RPC search_pois"),
        Vertex("stage-nominatim", "nm-stage-nominatim", rich("GeoGateway → Nominatim", "GET /api/geo/search · reverse · lookup", "Check geo_geocode_cache before provider"), rich("GeoGateway → Nominatim", "GET /api/geo/search · reverse · lookup", "Semak geo_geocode_cache sebelum penyedia"), 770, 125, 330, 285, CARD_PURPLE_GATED, "vercel-runtime,express-app,geo-api,geo-gateway,nominatim,geo-geocode-cache", "geo_geocode_cache", "map-search,map-canvas", "vercel.json,server/app.ts,server/routes/geo.ts,server/geo/gateway.ts", "/api/geo/search,/api/geo/reverse,/api/geo/lookup", status="gated"),
        Vertex("stage-merge", "nm-stage-merge", rich("Normalize and merge", "GeoPlace + public.pois results", "Deduplicate; PetaKerja records win"), rich("Normalisasi dan gabung", "GeoPlace + hasil public.pois", "Buang pendua; rekod PetaKerja diutamakan"), 1140, 125, 330, 285, CARD_CYAN, "search-manager,geo-place,poi-entity", "pois", "map-search", "src/managers/SearchManager.ts,src/geo/contracts.ts"),
        Vertex("stage-render", "nm-stage-render", rich("MapLibre displays the place", "flyTo · A/B markers · readable labels", "Optional boundary + POIs within area"), rich("MapLibre memaparkan tempat", "flyTo · marker A/B · label mudah dibaca", "Sempadan pilihan + POI dalam kawasan"), 1510, 125, 380, 285, CARD_BLUE, "maplibre-gl,map-manager,geo-navigation-manager,geo-route-renderer", hotspots="map-search,map-canvas", source_files="src/managers/MapManager.ts,src/managers/GeoNavigationManager.ts,src/managers/GeoRouteRenderer.ts", routes="/api/geo/within"),
    ]
    ids = add_numbered_stages(root, prefix, stages)
    add_logo(root, prefix, "maplibre-input", BRANDS / "maplibre.svg", 54, 190, 72, 72)
    add_logo(root, prefix, "typescript", BRANDS / "typescript.svg", 424, 194)
    add_logo(root, prefix, "nominatim", BRANDS / "openstreetmap.svg", 794, 194, label="Nominatim")
    add_logo(root, prefix, "petakerja", petakerja_logo(), 1164, 192, 68, 68)
    add_logo(root, prefix, "maplibre-result", BRANDS / "maplibre.svg", 1534, 190, 72, 72)
    poi_panel = Vertex("source-pois", "nm-source-pois", rich("First-party source: public.pois", "searchPOIs() runs independently through Supabase and remains available when Nominatim is off."), rich("Sumber pihak pertama: public.pois", "searchPOIs() berjalan berasingan melalui Supabase dan kekal tersedia apabila Nominatim dimatikan."), 80, 510, 750, 130, PANEL, "supabase-module,supabase-db,poi-entity", "pois", "map-search", "src/services/supabase.ts,src/managers/SearchManager.ts", "RPC search_pois", role="source")
    add_vertex(root, prefix, poi_panel)
    add_logo(root, prefix, "supabase", BRANDS / "supabase.svg", 660, 535, 48, 48, "Supabase")
    add_vertex(root, prefix, Vertex("note-boundary", "nm-note-boundary", rich("Important boundary", "MapLibre never calls Nominatim directly.", "It receives normalized place data from the same-origin API."), rich("Sempadan penting", "MapLibre tidak pernah memanggil Nominatim secara terus.", "Ia menerima data tempat ternormal daripada API same-origin."), 880, 500, 990, 140, NOTE_BLUE, "maplibre-gl,geo-api,geo-gateway,nominatim", role="note"))
    add_vertex(root, prefix, Vertex("note-status", "nm-note-status", rich("Current status", "Nominatim is implemented but disabled. MapLibre, internal POIs and local dropped-pin labels continue to work."), rich("Status semasa", "Nominatim telah dilaksanakan tetapi dinyahaktifkan. MapLibre, POI dalaman dan label pin lokal terus berfungsi."), 80, 690, 1790, 120, NOTE_PURPLE, "nominatim,maplibre-gl,search-manager,poi-entity", "pois", "map-search,map-canvas", role="note", status="gated"))
    flows = [
        Flow("flow-input", "nm-flow-input", ids["stage-map-input"], ids["stage-search"], "Query + viewbox / coordinate", "Pertanyaan + viewbox / koordinat", EDGE_BLUE),
        Flow("flow-geocode", "nm-flow-geocode", ids["stage-search"], ids["stage-nominatim"], "Gated same-origin geo request", "Permintaan geo same-origin berpagar", EDGE_FUTURE, status="gated"),
        Flow("flow-place", "nm-flow-place", ids["stage-nominatim"], ids["stage-merge"], "Gated normalized GeoPlace[]", "GeoPlace[] ternormal berpagar", EDGE_FUTURE, status="gated"),
        Flow("flow-render", "nm-flow-render", ids["stage-merge"], ids["stage-render"], "Selected coordinates + bounds", "Koordinat + sempadan dipilih", EDGE_BLUE),
        Flow("flow-poi-request", "nm-flow-poi-request", ids["stage-search"], "nm-source-pois", "searchPOIs()", "searchPOIs()", EDGE_CYAN, ((565, 445), (455, 475))),
        Flow("flow-poi-merge", "nm-flow-poi-merge", "nm-source-pois", ids["stage-merge"], "First-party results", "Hasil pihak pertama", EDGE_CYAN, ((1000, 660), (1305, 660), (1305, 430))),
    ]
    for flow in flows:
        add_flow(root, prefix, flow)
    return document


def build_valhalla_maplibre() -> ET.Element:
    diagram_id = "valhalla-maplibre-workflow"
    prefix = diagram_id
    document, root = new_document(diagram_id, "Valhalla + MapLibre Workflow")
    add_header(root, prefix, "Valhalla + MapLibre Workflow", "Aliran Kerja Valhalla + MapLibre", "Valhalla calculates the road route; MapLibre renders the returned GeoJSON", "Valhalla mengira laluan jalan; MapLibre memaparkan GeoJSON yang dipulangkan")
    stages = [
        Vertex("stage-input", "vm-stage-input", rich("Choose A/B + profile", "Driving · walking · cycling", "GeoNavigationManager owns the interaction"), rich("Pilih A/B + profil", "Memandu · berjalan · berbasikal", "GeoNavigationManager mengawal interaksi"), 30, 125, 330, 285, CARD_BLUE, "browser,maplibre-gl,geo-navigation-manager", hotspots="map-canvas", source_files="src/managers/GeoNavigationManager.ts"),
        Vertex("stage-api", "vm-stage-api", rich("Same-origin geo request", "POST /api/geo/route", "Vercel + Express validate and rate-limit"), rich("Permintaan geo same-origin", "POST /api/geo/route", "Vercel + Express mengesah dan mengehad kadar"), 400, 125, 330, 285, CARD_NEUTRAL, "vercel-runtime,express-app,geo-api,geo-gateway", hotspots="map-canvas", source_files="vercel.json,api/server.ts,server/app.ts,server/routes/geo.ts", routes="/api/geo/route"),
        Vertex("stage-provider", "vm-stage-provider", rich("Protected Valhalla origin", "HTTPS geo.petakerja.my/valhalla/route", "Caddy → private Docker port 8002"), rich("Origin Valhalla terlindung", "HTTPS geo.petakerja.my/valhalla/route", "Caddy → port Docker peribadi 8002"), 770, 125, 330, 285, CARD_TEAL, "digitalocean-geo-host,caddy-geo-edge,geo-docker-network,valhalla", hotspots="map-canvas", source_files="infra/geo/compose.routing.yaml,infra/geo/Caddy.routing,infra/geo/README.md", routes="https://geo.petakerja.my/valhalla/route"),
        Vertex("stage-normalize", "vm-stage-normalize", rich("Normalize GeoRoute", "Decode polyline6 → GeoJSON", "Distance · duration · maneuvers · alternatives"), rich("Normalisasi GeoRoute", "Nyahkod polyline6 → GeoJSON", "Jarak · tempoh · arahan · alternatif"), 1140, 125, 330, 285, CARD_CYAN, "geo-gateway,geo-route,geo-route-alternative,geo-maneuver", "geo_route_cache", source_files="server/geo/gateway.ts,server/geo/normalize.ts,src/geo/contracts.ts"),
        Vertex("stage-render", "vm-stage-render", rich("Render with MapLibre", "GeoRouteRenderer adds sources + layers", "Routes · markers · labels · camera · preview"), rich("Papar dengan MapLibre", "GeoRouteRenderer menambah source + layer", "Laluan · marker · label · kamera · pratonton"), 1510, 125, 380, 285, CARD_BLUE, "geo-route-renderer,maplibre-gl,route-appearance-manager", hotspots="map-canvas", source_files="src/managers/GeoRouteRenderer.ts,src/managers/RouteAppearanceManager.ts"),
    ]
    ids = add_numbered_stages(root, prefix, stages)
    add_logo(root, prefix, "maplibre-input", BRANDS / "maplibre.svg", 54, 190, 72, 72)
    add_logo(root, prefix, "vercel", BRANDS / "vercel.svg", 424, 194)
    add_logo(root, prefix, "valhalla", BRANDS / "valhalla.svg", 794, 190, 72, 72)
    add_logo(root, prefix, "typescript", BRANDS / "typescript.svg", 1164, 194)
    add_logo(root, prefix, "maplibre-result", BRANDS / "maplibre.svg", 1534, 190, 72, 72)
    cache = Vertex("route-cache", "vm-route-cache", rich("Supabase route cache", "geo_route_cache stores normalized route, matrix and isochrone payloads for six hours."), rich("Cache laluan Supabase", "geo_route_cache menyimpan payload laluan, matriks dan isokron ternormal selama enam jam."), 80, 500, 720, 135, PANEL, "supabase-db,geo-route-cache,geo-gateway", "geo_route_cache", source_files="server/geo/gateway.ts,supabase/migrations/20260718011925_geo_gateway_routing_and_studio.sql", role="cache")
    add_vertex(root, prefix, cache)
    add_logo(root, prefix, "supabase", BRANDS / "supabase.svg", 630, 528, 48, 48, "Supabase")
    add_vertex(root, prefix, Vertex("note-boundary", "vm-note-boundary", rich("Important boundary", "MapLibre is the visualizer, not the routing engine.", "It receives already-calculated GeoJSON from Valhalla through GeoGateway."), rich("Sempadan penting", "MapLibre ialah pemapar, bukan enjin penghalaan.", "Ia menerima GeoJSON yang telah dikira oleh Valhalla melalui GeoGateway."), 850, 495, 1020, 140, NOTE_BLUE, "maplibre-gl,valhalla,geo-gateway", role="note"))
    add_vertex(root, prefix, Vertex("note-fallback", "vm-note-fallback", rich("Routing fallback", "If Valhalla is disabled or unavailable, return a labelled Haversine straight-line estimate: no ETA, no maneuvers and no navigable-route claim."), rich("Sandaran penghalaan", "Jika Valhalla dinyahaktifkan atau tidak tersedia, pulangkan anggaran garis lurus Haversine berlabel: tiada ETA, tiada arahan dan tiada dakwaan laluan navigasi."), 80, 690, 1790, 120, NOTE_AMBER, "geo-gateway,geo-navigation-manager,maplibre-gl", hotspots="map-canvas", role="note"))
    flows = [
        Flow("flow-request", "vm-flow-request", ids["stage-input"], ids["stage-api"], "A/B + profile", "A/B + profil", EDGE_BLUE),
        Flow("flow-provider", "vm-flow-provider", ids["stage-api"], ids["stage-provider"], "Cache miss · bearer token", "Cache luput · token bearer", EDGE_TEAL),
        Flow("flow-response", "vm-flow-response", ids["stage-provider"], ids["stage-normalize"], "Encoded route response", "Respons laluan berkod", EDGE_TEAL),
        Flow("flow-render", "vm-flow-render", ids["stage-normalize"], ids["stage-render"], "Normalized GeoJSON", "GeoJSON ternormal", EDGE_BLUE),
        Flow("flow-cache-read", "vm-flow-cache-read", ids["stage-api"], "vm-route-cache", "Cache key lookup", "Carian kunci cache", EDGE_CYAN, ((565, 445), (440, 470))),
        Flow("flow-cache-hit", "vm-flow-cache-hit", "vm-route-cache", ids["stage-normalize"], "Fresh cached GeoRoute", "GeoRoute cache segar", EDGE_CYAN, ((980, 660), (1305, 660), (1305, 430))),
        Flow("flow-haversine", "vm-flow-haversine", ids["stage-api"], ids["stage-normalize"], "Provider failure → straight line", "Penyedia gagal → garis lurus", EDGE_DASHED, ((565, 455), (935, 455))),
    ]
    for flow in flows:
        add_flow(root, prefix, flow)
    return document


def build_geo_server_communication() -> ET.Element:
    diagram_id = "geo-server-communication-workflow"
    prefix = diagram_id
    document, root = new_document(diagram_id, "Geo Server Communication")
    add_header(root, prefix, "Geo Server Communication", "Komunikasi Pelayan Geo", "Current production request path, cache boundary and private DigitalOcean provider network", "Laluan permintaan produksi semasa, sempadan cache dan rangkaian penyedia DigitalOcean peribadi")
    stages = [
        Vertex("stage-browser", "gs-stage-browser", rich("PetaKerja browser", "Vite + MapLibre application", "Calls only same-origin /api/geo/*"), rich("Pelayar PetaKerja", "Aplikasi Vite + MapLibre", "Hanya memanggil /api/geo/* same-origin"), 30, 125, 330, 285, CARD_BLUE, "browser,maplibre-gl,geo-service", hotspots="map-search,map-canvas", source_files="src/services/geo.ts,src/managers/GeoNavigationManager.ts", routes="/api/geo/*"),
        Vertex("stage-vercel", "gs-stage-vercel", rich("Matching Vercel deployment", "Edge rewrite → api/server.ts → Express", "GeoGateway validates, limits and normalizes"), rich("Deployment Vercel sepadan", "Rewrite edge → api/server.ts → Express", "GeoGateway mengesah, mengehad dan menormal"), 400, 125, 330, 285, CARD_NEUTRAL, "vercel-runtime,vercel-edge-delivery,vercel-node-function,express-app,geo-api,geo-gateway", source_files="vercel.json,api/server.ts,server/app.ts,server/routes/geo.ts,server/geo/gateway.ts", routes="/api/geo/*"),
        Vertex("stage-cache", "gs-stage-cache", rich("Environment Supabase", "Production/staging keep isolated projects", "geo_route_cache + geo_geocode_cache"), rich("Supabase persekitaran", "Produksi/staging menggunakan projek berasingan", "geo_route_cache + geo_geocode_cache"), 770, 125, 330, 285, CARD_CYAN, "supabase-db,geo-route-cache,geo-geocode-cache", "geo_route_cache,geo_geocode_cache", source_files="server/geo/gateway.ts,supabase/migrations/20260718011925_geo_gateway_routing_and_studio.sql"),
        Vertex("stage-origin", "gs-stage-origin", rich("Public geo origin", "Cloudflare DNS-only → DigitalOcean", "Caddy terminates HTTPS + checks bearer token"), rich("Origin geo awam", "Cloudflare DNS sahaja → DigitalOcean", "Caddy menamatkan HTTPS + menyemak token bearer"), 1140, 125, 330, 285, CARD_AMBER, "cloudflare-dns,digitalocean-geo-host,caddy-geo-edge", source_files="infra/geo/Caddy.routing,infra/geo/Caddyfile,infra/geo/README.md", routes="https://geo.petakerja.my"),
        Vertex("stage-docker", "gs-stage-docker", rich("Private Docker network", "Valhalla :8002 · current", "Nominatim :8080 · future / gated"), rich("Rangkaian Docker peribadi", "Valhalla :8002 · semasa", "Nominatim :8080 · masa depan / berpagar"), 1510, 125, 380, 285, CARD_TEAL, "geo-docker-network,valhalla,nominatim", source_files="infra/geo/compose.routing.yaml,infra/geo/compose.yaml", routes="Valhalla HTTP API,Nominatim HTTP API"),
    ]
    ids = add_numbered_stages(root, prefix, stages)
    add_logo(root, prefix, "petakerja", petakerja_logo(), 54, 192, 68, 68)
    add_logo(root, prefix, "vercel", BRANDS / "vercel.svg", 424, 194)
    add_logo(root, prefix, "supabase", BRANDS / "supabase.svg", 794, 194)
    add_logo(root, prefix, "cloudflare", BRANDS / "cloudflare.svg", 1164, 194)
    add_logo(root, prefix, "digitalocean", BRANDS / "digitalocean.svg", 1244, 194)
    add_logo(root, prefix, "caddy", BRANDS / "caddy.svg", 1324, 194)
    add_logo(root, prefix, "docker", BRANDS / "docker.svg", 1534, 190, 72, 72)
    add_logo(root, prefix, "valhalla", BRANDS / "valhalla.svg", 1622, 190, 72, 72, "Current")
    add_logo(root, prefix, "nominatim", BRANDS / "openstreetmap.svg", 1710, 194, 64, 64, "Future")
    maintenance = Vertex("maintenance", "gs-maintenance", rich("Regional map-data maintenance", "Geofabrik Malaysia/Singapore/Brunei PBF → Valhalla monthly rebuild; future Nominatim replication remains disabled."), rich("Penyelenggaraan data peta wilayah", "PBF Geofabrik Malaysia/Singapura/Brunei → bina semula Valhalla bulanan; replikasi Nominatim masa depan kekal dinyahaktifkan."), 60, 500, 860, 140, PANEL, "geofabrik-extract,valhalla-tile-builder,valhalla,nominatim", source_files="infra/geo/scripts/rebuild-valhalla-routing.sh,infra/geo/compose.routing.yaml,infra/geo/compose.yaml", role="maintenance")
    add_vertex(root, prefix, maintenance)
    add_logo(root, prefix, "openstreetmap", BRANDS / "openstreetmap.svg", 760, 535, 50, 50, "Geofabrik / OSM")
    add_vertex(root, prefix, Vertex("note-security", "gs-note-security", rich("Trust boundary", "Only ports 80/443 are public. Ports 8002/8080 stay inside Docker. GEO_SERVICE_TOKEN exists only in Vercel server environments and Caddy runtime."), rich("Sempadan kepercayaan", "Hanya port 80/443 awam. Port 8002/8080 kekal dalam Docker. GEO_SERVICE_TOKEN hanya wujud dalam persekitaran pelayan Vercel dan runtime Caddy."), 960, 495, 910, 145, NOTE_AMBER, "vercel-node-function,caddy-geo-edge,geo-docker-network", source_files="infra/geo/Caddy.routing,infra/geo/compose.routing.yaml,infra/geo/README.md", role="note"))
    add_vertex(root, prefix, Vertex("note-status", "gs-note-status", rich("Current versus future", "Solid path: routing-only Valhalla pilot on the Singapore Droplet. Dashed path: larger combined Nominatim + Valhalla deployment after capacity approval."), rich("Semasa berbanding masa depan", "Laluan padu: rintis Valhalla sahaja pada Droplet Singapura. Laluan putus-putus: deployment Nominatim + Valhalla lebih besar selepas kelulusan kapasiti."), 60, 690, 1810, 120, NOTE_PURPLE, "digitalocean-geo-host,valhalla,nominatim", role="note", status="gated"))
    flows = [
        Flow("flow-request", "gs-flow-request", ids["stage-browser"], ids["stage-vercel"], "HTTPS same-origin /api/geo/*", "HTTPS /api/geo/* same-origin", EDGE_BLUE),
        Flow("flow-cache", "gs-flow-cache", ids["stage-vercel"], ids["stage-cache"], "Server-side cache read/write", "Baca/tulis cache pelayan", EDGE_CYAN),
        Flow("flow-origin", "gs-flow-origin", ids["stage-vercel"], ids["stage-origin"], "HTTPS + bearer token", "HTTPS + token bearer", EDGE_AMBER, ((565, 445), (1305, 445))),
        Flow("flow-valhalla", "gs-flow-valhalla", ids["stage-origin"], ids["stage-docker"], "Caddy → Valhalla :8002", "Caddy → Valhalla :8002", EDGE_TEAL),
        Flow("flow-provider-response", "gs-flow-provider-response", ids["stage-docker"], ids["stage-vercel"], "Provider JSON response", "Respons JSON penyedia", EDGE_TEAL, ((1700, 455), (565, 455))),
        Flow("flow-browser-response", "gs-flow-browser-response", ids["stage-vercel"], ids["stage-browser"], "Normalized JSON", "JSON ternormal", EDGE_BLUE, ((565, 475), (195, 475))),
        Flow("flow-maintenance", "gs-flow-maintenance", "gs-maintenance", ids["stage-docker"], "PBF / replication data", "Data PBF / replikasi", EDGE_DASHED, ((1080, 660), (1700, 660), (1700, 430))),
        Flow("flow-future-nominatim", "gs-flow-future-nominatim", ids["stage-origin"], ids["stage-docker"], "Future Caddy → Nominatim :8080", "Caddy masa depan → Nominatim :8080", EDGE_FUTURE, ((1305, 445), (1785, 445)), status="gated"),
    ]
    for flow in flows:
        add_flow(root, prefix, flow)
    return document


BUILDERS = {
    "nominatim-valhalla-workflow": build_nominatim_valhalla,
    "nominatim-maplibre-workflow": build_nominatim_maplibre,
    "valhalla-maplibre-workflow": build_valhalla_maplibre,
    "geo-server-communication-workflow": build_geo_server_communication,
}


def validate(diagram_id: str, document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != DIAGRAMS[diagram_id]:
        raise ValueError(f"{diagram_id} is missing page {DIAGRAMS[diagram_id]}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(PAGE_WIDTH), str(PAGE_HEIGHT)):
        raise ValueError(f"{diagram_id} canvas must be exactly {PAGE_WIDTH} x {PAGE_HEIGHT}")
    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if not all(keys) or len(keys) != len(set(keys)):
        raise ValueError(f"{diagram_id} component keys must be present and unique")
    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            raise ValueError(f"{wrapper.get('id')} is missing bilingual labels")
    stages = [wrapper for wrapper in wrappers if wrapper.get("workflowRole") == "stage"]
    if len(stages) != 5:
        raise ValueError(f"{diagram_id} must contain exactly five numbered stages")
    vertex_ids = {
        wrapper.get("id", "") for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    for wrapper in wrappers:
        cell = wrapper.find("mxCell")
        if cell is not None and cell.get("edge") == "1" and (cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids):
            raise ValueError(f"{wrapper.get('id')} has a disconnected endpoint")
    for cell in diagram.findall(".//mxCell"):
        style = cell.get("style", "")
        if "shape=image" in style and ("image=data:image/" not in style or "image=http" in style):
            raise ValueError(f"{cell.get('id')} does not use an embedded local image")
        if "gradientColor=" in style:
            raise ValueError(f"{cell.get('id')} uses a forbidden gradient")


def build_documents() -> dict[str, ET.Element]:
    documents = {diagram_id: builder() for diagram_id, builder in BUILDERS.items()}
    for diagram_id, document in documents.items():
        validate(diagram_id, document)
    return documents


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for diagram_id, document in build_documents().items():
        ET.indent(document, space="  ")
        output = OUTPUT_DIR / f"{diagram_id}.drawio"
        ET.ElementTree(document).write(output, encoding="utf-8", xml_declaration=True)
        print(f"Wrote {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
