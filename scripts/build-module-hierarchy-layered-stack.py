"""Generate the editable PetaKerja layered Module Hierarchy diagram."""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from paths import DRAWIO


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "module-hierarchy-layered-stack.drawio"
SVG = ROOT / "assets" / "diagrams" / "module-hierarchy-layered-stack.svg"
PAGE_ID = "petakerja_module_hierarchy_layered_stack"
WIDTH = 1900
HEIGHT = 1180


@dataclass(frozen=True)
class Label:
    simple_en: str
    simple_ms: str
    code_en: str
    code_ms: str


LABELS = {
    "core-shell": Label("Starts the application and workspace", "Memulakan aplikasi dan ruang kerja", "src/main.ts → MyPetaApp + templates", "src/main.ts → MyPetaApp + templat"),
    "core-map": Label("Controls and renders the interactive map", "Mengawal dan memaparkan peta interaktif", "MapManager + MapLibre GL JS", "MapManager + MapLibre GL JS"),
    "core-poi": Label("Searches places, POIs and categories", "Mencari tempat, POI dan kategori", "POIManager + SearchManager + CategoryManager", "POIManager + SearchManager + CategoryManager"),
    "jobs-manager": Label("Coordinates job search modes", "Menyelaras mod carian pekerjaan", "JobFinderManager", "JobFinderManager"),
    "jobs-modes": Label("Daily Index, Pipeline Index and Live Search", "Indeks Harian, Indeks Pipeline dan Carian Langsung", "searchSupaJobs() + searchJobs() + pipeline API", "searchSupaJobs() + searchJobs() + API pipeline"),
    "jobs-markers": Label("Shows job cards and map markers", "Memaparkan kad pekerjaan dan penanda peta", "JobFinderManager + markers.ts", "JobFinderManager + markers.ts"),
    "account-auth": Label("Signs users in and protects sessions", "Log masuk pengguna dan melindungi sesi", "AuthManager + Better Auth", "AuthManager + Better Auth"),
    "account-bridge": Label("Links sign-in identity to the app profile", "Menghubungkan identiti log masuk kepada profil aplikasi", "public.users.better_auth_user_id", "public.users.better_auth_user_id"),
    "account-admin": Label("Manages configuration and user status", "Mengurus konfigurasi dan status pengguna", "AdminDashboardManager + /api/admin/*", "AdminDashboardManager + /api/admin/*"),
    "analysis-insights": Label("Loads national data and insights", "Memuatkan data negara dan cerapan", "InsightsManager + OpenDataAPI", "InsightsManager + OpenDataAPI"),
    "analysis-highlight": Label("Highlights selected areas on the map", "Menyorot kawasan dipilih pada peta", "HighlightManager + highlight layer", "HighlightManager + lapisan sorotan"),
    "analysis-chatbot": Label("Provides AI assistance", "Menyediakan bantuan AI", "ChatbotManager + /api/assistant/*", "ChatbotManager + /api/assistant/*"),
}


NODES = (
    ("application-root", "PetaKerja", "PetaKerja", 665, 154, 220, 50, "root", None),
    ("module-core", "Core Application", "Aplikasi Teras", 205, 320, 230, 56, "module-blue", None),
    ("module-jobs", "Job Search Module", "Modul Carian Pekerjaan", 475, 320, 230, 56, "module-violet", None),
    ("module-account", "Accounts and Administration", "Akaun dan Pentadbiran", 745, 320, 230, 56, "module-amber", None),
    ("module-analysis", "Analytics and Assistance", "Analitik dan Bantuan", 1015, 320, 230, 56, "module-green", None),
    ("core-shell", "", "", 155, 535, 185, 68, "blue", "core-shell"),
    ("jobs-manager", "", "", 355, 535, 185, 68, "violet", "jobs-manager"),
    ("account-auth", "", "", 555, 535, 185, 68, "amber", "account-auth"),
    ("account-admin", "", "", 755, 535, 185, 68, "amber", "account-admin"),
    ("analysis-insights", "", "", 955, 535, 185, 68, "green", "analysis-insights"),
    ("analysis-chatbot", "", "", 1155, 535, 185, 68, "green", "analysis-chatbot"),
    ("core-map", "", "", 150, 815, 220, 68, "blue", "core-map"),
    ("core-poi", "", "", 150, 915, 220, 68, "blue", "core-poi"),
    ("jobs-modes", "", "", 405, 815, 220, 68, "violet", "jobs-modes"),
    ("jobs-markers", "", "", 405, 915, 220, 68, "violet", "jobs-markers"),
    ("account-bridge", "", "", 720, 865, 240, 68, "amber", "account-bridge"),
    ("analysis-highlight", "", "", 1055, 865, 240, 68, "green", "analysis-highlight"),
)


EDGES = (
    ("hierarchy-root-core", "application-root", "module-core"),
    ("hierarchy-root-jobs", "application-root", "module-jobs"),
    ("hierarchy-root-account", "application-root", "module-account"),
    ("hierarchy-root-analysis", "application-root", "module-analysis"),
    ("hierarchy-core-shell", "module-core", "core-shell"),
    ("hierarchy-core-map", "core-shell", "core-map"),
    ("hierarchy-core-poi", "core-map", "core-poi"),
    ("hierarchy-jobs-manager", "module-jobs", "jobs-manager"),
    ("hierarchy-jobs-modes", "jobs-manager", "jobs-modes"),
    ("hierarchy-jobs-markers", "jobs-modes", "jobs-markers"),
    ("hierarchy-account-auth", "module-account", "account-auth"),
    ("hierarchy-account-admin", "module-account", "account-admin"),
    ("hierarchy-account-bridge", "account-auth", "account-bridge"),
    ("hierarchy-analysis-insights", "module-analysis", "analysis-insights"),
    ("hierarchy-analysis-chatbot", "module-analysis", "analysis-chatbot"),
    ("hierarchy-analysis-highlight", "analysis-insights", "analysis-highlight"),
)


DEPENDENCIES = (
    ("Interactive map", "JobFinderManager", "Map workspace", "Peta interaktif", "JobFinderManager", "Ruang kerja peta"),
    ("Interactive map", "InsightsManager / OpenDataAPI", "Location context", "Peta interaktif", "InsightsManager / OpenDataAPI", "Konteks lokasi"),
    ("Profile bridge", "JobFinderManager", "Save job status", "Jambatan profil", "JobFinderManager", "Simpan status pekerjaan"),
    ("Better Auth", "ChatbotManager", "Protected AI functions", "Better Auth", "ChatbotManager", "Fungsi AI terlindung"),
)


def style(**values: str) -> str:
    return ";".join(f"{key}={value}" for key, value in values.items()) + ";"


def add_object(root: ET.Element, identifier: str, label_en: str, label_ms: str, x: float, y: float,
               width: float, height: float, cell_style: str, *, key: str | None = None,
               modes: Label | None = None, pointer_events: bool = True) -> str:
    attrs = {"id": identifier, "label": modes.simple_en if modes else label_en, "labelEn": label_en, "labelMs": label_ms}
    if key:
        attrs["petakerjaKey"] = f"modules/{key}"
    if modes:
        attrs.update({
            "labelEn": modes.simple_en, "labelMs": modes.simple_ms,
            "simpleLabelEn": modes.simple_en, "simpleLabelMs": modes.simple_ms,
            "codeLabelEn": modes.code_en, "codeLabelMs": modes.code_ms,
        })
    wrapper = ET.SubElement(root, "object", attrs)
    if not pointer_events:
        cell_style += "pointerEvents=0;"
    cell = ET.SubElement(wrapper, "mxCell", {"parent": "1", "vertex": "1", "style": cell_style})
    ET.SubElement(cell, "mxGeometry", {
        "x": f"{x:g}", "y": f"{y:g}", "width": f"{width:g}", "height": f"{height:g}", "as": "geometry",
    })
    return identifier


def build() -> ET.ElementTree:
    mxfile = ET.Element("mxfile", {
        "host": "Electron", "agent": "PetaKerja Architecture Explorer", "version": "27.0.2",
        "petakerjaDiagramLabelMode": "simple", "petakerjaProjectionLanguage": "en",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": PAGE_ID, "name": "PetaKerja Module Hierarchy - Layered Stack",
        "petakerjaRevision": "2026-07-22-layered-stack-v1",
    })
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": str(WIDTH), "dy": str(HEIGHT), "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(WIDTH), "pageHeight": str(HEIGHT), "math": "0", "shadow": "0",
        "background": "light-dark(#fbfcfe,#0b1118)",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    add_object(root, "diagram-title", "PetaKerja Module Hierarchy — Layered Stack", "Hierarki Modul PetaKerja — Susunan Bertingkat", 80, 20, 1280, 38,
               "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=24;fontStyle=1;fontColor=light-dark(#172033,#f3f6fb);", pointer_events=False)
    add_object(root, "diagram-subtitle", "Broad ownership at the top; implementation responsibilities and outcomes below.", "Pemilikan umum di atas; tanggungjawab pelaksanaan dan hasil di bawah.", 80, 58, 1280, 28,
               "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontColor=light-dark(#475467,#c5cedb);", pointer_events=False)

    layers = (
        ("layer-product", "1 · PRODUCT ROOT", "1 · AKAR PRODUK", 450, 105, 650, 120, 44, "#eef5ff", "#17263a", "#3d6f9e", "#8fb7df"),
        ("layer-modules", "2 · MODULE FAMILIES", "2 · KELUARGA MODUL", 150, 250, 1160, 175, 54, "#f5f0ff", "#2b2140", "#6941c6", "#b9a2ff"),
        ("layer-coordinators", "3 · MANAGERS AND BOUNDARIES", "3 · PENGURUS DAN SEMPADAN", 100, 450, 1260, 240, 62, "#fff7df", "#3a2e16", "#9a6700", "#f4c95d"),
        ("layer-capabilities", "4 · CAPABILITIES AND OUTPUTS", "4 · KEUPAYAAN DAN HASIL", 50, 720, 1360, 310, 70, "#ecfdf3", "#133221", "#1f7a4d", "#72d6a1"),
    )
    for identifier, en, ms, x, y, width, height, size, light_fill, dark_fill, light_stroke, dark_stroke in layers:
        add_object(root, identifier, en, ms, x, y, width, height,
                   style(shape="trapezoid", perimeter="trapezoidPerimeter", fixedSize="1", size=str(size), whiteSpace="wrap", html="1",
                         align="center", verticalAlign="top", spacingTop="12", fontFamily="Arial", fontSize="15", fontStyle="1",
                         fontColor="light-dark(#172033,#f3f6fb)", fillColor=f"light-dark({light_fill},{dark_fill})",
                         strokeColor=f"light-dark({light_stroke},{dark_stroke})", strokeWidth="2"), pointer_events=False)

    card_styles = {
        "root": ("light-dark(#17263a,#eef5ff)", "light-dark(#3d6f9e,#8fb7df)", "light-dark(#ffffff,#172033)", "16"),
        "module-blue": ("light-dark(#eef5ff,#17263a)", "light-dark(#3d6f9e,#8fb7df)", "light-dark(#172033,#f3f6fb)", "13"),
        "module-violet": ("light-dark(#f5f0ff,#2b2140)", "light-dark(#6941c6,#b9a2ff)", "light-dark(#172033,#f3f6fb)", "13"),
        "module-amber": ("light-dark(#fff7df,#3a2e16)", "light-dark(#9a6700,#f4c95d)", "light-dark(#172033,#f3f6fb)", "13"),
        "module-green": ("light-dark(#ecfdf3,#133221)", "light-dark(#1f7a4d,#72d6a1)", "light-dark(#172033,#f3f6fb)", "13"),
        "blue": ("light-dark(#ffffff,#1c222c)", "light-dark(#3d6f9e,#8fb7df)", "light-dark(#172033,#f3f6fb)", "11"),
        "violet": ("light-dark(#ffffff,#1c222c)", "light-dark(#6941c6,#b9a2ff)", "light-dark(#172033,#f3f6fb)", "11"),
        "amber": ("light-dark(#ffffff,#1c222c)", "light-dark(#9a6700,#f4c95d)", "light-dark(#172033,#f3f6fb)", "11"),
        "green": ("light-dark(#ffffff,#1c222c)", "light-dark(#1f7a4d,#72d6a1)", "light-dark(#172033,#f3f6fb)", "11"),
    }
    for key, label_en, label_ms, x, y, width, height, role, component_key in NODES:
        fill, stroke, font, font_size = card_styles[role]
        add_object(root, f"modules-layered-stack-{key}", label_en, label_ms, x, y, width, height,
                   style(rounded="1", arcSize="8", whiteSpace="wrap", html="1", align="center", verticalAlign="middle", spacing="8",
                         fontFamily="Arial", fontSize=font_size, fontStyle="1", fontColor=font, fillColor=fill, strokeColor=stroke, strokeWidth="2"),
                   key=component_key, modes=LABELS.get(component_key))

    node_ids = {key: f"modules-layered-stack-{key}" for key, *_rest in NODES}
    for identifier, source, target in EDGES:
        wrapper = ET.SubElement(root, "object", {"id": f"modules-layered-stack-{identifier}", "label": "", "petakerjaRelation": "structural"})
        cell = ET.SubElement(wrapper, "mxCell", {
            "parent": "1", "edge": "1", "source": node_ids[source], "target": node_ids[target],
            "style": style(edgeStyle="orthogonalEdgeStyle", rounded="0", orthogonalLoop="1", jettySize="auto", html="1",
                           endArrow="none", strokeWidth="2", strokeColor="light-dark(#475467,#b8c2d0)"),
        })
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    add_object(root, "modules-layered-stack-reading", "HOW TO READ", "CARA MEMBACA", 1450, 110, 380, 145,
               style(rounded="1", arcSize="8", whiteSpace="wrap", html="1", align="left", verticalAlign="top", spacingTop="18", spacingLeft="18",
                     fontFamily="Arial", fontSize="15", fontStyle="1", fontColor="light-dark(#ffffff,#f5f7fa)", fillColor="light-dark(#172033,#0b1016)", strokeColor="light-dark(#172033,#596579)", strokeWidth="2"), pointer_events=False)
    add_object(root, "modules-layered-stack-reading-body", "Read downward: product → module family → coordinator → user-facing capability.", "Baca ke bawah: produk → keluarga modul → penyelaras → keupayaan pengguna.", 1470, 160, 340, 70,
               "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontColor=light-dark(#ffffff,#f5f7fa);", pointer_events=False)

    add_object(root, "modules-layered-stack-dependencies", "CROSS-MODULE DEPENDENCIES", "KEBERGANTUNGAN SILANG MODUL", 1450, 285, 380, 425,
               style(rounded="1", arcSize="8", whiteSpace="wrap", html="1", align="left", verticalAlign="top", spacingTop="16", spacingLeft="16",
                     fontFamily="Arial", fontSize="14", fontStyle="1", fontColor="light-dark(#172033,#f3f6fb)", fillColor="light-dark(#f8fafc,#151a22)", strokeColor="light-dark(#98a2b3,#7d8796)", strokeWidth="1"), pointer_events=False)
    for index, (source_en, target_en, label_en, source_ms, target_ms, label_ms) in enumerate(DEPENDENCIES):
        add_object(root, f"modules-layered-stack-dependency-{index + 1}", f"{source_en} → {target_en}\n{label_en}", f"{source_ms} → {target_ms}\n{label_ms}", 1470, 335 + index * 86, 340, 66,
                   style(rounded="1", arcSize="6", whiteSpace="wrap", html="1", align="center", verticalAlign="middle", spacing="8", fontFamily="Arial",
                         fontSize="11", fontColor="light-dark(#344054,#d8e0eb)", fillColor="light-dark(#ffffff,#1c222c)", strokeColor="light-dark(#667085,#aeb7c7)", strokeWidth="1"), pointer_events=False)

    add_object(root, "modules-layered-stack-footer", "Simple explains responsibility. Code shows the exact implementation identifiers without changing the hierarchy.", "Ringkas menerangkan tanggungjawab. Kod menunjukkan pengecam pelaksanaan tepat tanpa mengubah hierarki.", 90, 1080, 1740, 38,
               "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=11;fontColor=light-dark(#667085,#aeb8c8);", pointer_events=False)
    return ET.ElementTree(mxfile)


def validate(tree: ET.ElementTree) -> None:
    root = tree.getroot()
    page = root.find("diagram")
    model = page.find("mxGraphModel") if page is not None else None
    wrappers = page.findall(".//object") if page is not None else []
    keyed = [item for item in wrappers if item.get("petakerjaKey", "").startswith("modules/")]
    structural = [item for item in wrappers if item.get("petakerjaRelation") == "structural"]
    if page is None or page.get("id") != PAGE_ID:
        raise ValueError("Layered Module Hierarchy page id drifted")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(WIDTH), str(HEIGHT)):
        raise ValueError("Layered Module Hierarchy canvas must remain 1900x1180")
    if len(keyed) != 12 or len(structural) != 16:
        raise ValueError("Layered Module Hierarchy must contain 12 mapped responsibilities and 16 hierarchy edges")
    keys = {item.get("petakerjaKey") for item in keyed}
    if keys != {f"modules/{key}" for key in LABELS}:
        raise ValueError("Layered Module Hierarchy stable component keys drifted")
    for item in keyed:
        if not all(item.get(name) for name in ("simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs")):
            raise ValueError(f"Missing bilingual label-mode metadata on {item.get('id')}")
    xml = ET.tostring(root, encoding="unicode")
    if "gradientColor" in xml or "data:image" in xml or "http://" in xml or "https://" in xml:
        raise ValueError("Layered Module Hierarchy must not use gradients or remote/embedded images")


def main() -> None:
    tree = build()
    validate(tree)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SVG.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(SOURCE, encoding="utf-8", xml_declaration=True)
    if not DRAWIO.exists():
        raise FileNotFoundError(DRAWIO)
    subprocess.run([str(DRAWIO), "--export", "--format", "svg", "--page-index", "0", "--output", str(SVG), str(SOURCE)], check=True)
    print(f"Generated {SOURCE.relative_to(ROOT)} and {SVG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
