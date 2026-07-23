#!/usr/bin/env python3
"""Generate the editable bilingual FYP Work Breakdown Structure diagram."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import html
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "assets" / "editor" / "fyp-report" / "work-breakdown-structure.drawio"
DIAGRAM_ID = "fyp-work-breakdown-structure"
PAGE_ID = "petakerja_fyp_work_breakdown_structure"
PAGE_WIDTH = 1800
PAGE_HEIGHT = 1350

TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=28;fontStyle=1;fontColor=light-dark(#172033,#edf2fb);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontColor=light-dark(#5f6b7a,#b8c2d1);"
ROOT_BOX = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#171d26);strokeColor=light-dark(#243b63,#8aa4cf);strokeWidth=2;fontColor=light-dark(#172033,#f3f6fb);fontFamily=Arial;fontSize=19;fontStyle=1;align=center;verticalAlign=middle;spacingLeft=86;spacingRight=18;shadow=0;"
PHASE_BASE = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;strokeWidth=1.8;fontColor=light-dark(#172033,#f4f7fb);fontFamily=Arial;fontSize=16;fontStyle=1;align=center;verticalAlign=middle;spacing=12;shadow=0;"
TASK_BASE = "rounded=1;arcSize=7;whiteSpace=wrap;html=1;strokeWidth=1.2;fontColor=light-dark(#253044,#edf2f8);fontFamily=Arial;fontSize=14;align=center;verticalAlign=middle;spacing=12;shadow=0;"
PHASE_STYLES = (
    PHASE_BASE + "fillColor=light-dark(#eaf2ff,#17243a);strokeColor=light-dark(#527fbd,#7fa9df);",
    PHASE_BASE + "fillColor=light-dark(#f2edff,#251e36);strokeColor=light-dark(#7c66aa,#a993d3);",
    PHASE_BASE + "fillColor=light-dark(#e9f8f2,#172c27);strokeColor=light-dark(#2e8c70,#60b99d);",
    PHASE_BASE + "fillColor=light-dark(#fff4e5,#2b2419);strokeColor=light-dark(#bf8124,#d6a04b);",
    PHASE_BASE + "fillColor=light-dark(#f0f3f7,#202630);strokeColor=light-dark(#66758a,#98a5b7);",
)
TASK_STYLES = (
    TASK_BASE + "fillColor=light-dark(#f7faff,#121d2d);strokeColor=light-dark(#8faed7,#587da9);",
    TASK_BASE + "fillColor=light-dark(#faf8ff,#1c1728);strokeColor=light-dark(#ad9dcd,#766295);",
    TASK_BASE + "fillColor=light-dark(#f5fbf8,#12231f);strokeColor=light-dark(#82bba8,#427f6d);",
    TASK_BASE + "fillColor=light-dark(#fffaf2,#231e15);strokeColor=light-dark(#d2ac70,#9e7639);",
    TASK_BASE + "fillColor=light-dark(#f8f9fb,#181d25);strokeColor=light-dark(#a7b0bf,#697589);",
)
NUMBER = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=light-dark(#253858,#536a98);strokeColor=none;fontColor=#ffffff;fontFamily=Arial;fontSize=13;fontStyle=1;align=center;verticalAlign=middle;"
IMAGE = "shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;strokeColor=none;fillColor=none;"
EDGE_ROOT = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=none;startArrow=none;strokeWidth=1.8;strokeColor=light-dark(#66758a,#9aa7b8);exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
EDGE_TASK = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=none;startArrow=none;strokeWidth=1.4;strokeColor=light-dark(#8290a3,#7f8b9d);exitX=0.5;exitY=1;entryX=0;entryY=0.5;"


@dataclass(frozen=True)
class Component:
    key: str
    identifier: str
    simple_en: str
    simple_ms: str
    code_en: str
    code_ms: str
    node_ids: str
    source_files: str
    routes: str = ""
    tables: str = ""
    hotspots: str = ""


@dataclass(frozen=True)
class Phase:
    component: Component
    tasks: tuple[Component, ...]


def rich(title: str, detail: str = "") -> str:
    if not detail:
        return f"<b>{html.escape(title)}</b>"
    return f"<b>{html.escape(title)}</b><br>{html.escape(detail)}"


def attrs(component: Component, role: str) -> dict[str, str]:
    values = {
        "label": component.simple_en,
        "labelEn": component.simple_en,
        "labelMs": component.simple_ms,
        "simpleLabelEn": component.simple_en,
        "simpleLabelMs": component.simple_ms,
        "codeLabelEn": component.code_en,
        "codeLabelMs": component.code_ms,
        "petakerjaKey": f"{DIAGRAM_ID}/{component.key}",
        "nodeIds": component.node_ids,
        "sourceFiles": component.source_files,
        "routePaths": component.routes,
        "tableName": component.tables,
        "uiHotspots": component.hotspots,
        "component": "1",
        "architectureRole": role,
    }
    return {name: value for name, value in values.items() if value}


def add_component(root: ET.Element, component: Component, role: str, x: int, y: int, width: int, height: int, style: str) -> str:
    wrapper = ET.SubElement(root, "object", {"id": component.identifier, **attrs(component, role)})
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": style})
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry",
    })
    return component.identifier


def add_raw_vertex(root: ET.Element, identifier: str, value: str, x: int, y: int, width: int, height: int, style: str) -> None:
    cell_attrs = {
        "id": identifier, "value": value, "parent": "1", "vertex": "1", "style": style,
    }
    if value:
        cell_attrs.update({"labelEn": value, "labelMs": value})
    cell = ET.SubElement(root, "mxCell", cell_attrs)
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry",
    })


def add_edge(root: ET.Element, identifier: str, source: str, target: str, style: str, points: tuple[tuple[int, int], ...] = ()) -> None:
    cell = ET.SubElement(root, "mxCell", {
        "id": identifier, "value": "", "parent": "1", "edge": "1", "source": source, "target": target, "style": style,
    })
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if points:
        point_array = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in points:
            ET.SubElement(point_array, "mxPoint", {"x": str(x), "y": str(y)})


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{path.suffix.lower().lstrip('.')},{encoded}"


def component(key: str, simple_en: str, simple_ms: str, code: str, node_ids: str, files: str, *, routes: str = "", tables: str = "", hotspots: str = "") -> Component:
    return Component(
        key=key,
        identifier=f"wbs-{key}",
        simple_en=simple_en,
        simple_ms=simple_ms,
        code_en=code,
        code_ms=code,
        node_ids=node_ids,
        source_files=files,
        routes=routes,
        tables=tables,
        hotspots=hotspots,
    )


def phases() -> tuple[Phase, ...]:
    return (
        Phase(
            component("phase-planning", rich("Planning and Analysis", "Define the project before implementation"), rich("Perancangan dan Analisis", "Menetapkan projek sebelum pelaksanaan"), rich("Planning evidence", "docs/architecture/overview.md · docs/planning/ · package.json"), "wbs-planning-analysis", "docs/architecture/overview.md,docs/planning/,package.json"),
            (
                component("planning-scope", "Identify the problem, objectives and scope", "Mengenal pasti masalah, objektif dan skop", "docs/architecture/overview.md", "wbs-planning-analysis", "docs/architecture/overview.md"),
                component("planning-requirements", "Gather and analyse user requirements", "Mengumpul dan menganalisis keperluan pengguna", "apps/architecture-explorer/fyp-report-tables.js", "wbs-planning-analysis", "apps/architecture-explorer/fyp-report-tables.js", hotspots="report-tables"),
                component("planning-sources", "Analyse job portals and data sources", "Menganalisis portal pekerjaan dan sumber data", "src/config/job-sources.ts · server/lib/scrapers/", "wbs-planning-analysis,daily-index-job-sources,live-search-job-sources", "src/config/job-sources.ts,server/lib/scrapers/", routes="Maukerja,Hiredly,Ricebowl,Graduan,Jora,JobStreet,Jobstore,Careerjet API"),
                component("planning-agile", "Plan Agile iterations, risks and schedule", "Merancang lelaran Agile, risiko dan jadual", "docs/planning/ · package.json", "wbs-planning-analysis", "docs/planning/,package.json"),
            ),
        ),
        Phase(
            component("phase-design", rich("System Design", "Translate requirements into a workable design"), rich("Reka Bentuk Sistem", "Menterjemah keperluan kepada reka bentuk yang boleh dibina"), rich("Design evidence", "MyPetaApp · Express · Supabase/PostGIS · managers"), "wbs-system-design", "src/MyPetaApp.ts,server/app.ts,supabase/migrations/,src/services/supabase.ts"),
            (
                component("design-architecture", "Design the layered application architecture", "Mereka bentuk seni bina aplikasi berlapis", "src/MyPetaApp.ts · server/app.ts", "wbs-system-design,mypeta-app,express-app", "src/MyPetaApp.ts,server/app.ts"),
                component("design-data", "Design Supabase/PostGIS data structures", "Mereka bentuk struktur data Supabase/PostGIS", "supabase/migrations/ · src/services/supabase.ts", "wbs-system-design,supabase-db,supabase-module", "supabase/migrations/,src/services/supabase.ts", tables="scraped_jobs,pois,user_profiles,geo_route_cache,geo_geocode_cache"),
                component("design-ui", "Design UI/UX and map interactions", "Mereka bentuk UI/UX dan interaksi peta", "src/ui/templates.ts · MapManager", "wbs-system-design,ui-templates,map-manager", "src/ui/templates.ts,src/managers/MapManager.ts", hotspots="app-shell,map-canvas,contents-pane"),
                component("design-flows", "Design job, POI and routing flows", "Mereka bentuk aliran pekerjaan, POI dan penghalaan", "src/modes/jobs/ · POIManager · GeoNavigationManager", "wbs-system-design,job-manager,poi-manager,geo-navigation-manager", "src/modes/jobs/,src/managers/POIManager.ts,src/managers/GeoNavigationManager.ts", routes="/api/search-jobs,/api/jobs/supa,/api/geo/*", hotspots="jobs-search,map-search,map-canvas"),
            ),
        ),
        Phase(
            component("phase-development", rich("System Development", "Implement modules and integrations"), rich("Pembangunan Sistem", "Melaksanakan modul dan integrasi"), rich("Development evidence", "src/ · server/ · Supabase · GeoGateway"), "wbs-system-development", "src/,server/,supabase/"),
            (
                component("development-map", "Build MapLibre 2D and 3D map features", "Membangunkan ciri peta MapLibre 2D dan 3D", "MapManager · GeoRouteRenderer", "wbs-system-development,map-manager,geo-route-renderer", "src/managers/MapManager.ts,src/managers/GeoRouteRenderer.ts", hotspots="map-canvas"),
                component("development-jobs", "Build Live Search and Daily Index", "Membangunkan Live Search dan Daily Index", "JobFinderManager · search-jobs.ts · intel-jobs.ts", "wbs-system-development,job-manager,live-search-route,daily-index-scraper", "src/modes/jobs/manager.ts,server/routes/search-jobs.ts,server/routes/intel-jobs.ts", routes="GET /api/search-jobs,GET /api/jobs/supa", tables="scraped_jobs", hotspots="jobs-search,jobs-cards,jobs-map"),
                component("development-spatial", "Build POI, transit and spatial analytics", "Membangunkan POI, transit dan analitik spatial", "POIManager · InsightsManager", "wbs-system-development,poi-manager,insights-manager", "src/managers/POIManager.ts,src/managers/InsightsManager.ts", routes="/api/pois,/api/open-data/*", tables="pois", hotspots="map-search,map-canvas"),
                component("development-account", "Build authentication, profile and applications", "Membangunkan pengesahan, profil dan permohonan", "AuthManager · UserDashboardManager", "wbs-system-development,auth-manager,user-dashboard", "src/managers/AuthManager.ts,src/managers/UserDashboardManager.ts", tables="user_profiles,user_applications", hotspots="auth-dialog,user-dashboard"),
                component("development-integration", "Integrate Express, Supabase and GeoGateway", "Mengintegrasikan Express, Supabase dan GeoGateway", "server/app.ts · services/supabase.ts · server/geo/gateway.ts", "wbs-system-development,express-app,supabase-module,geo-gateway", "server/app.ts,src/services/supabase.ts,server/geo/gateway.ts", routes="/api/*,/api/geo/*", tables="geo_route_cache,geo_geocode_cache"),
            ),
        ),
        Phase(
            component("phase-testing", rich("Testing and Improvement", "Verify quality and feed findings back"), rich("Pengujian dan Penambahbaikan", "Mengesahkan kualiti dan menyalurkan semula penemuan"), rich("Verification evidence", "typecheck · tests · bundle budget · security guards"), "wbs-testing-improvement", "package.json,tests/,scripts/check-bundle-budget.mjs,server/middleware/requireAuth.ts"),
            (
                component("testing-automated", "Run type checks and unit tests", "Menjalankan semakan jenis dan ujian unit", "npm run typecheck · npm test", "wbs-testing-improvement", "package.json,tests/"),
                component("testing-functional", "Test functions, user flows and maps", "Menguji fungsi, aliran pengguna dan peta", "tests/ · npm run explorer:test", "wbs-testing-improvement,map-manager,job-manager", "tests/,apps/architecture-explorer/scripts/", hotspots="app-shell,map-canvas,jobs-search"),
                component("testing-resilience", "Check performance, security and failures", "Menyemak prestasi, keselamatan dan kegagalan", "npm run bundle:check · requireAuth · GeoGateway fallbacks", "wbs-testing-improvement,geo-gateway,auth-manager", "scripts/check-bundle-budget.mjs,server/middleware/requireAuth.ts,server/geo/gateway.ts"),
                component("testing-feedback", "Apply feedback-driven fixes", "Melaksanakan pembaikan berdasarkan maklum balas", "tests/ · docs/changelogs/", "wbs-testing-improvement", "tests/,docs/changelogs/"),
            ),
        ),
        Phase(
            component("phase-documentation", rich("Documentation and Evaluation", "Prepare evidence, assessment and handover"), rich("Dokumentasi dan Penilaian", "Menyediakan bukti, penilaian dan penyerahan"), rich("Report evidence", "docs/ · Explorer · FYP report · docs-site/"), "wbs-documentation-evaluation", "docs/,apps/architecture-explorer/README.md,docs-site/,vercel.json"),
            (
                component("documentation-guides", "Prepare technical and user documentation", "Menyediakan dokumentasi teknikal dan pengguna", "docs/ · apps/architecture-explorer/README.md", "wbs-documentation-evaluation", "docs/,apps/architecture-explorer/README.md"),
                component("documentation-report", "Complete the final-year project report", "Menyiapkan laporan projek tahun akhir", "External FYP DOCX · Rajah 1.8", "wbs-documentation-evaluation", "External FYP DOCX · Rajah 1.8"),
                component("documentation-evaluate", "Evaluate objectives and project results", "Menilai objektif dan hasil projek", "tests/ · docs/architecture/overview.md", "wbs-documentation-evaluation", "tests/,docs/architecture/overview.md"),
                component("documentation-handover", "Present and hand over the final project", "Membentang dan menyerahkan projek akhir", "docs-site/ · vercel.json", "wbs-documentation-evaluation", "docs-site/,vercel.json"),
            ),
        ),
    )


def new_document() -> tuple[ET.Element, ET.Element]:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja FYP Work Breakdown Structure Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaDiagramLabelMode": "simple",
        "petakerjaLayoutStandard": "fyp-work-breakdown-structure-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": PAGE_ID, "name": "PetaKerja FYP Work Breakdown Structure"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(PAGE_WIDTH), "dy": str(PAGE_HEIGHT), "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1",
        "page": "1", "pageScale": "1", "pageWidth": str(PAGE_WIDTH), "pageHeight": str(PAGE_HEIGHT),
        "math": "0", "shadow": "0", "background": "light-dark(#f7f9fc,#0b1118)",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return mxfile, root


def build_document() -> ET.Element:
    document, root = new_document()
    add_raw_vertex(root, "wbs-title", "Work Breakdown Structure / Struktur Pecahan Kerja", 250, 16, 1300, 40, TITLE)
    add_raw_vertex(root, "wbs-subtitle", "Figure 1.8 · PetaKerja Final-Year Project / Rajah 1.8 · Projek Tahun Akhir PetaKerja", 250, 54, 1300, 28, SUBTITLE)

    root_component = component(
        "project", rich("PetaKerja Application Project", "Five coordinated Agile workstreams"), rich("Projek Aplikasi PetaKerja", "Lima aliran kerja Agile yang saling berkaitan"),
        rich("4kmal/petakerja", "main · Vite + TypeScript + Express + Supabase"), "wbs-project,mypeta-app", "package.json,docs/architecture/overview.md", hotspots="app-shell",
    )
    root_id = add_component(root, root_component, "project", 660, 88, 480, 104, ROOT_BOX)
    logo = REPOSITORY_ROOT / "public" / "icon" / "android-chrome-192x192.png"
    add_raw_vertex(root, "wbs-logo-petakerja", "", 688, 108, 64, 64, IMAGE + f"image={image_data_uri(logo)};")

    phase_x = (55, 390, 725, 1060, 1395)
    phase_y = 275
    phase_width = 300
    phase_height = 92
    task_x_offset = 32
    task_width = 268
    task_height = 112
    task_start_y = 420
    task_gap = 28

    for phase_index, (phase, x) in enumerate(zip(phases(), phase_x), 1):
        phase_id = add_component(root, phase.component, "phase", x, phase_y, phase_width, phase_height, PHASE_STYLES[phase_index - 1])
        add_raw_vertex(root, f"wbs-phase-number-{phase_index}", str(phase_index), x + 10, phase_y + 10, 28, 28, NUMBER)
        phase_center = x + phase_width // 2
        add_edge(
            root,
            f"wbs-edge-project-phase-{phase_index}",
            root_id,
            phase_id,
            EDGE_ROOT,
            ((900, 230), (phase_center, 230)),
        )

        trunk_x = x + 13
        for task_index, task in enumerate(phase.tasks, 1):
            task_y = task_start_y + (task_index - 1) * (task_height + task_gap)
            task_id = add_component(root, task, "work-package", x + task_x_offset, task_y, task_width, task_height, TASK_STYLES[phase_index - 1])
            add_edge(
                root,
                f"wbs-edge-phase-{phase_index}-task-{task_index}",
                phase_id,
                task_id,
                EDGE_TASK,
                ((phase_center, 392), (trunk_x, 392), (trunk_x, task_y + task_height // 2)),
            )
    return document


def validate(document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise ValueError(f"missing page {PAGE_ID}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(PAGE_WIDTH), str(PAGE_HEIGHT)):
        raise ValueError("canvas must be exactly 1800 x 1350")
    wrappers = diagram.findall(".//object")
    edges = [cell for cell in diagram.findall(".//mxCell") if cell.get("edge") == "1"]
    if len(wrappers) != 27 or len(edges) != 26:
        raise ValueError(f"expected 27 components and 26 edges, found {len(wrappers)} and {len(edges)}")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if not all(keys) or len(keys) != len(set(keys)):
        raise ValueError("component keys must be present and unique")
    for wrapper in wrappers:
        required = ("labelEn", "labelMs", "simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs", "nodeIds", "sourceFiles")
        if any(not wrapper.get(name) for name in required):
            raise ValueError(f"{wrapper.get('id')} is missing bilingual label or implementation metadata")
        if wrapper.get("simpleLabelEn") == wrapper.get("codeLabelEn"):
            raise ValueError(f"{wrapper.get('id')} does not change between Simple and Code")
    vertices = {
        wrapper.get("id", "") for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    for edge in edges:
        if edge.get("source") not in vertices or edge.get("target") not in vertices:
            raise ValueError(f"{edge.get('id')} has a disconnected endpoint")
        if "endArrow=none" not in edge.get("style", ""):
            raise ValueError(f"{edge.get('id')} is not arrow-free")
    image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
    if len(image_cells) != 1 or "image=data:image/" not in image_cells[0].get("style", ""):
        raise ValueError("the root must contain exactly one embedded local PetaKerja mark")
    for cell in diagram.findall(".//mxCell"):
        style = cell.get("style", "")
        if "gradientColor=" in style or "image=http" in style:
            raise ValueError(f"{cell.get('id')} uses a forbidden style or remote image")


def main() -> None:
    document = build_document()
    validate(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(document, space="  ")
    ET.ElementTree(document).write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
