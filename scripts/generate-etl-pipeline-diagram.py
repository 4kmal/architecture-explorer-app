#!/usr/bin/env python3
"""Generate the editable bilingual PetaKerja operational ETL diagram.

The source is intentionally grounded in the checked-in runtime configuration:
GitHub Actions performs scheduled dataset ingestion, Vercel runs the application
and its daily maintenance cron, Supabase is the operational store, and the
DigitalOcean pilot hosts the separately-built Valhalla routing data.
"""

from __future__ import annotations

from dataclasses import dataclass
import html
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "editor" / "etl-pipeline.drawio"
PAGE_ID = "petakerja_etl_pipeline"
PAGE_WIDTH = 2048
PAGE_HEIGHT = 1120


TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=25;fontStyle=1;fontColor=light-dark(#172033,#e8edf7);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontStyle=2;fontColor=light-dark(#667085,#aeb8c8);"
REGION_CONTROL = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#eef2ff,#172037);strokeColor=light-dark(#8fa4ff,#637ee8);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingTop=14;spacingLeft=16;"
REGION_SOURCE = "rounded=1;arcSize=18;whiteSpace=wrap;html=1;fillColor=light-dark(#eef6ff,#142235);strokeColor=light-dark(#83b8ec,#4f8bc6);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=16;fontStyle=1;align=center;verticalAlign=bottom;spacingBottom=12;"
REGION_ETL = "rounded=1;arcSize=18;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8ee,#2a2118);strokeColor=light-dark(#e6ad69,#b87931);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=16;fontStyle=1;align=center;verticalAlign=bottom;spacingBottom=12;"
REGION_SERVE = "rounded=1;arcSize=18;whiteSpace=wrap;html=1;fillColor=light-dark(#eefaf3,#14281d);strokeColor=light-dark(#75c997,#4a9d6c);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=16;fontStyle=1;align=center;verticalAlign=bottom;spacingBottom=12;"
REGION_NOTES = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#f7f9fc,#171c24);strokeColor=light-dark(#c7d0dc,#596579);strokeWidth=1;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=left;verticalAlign=middle;spacingLeft=16;"
STAGE = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=light-dark(#b9834b,#916332);strokeWidth=1;dashed=1;dashPattern=6 4;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=14;fontStyle=1;align=center;verticalAlign=top;spacingTop=12;"
CARD_CONTROL = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#202943);strokeColor=light-dark(#7759d8,#9a82ef);strokeWidth=1.25;fontColor=light-dark(#172033,#eef1ff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;shadow=1;"
CARD_SOURCE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1b2d43);strokeColor=light-dark(#4f91d4,#70afea);strokeWidth=1.1;fontColor=light-dark(#17375e,#e7f2ff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_PROCESS = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fffdf9,#332719);strokeColor=light-dark(#d58e3b,#d8a25d);strokeWidth=1.1;fontColor=light-dark(#5c3912,#fff0d6);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_STORE = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;whiteSpace=wrap;html=1;fillColor=light-dark(#fff3ca,#3a3019);strokeColor=light-dark(#c38b21,#d5a941);strokeWidth=1.2;fontColor=light-dark(#513700,#fff0bd);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_SERVE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#193126);strokeColor=light-dark(#3da86a,#62ca88);strokeWidth=1.2;fontColor=light-dark(#174a2b,#e5ffed);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;shadow=1;"
CARD_DISABLED = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f2f4f7,#242932);strokeColor=light-dark(#98a2b3,#747f90);strokeWidth=1.1;dashed=1;dashPattern=6 4;fontColor=light-dark(#475467,#d0d5dd);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
NOTE = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#202630);strokeColor=light-dark(#98a2b3,#697586);strokeWidth=1;fontColor=light-dark(#344054,#e2e7ef);fontFamily=Arial;fontSize=11;align=center;verticalAlign=middle;spacing=7;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=light-dark(#667085,#aeb8c8);strokeWidth=1.4;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
EDGE_CONTROL = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#7759d8,#9a82ef);"
EDGE_DATA = EDGE + "strokeColor=light-dark(#c17424,#e0a24e);"
EDGE_SERVE = EDGE + "strokeColor=light-dark(#2f9b5e,#62ca88);"


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
    role: str = "card"


@dataclass(frozen=True)
class Flow:
    key: str
    identifier: str
    source: str
    target: str
    label_en: str = ""
    label_ms: str = ""
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
        "petakerjaKey": f"etl-pipeline/{key}",
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
            spec.table_name, spec.hotspots, etlRole=spec.role,
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


def add_flow(root: ET.Element, spec: Flow) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(spec.label_en, spec.label_ms, spec.key, etlRole="flow"),
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


def build_document() -> ET.Element:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja ETL Pipeline Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaLayoutStandard": "etl-pipeline-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": PAGE_ID,
        "name": "PetaKerja Operational ETL & Serving Pipeline",
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
        Vertex("title", "etl-title", "PetaKerja Operational ETL & Serving Pipeline", "Pipeline ETL Operasi & Penyampaian PetaKerja", 50, 18, 1948, 38, TITLE, role="title"),
        Vertex("subtitle", "etl-subtitle", "Current batch ingestion, normalization, operational storage and application delivery", "Ingest kelompok, penormalan, storan operasi dan penyampaian aplikasi semasa", 50, 58, 1948, 26, SUBTITLE, role="subtitle"),

        Vertex("region-control", "etl-region-control", "CONTROL & SCHEDULING", "KAWALAN & PENJADUALAN", 50, 100, 1948, 125, REGION_CONTROL, role="region"),
        Vertex("control-github", "etl-control-github", rich("GitHub Actions", "events every 6 h", "jobs 02:00 UTC · extractors 03:00 UTC", "coffee weekly"), rich("GitHub Actions", "acara setiap 6 jam", "kerja 02:00 UTC · extractor 03:00 UTC", "kopi mingguan"), 250, 135, 330, 66, CARD_CONTROL, "github-actions"),
        Vertex("control-vercel", "etl-control-vercel", rich("Vercel Cron", "/api/cron/daily · 01:00 UTC", "four isolated maintenance steps"), rich("Cron Vercel", "/api/cron/daily · 01:00 UTC", "empat langkah penyelenggaraan terasing"), 650, 135, 330, 66, CARD_CONTROL, "vercel-daily-cron"),
        Vertex("control-admin", "etl-control-admin", rich("Administrator / manual run", "feature-gated extractor runtimes", "source-scoped execution"), rich("Pentadbir / pelaksanaan manual", "runtime extractor berpagar ciri", "pelaksanaan mengikut sumber"), 1050, 135, 330, 66, CARD_CONTROL, "extractor-service"),
        Vertex("control-do", "etl-control-do", rich("DigitalOcean maintenance", "monthly regional tile rebuild", "preflight · rollback · route checks"), rich("Penyelenggaraan DigitalOcean", "binaan semula jubin wilayah bulanan", "prasemak · undur · semak laluan"), 1450, 135, 330, 66, CARD_CONTROL, "valhalla-tile-builder"),

        Vertex("region-sources", "etl-region-sources", "SOURCE CONTEXT", "KONTEKS SUMBER", 50, 245, 330, 680, REGION_SOURCE, role="region"),
        Vertex("source-jobs", "etl-source-jobs", rich("Malaysian job boards", "8 configured sources", "HTML + public listing endpoints"), rich("Papan kerja Malaysia", "8 sumber dikonfigurasi", "HTML + endpoint senarai awam"), 85, 300, 260, 90, CARD_SOURCE),
        Vertex("source-apis", "etl-source-apis", rich("Extractor sources", "Adzuna · Khamsat · Wuzzuf", "operator-only runtimes remain gated"), rich("Sumber extractor", "Adzuna · Khamsat · Wuzzuf", "runtime operator kekal berpagar"), 85, 410, 260, 90, CARD_SOURCE),
        Vertex("source-community", "etl-source-community", rich("Community sources", "Petakopi specialty cafés", "Luma technology and AI events"), rich("Sumber komuniti", "kafe specialty Petakopi", "acara teknologi dan AI Luma"), 85, 520, 260, 90, CARD_SOURCE),
        Vertex("source-app", "etl-source-app", rich("Application maintenance", "scheduled posts · view events", "broadcast queue · watchlists"), rich("Penyelenggaraan aplikasi", "post berjadual · peristiwa paparan", "baris siar · senarai pantau"), 85, 630, 260, 90, CARD_SOURCE),
        Vertex("source-osm", "etl-source-osm", rich("Geofabrik OSM extract", "regional .osm.pbf", "routing-only pilot input"), rich("Ekstrak OSM Geofabrik", ".osm.pbf wilayah", "input rintis penghalaan sahaja"), 85, 740, 260, 90, CARD_SOURCE),

        Vertex("region-etl", "etl-region-etl", "OPERATIONAL ETL", "ETL OPERASI", 400, 245, 980, 680, REGION_ETL, role="region"),
        Vertex("stage-extract", "etl-stage-extract", "1 · EXTRACT", "1 · EKSTRAK", 430, 290, 290, 570, STAGE, role="stage"),
        Vertex("stage-transform", "etl-stage-transform", "2 · NORMALIZE & VALIDATE", "2 · NORMALISASI & SAH", 745, 290, 290, 570, STAGE, role="stage"),
        Vertex("stage-load", "etl-stage-load", "3 · PERSIST & PROTECT", "3 · SIMPAN & LINDUNGI", 1060, 290, 290, 570, STAGE, role="stage"),

        Vertex("extract-jobs", "etl-extract-jobs", rich("Job ingestion", "TypeScript workers + Scrapling bridge", "parallel sources; polite delay per source"), rich("Ingest pekerjaan", "worker TypeScript + bridge Scrapling", "sumber selari; sela sopan setiap sumber"), 455, 345, 240, 92, CARD_PROCESS, "extractor-service"),
        Vertex("extract-community", "etl-extract-community", rich("Community ingestion", "Python Scrapling Fetcher", "stealth browser fallback when required"), rich("Ingest komuniti", "Scrapling Fetcher Python", "sandaran pelayar stealth apabila perlu"), 455, 470, 240, 92, CARD_PROCESS, "kopi-manager,event-manager"),
        Vertex("extract-maintenance", "etl-extract-maintenance", rich("Daily maintenance", "promote · roll up · drain · poll", "each step reports independently"), rich("Penyelenggaraan harian", "promosi · gulung · hantar · tinjau", "setiap langkah melapor berasingan"), 455, 595, 240, 92, CARD_PROCESS, "vercel-daily-cron,blog-routes,watchlist-service"),
        Vertex("extract-tiles", "etl-extract-tiles", rich("Valhalla tile build", "download regional PBF", "retain previous archive before rebuild"), rich("Binaan jubin Valhalla", "muat turun PBF wilayah", "simpan arkib lama sebelum bina semula"), 455, 720, 240, 92, CARD_PROCESS, "valhalla-tile-builder"),

        Vertex("transform-jobs", "etl-transform-jobs", rich("Normalize job records", "canonical URL · Malaysia location/state", "salary · remote · experience · expiry"), rich("Normalisasi rekod kerja", "URL kanonik · lokasi/negeri Malaysia", "gaji · remote · pengalaman · tamat"), 770, 345, 240, 92, CARD_PROCESS, "extractor-service,job-entity"),
        Vertex("transform-community", "etl-transform-community", rich("Normalize community records", "deduplicate cafés", "event coordinates · city fallback · KL bounds"), rich("Normalisasi rekod komuniti", "nyahpendua kafe", "koordinat acara · sandaran bandar · sempadan KL"), 770, 470, 240, 92, CARD_PROCESS, "kopi-manager,event-manager"),
        Vertex("transform-safeguards", "etl-transform-safeguards", rich("Batch safeguards", "validate required fields", "non-zero guard · source-scoped stale cleanup"), rich("Perlindungan kelompok", "sahkan medan wajib", "penghadang bukan sifar · bersih lapuk ikut sumber"), 770, 595, 240, 92, CARD_PROCESS, "extractor-service,supabase-db"),
        Vertex("transform-tiles", "etl-transform-tiles", rich("Validate routing artifacts", "disk-headroom preflight", "health + representative route checks"), rich("Sahkan artifak penghalaan", "prasemak ruang cakera", "kesihatan + semakan laluan contoh"), 770, 720, 240, 92, CARD_PROCESS, "valhalla-tile-builder,valhalla"),

        Vertex("load-jobs", "etl-load-jobs", rich("Job serving data", "scraped_jobs", "extractor_runs · extractor_jobs JSONB"), rich("Data penyampaian kerja", "scraped_jobs", "extractor_runs · extractor_jobs JSONB"), 1085, 335, 240, 112, CARD_STORE, "supabase-db,extractor-entity,job-entity", "scraped_jobs"),
        Vertex("load-community", "etl-load-community", rich("Community + app data", "coffee_shops · events", "blog analytics · broadcasts · watchlists"), rich("Data komuniti + aplikasi", "coffee_shops · events", "analitik blog · siaran · senarai pantau"), 1085, 475, 240, 112, CARD_STORE, "supabase-db,community-data"),
        Vertex("load-cache", "etl-load-cache", rich("Reusable geo data", "geo_route_cache", "geo_geocode_cache remains gated"), rich("Data geo boleh guna semula", "geo_route_cache", "geo_geocode_cache kekal berpagar"), 1085, 615, 240, 112, CARD_STORE, "supabase-db,geo-route-cache,geo-geocode-cache", "geo_route_cache"),
        Vertex("load-tiles", "etl-load-tiles", rich("Routing archive", "valhalla_tiles.tar", "previous archive retained for rollback"), rich("Arkib penghalaan", "valhalla_tiles.tar", "arkib lama disimpan untuk undur"), 1085, 755, 240, 76, CARD_STORE, "valhalla-tile-builder"),

        Vertex("region-serving", "etl-region-serving", "PLATFORMS & CONSUMPTION", "PLATFORM & PENGGUNAAN", 1400, 245, 598, 680, REGION_SERVE, role="region"),
        Vertex("serve-supabase", "etl-serve-supabase", rich("Supabase PostgreSQL + PostGIS", "operational tables + normalized serving data", "service role: server / CI only"), rich("Supabase PostgreSQL + PostGIS", "jadual operasi + data penyampaian ternormal", "service role: pelayan / CI sahaja"), 1445, 315, 235, 175, CARD_STORE, "supabase-db"),
        Vertex("serve-do", "etl-serve-do", rich("DigitalOcean Valhalla", "Singapore routing-only pilot", "Caddy gateway · internal tile service"), rich("Valhalla DigitalOcean", "rintis penghalaan sahaja di Singapura", "gerbang Caddy · servis jubin dalaman"), 1720, 315, 235, 175, CARD_SERVE, "digitalocean-geo-host,valhalla"),
        Vertex("serve-vercel", "etl-serve-vercel", rich("Vercel Vite + Express", "/api/jobs/supa · /api/intel/*", "/api/geo/* through GeoGateway"), rich("Vite + Express di Vercel", "/api/jobs/supa · /api/intel/*", "/api/geo/* melalui GeoGateway"), 1445, 545, 235, 150, CARD_SERVE, "vercel-runtime,express-app,geo-gateway"),
        Vertex("serve-browser", "etl-serve-browser", rich("PetaKerja browser", "Job Finder · MapLibre job map", "Kopi · Events · route visualization"), rich("Pelayar PetaKerja", "Job Finder · peta kerja MapLibre", "Kopi · Acara · visualisasi laluan"), 1720, 545, 235, 150, CARD_SERVE, "browser,job-manager,kopi-manager,event-manager,map-manager", hotspots="jobs-search,jobs-cards,jobs-map,map-canvas"),
        Vertex("serve-nominatim", "etl-serve-nominatim", rich("Nominatim", "supported by code · currently disabled", "no active geocoding ingestion"), rich("Nominatim", "disokong kod · kini dinyahaktifkan", "tiada ingest geokod aktif"), 1580, 755, 240, 76, CARD_DISABLED, "nominatim"),

        Vertex("region-notes", "etl-region-notes", "OPERATIONAL TRUTH", "KEADAAN OPERASI", 50, 955, 1948, 120, REGION_NOTES, role="region"),
        Vertex("note-stack", "etl-note-stack", rich("Current pattern", "sources → batch ETL → operational stores → APIs → browser"), rich("Corak semasa", "sumber → ETL kelompok → storan operasi → API → pelayar"), 245, 980, 365, 68, NOTE, role="note"),
        Vertex("note-security", "etl-note-security", rich("Security boundary", "service-role and provider tokens never enter the browser"), rich("Sempadan keselamatan", "service-role dan token penyedia tidak masuk ke pelayar"), 660, 980, 365, 68, NOTE, role="note"),
        Vertex("note-failure", "etl-note-failure", rich("Failure behavior", "failed or zero-result scrapes preserve existing serving data"), rich("Tingkah laku kegagalan", "scrape gagal atau sifar mengekalkan data sedia ada"), 1075, 980, 365, 68, NOTE, role="note"),
        Vertex("note-routing", "etl-note-routing", rich("Routing status · 20 Jul 2026", "Valhalla available · ETA traffic-independent · Nominatim disabled"), rich("Status penghalaan · 20 Jul 2026", "Valhalla tersedia · ETA tanpa trafik · Nominatim dinyahaktifkan"), 1490, 980, 365, 68, NOTE, role="note"),
    ]

    ids: dict[str, str] = {}
    for vertex in vertices:
        ids[vertex.key] = add_vertex(root, vertex)

    flows = [
        Flow("control/github-jobs", "etl-flow-control-jobs", ids["control-github"], ids["extract-jobs"], style=EDGE_CONTROL, points=((415, 230), (575, 230))),
        Flow("control/github-community", "etl-flow-control-community", ids["control-github"], ids["extract-community"], style=EDGE_CONTROL, points=((415, 235), (405, 235), (405, 515))),
        Flow("control/vercel", "etl-flow-control-vercel", ids["control-vercel"], ids["extract-maintenance"], style=EDGE_CONTROL, points=((815, 235), (730, 235), (730, 640))),
        Flow("control/admin", "etl-flow-control-admin", ids["control-admin"], ids["extract-jobs"], "manual", "manual", EDGE_CONTROL, ((1215, 235), (705, 235), (705, 390))),
        Flow("control/digitalocean", "etl-flow-control-do", ids["control-do"], ids["extract-tiles"], style=EDGE_CONTROL, points=((1615, 235), (1370, 235), (1370, 845), (705, 845), (705, 765))),

        Flow("source/jobs", "etl-flow-source-jobs", ids["source-jobs"], ids["extract-jobs"], style=EDGE_DATA),
        Flow("source/apis", "etl-flow-source-apis", ids["source-apis"], ids["extract-jobs"], style=EDGE_DATA),
        Flow("source/community", "etl-flow-source-community", ids["source-community"], ids["extract-community"], style=EDGE_DATA),
        Flow("source/app", "etl-flow-source-app", ids["source-app"], ids["extract-maintenance"], style=EDGE_DATA),
        Flow("source/osm", "etl-flow-source-osm", ids["source-osm"], ids["extract-tiles"], style=EDGE_DATA),

        Flow("jobs/extract-transform", "etl-flow-jobs-normalize", ids["extract-jobs"], ids["transform-jobs"], "validated records", "rekod disahkan", EDGE_DATA),
        Flow("community/extract-transform", "etl-flow-community-normalize", ids["extract-community"], ids["transform-community"], style=EDGE_DATA),
        Flow("maintenance/extract-transform", "etl-flow-maintenance-safeguards", ids["extract-maintenance"], ids["transform-safeguards"], style=EDGE_DATA),
        Flow("tiles/extract-transform", "etl-flow-tiles-validate", ids["extract-tiles"], ids["transform-tiles"], style=EDGE_DATA),
        Flow("jobs/transform-load", "etl-flow-jobs-load", ids["transform-jobs"], ids["load-jobs"], "source-scoped upsert", "upsert mengikut sumber", EDGE_DATA),
        Flow("community/transform-load", "etl-flow-community-load", ids["transform-community"], ids["load-community"], style=EDGE_DATA),
        Flow("tiles/transform-load", "etl-flow-tiles-load", ids["transform-tiles"], ids["load-tiles"], style=EDGE_DATA),

        Flow("load/jobs-supabase", "etl-flow-jobs-supabase", ids["load-jobs"], ids["serve-supabase"], style=EDGE_SERVE),
        Flow("load/community-supabase", "etl-flow-community-supabase", ids["load-community"], ids["serve-supabase"], style=EDGE_SERVE),
        Flow("load/cache-supabase", "etl-flow-cache-supabase", ids["load-cache"], ids["serve-supabase"], style=EDGE_SERVE),
        Flow("load/tiles-digitalocean", "etl-flow-tiles-digitalocean", ids["load-tiles"], ids["serve-do"], style=EDGE_SERVE, points=((1365, 793), (1380, 793), (1380, 510), (1837, 510))),
        Flow("serve/supabase-vercel", "etl-flow-supabase-vercel", ids["serve-supabase"], ids["serve-vercel"], "server/Data API", "API pelayan/Data", EDGE_SERVE),
        Flow("serve/vercel-digitalocean", "etl-flow-vercel-do", ids["serve-vercel"], ids["serve-do"], "server-only route request", "permintaan laluan pelayan sahaja", EDGE_SERVE, ((1700, 620), (1700, 520), (1837, 520))),
        Flow("serve/vercel-browser", "etl-flow-vercel-browser", ids["serve-vercel"], ids["serve-browser"], style=EDGE_SERVE),
        Flow("serve/vercel-cache", "etl-flow-vercel-cache", ids["serve-vercel"], ids["load-cache"], "runtime cache writes", "tulisan cache masa jalan", EDGE_SERVE, ((1425, 680), (1365, 680))),
        Flow("serve/nominatim-gateway", "etl-flow-nominatim-gateway", ids["serve-vercel"], ids["serve-nominatim"], "feature gate: off", "pagar ciri: tutup", EDGE_CONTROL),
    ]
    for flow in flows:
        add_flow(root, flow)
    return mxfile


def validate(document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise RuntimeError(f"ETL diagram must contain page {PAGE_ID!r}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(PAGE_WIDTH), str(PAGE_HEIGHT)):
        raise RuntimeError(f"ETL diagram canvas must be {PAGE_WIDTH} x {PAGE_HEIGHT}")

    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if len(keys) != len(set(keys)) or any(not key.startswith("etl-pipeline/") for key in keys):
        raise RuntimeError("ETL diagram component keys must be unique and namespaced")
    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            raise RuntimeError(f"{wrapper.get('id')} is missing bilingual labels")

    cells = {cell.get("id", ""): cell for cell in diagram.findall(".//mxCell")}
    object_cells = {
        wrapper.get("id", ""): wrapper.find("mxCell")
        for wrapper in wrappers
        if wrapper.find("mxCell") is not None
    }
    vertex_ids = {identifier for identifier, cell in object_cells.items() if cell is not None and cell.get("vertex") == "1"}
    for identifier, cell in object_cells.items():
        if cell is None or cell.get("edge") != "1":
            continue
        if cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids:
            raise RuntimeError(f"{identifier} has a disconnected endpoint")

    required_nodes = {
        "github-actions", "vercel-daily-cron", "digitalocean-geo-host", "valhalla-tile-builder",
        "supabase-db", "express-app", "geo-gateway", "valhalla", "nominatim", "browser",
    }
    represented = {
        node_id
        for wrapper in wrappers
        for node_id in wrapper.get("nodeIds", "").split(",")
        if node_id
    }
    missing = required_nodes - represented
    if missing:
        raise RuntimeError(f"ETL diagram is missing architecture nodes: {sorted(missing)}")

    visible = " ".join(html.unescape(wrapper.get("label", "")) for wrapper in wrappers).lower()
    forbidden = ("aws lambda", "terraform", "step functions", "bronze layer", "silver layer", "gold layer", "dbt")
    found = [term for term in forbidden if term in visible]
    if found:
        raise RuntimeError(f"ETL diagram contains unimplemented platform claims: {found}")
    if len(cells) < 2:
        raise RuntimeError("ETL diagram graph is empty")


def main() -> None:
    document = build_document()
    validate(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(document, space="  ")
    ET.ElementTree(document).write(OUTPUT, encoding="utf-8", xml_declaration=False)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
