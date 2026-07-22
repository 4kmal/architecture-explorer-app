#!/usr/bin/env python3
"""Focused deterministic checks for the logo-based Layered Architecture variant."""

from __future__ import annotations

import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "architecture-visual-stack.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "architecture-visual-stack.svg"
GENERATOR = ROOT / "scripts" / "generate-architecture-visual-stack.py"
PAGE_ID = "petakerja_layered_architecture_visual_stack"

EXPECTED_KEYS = {
    "view", "application", "clients", "api", "data",
    "flow-interaction", "flow-manager", "flow-api", "flow-data", "flow-return",
    "mvc-view", "mvc-controller", "mvc-model", "note-mvc", "note-reading",
}
EXPECTED_LOGOS = {
    "petakerja", "vite", "typescript-view", "maplibre", "typescript-app",
    "supabase-client", "vercel", "express", "better-auth", "supabase-data", "postgresql",
}


def serialized(document: ET.Element) -> bytes:
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="utf-8", xml_declaration=True).replace(b"\r\n", b"\n")


def main() -> int:
    errors: list[str] = []
    generated = runpy.run_path(str(GENERATOR))
    expected_document = generated["build_document"]()
    generated["validate"](expected_document)

    if not SOURCE.exists():
        errors.append("missing canonical architecture-visual-stack.drawio")
    else:
        document = ET.parse(SOURCE).getroot()
        diagram = document.find("diagram")
        if diagram is None or diagram.get("id") != PAGE_ID:
            errors.append(f"missing exact page id {PAGE_ID}")
        else:
            model = diagram.find("mxGraphModel")
            if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1920", "900"):
                errors.append("canvas is not exactly 1920 x 900")

            wrappers = diagram.findall(".//object")
            keyed = {wrapper.get("petakerjaKey", ""): wrapper for wrapper in wrappers}
            if "" in keyed or len(keyed) != len(wrappers):
                errors.append("component keys are missing or duplicated")
            for key in EXPECTED_KEYS:
                if f"architecture-visual-stack/{key}" not in keyed:
                    errors.append(f"missing stable component key {key}")

            tiers = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "tier"]
            flows = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "flow"]
            mappings = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "mvc-mapping"]
            if len(tiers) != 5:
                errors.append(f"expected five tiers, found {len(tiers)}")
            if len(flows) != 5:
                errors.append(f"expected five flows, found {len(flows)}")
            if len(mappings) != 3:
                errors.append(f"expected three MVC mapping labels, found {len(mappings)}")

            for wrapper in (*tiers, *flows):
                fields = ("labelEn", "labelMs", "simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs")
                if any(not wrapper.get(field) for field in fields):
                    errors.append(f"{wrapper.get('id')} is missing bilingual Simple/Code labels")
                if wrapper.get("simpleLabelEn") == wrapper.get("codeLabelEn"):
                    errors.append(f"{wrapper.get('id')} does not visibly change between Simple and Code")

            vertices = {
                wrapper.get("id", "") for wrapper in wrappers
                if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
            }
            for flow in flows:
                cell = flow.find("mxCell")
                if cell is None or cell.get("source") not in vertices or cell.get("target") not in vertices:
                    errors.append(f"{flow.get('id')} has a disconnected endpoint")

            image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
            if len(image_cells) != 11:
                errors.append(f"expected 11 embedded logos, found {len(image_cells)}")
            raw_ids = {cell.get("id", "") for cell in diagram.findall(".//mxCell")}
            for logo in EXPECTED_LOGOS:
                if f"avs-logo-{logo}" not in raw_ids:
                    errors.append(f"missing embedded logo {logo}")
            for cell in image_cells:
                style = cell.get("style", "")
                if "image=data:image/" not in style or re.search(r"image=https?", style, re.I):
                    errors.append(f"{cell.get('id')} does not use a local embedded image")

            raw = SOURCE.read_text(encoding="utf-8")
            if "gradientColor=" in raw:
                errors.append("gradients are not allowed")
            if re.search(r"(?:image=|href=|xlink:href=)https?", raw, re.I):
                errors.append("source contains a remote image dependency")
            for phrase in ("MVC-inspired, not strict MVC", "Berinspirasikan MVC, bukan MVC ketat", "MyPetaApp", "public.scraped_jobs", "fetch('/api/*')"):
                if phrase not in raw:
                    errors.append(f"source is missing expected explanation or code label: {phrase}")

            expected_nodes = {
                "avs-tier-view": "browser,index-html,main-ts,ui-templates,maplibre-gl",
                "avs-tier-application": "mypeta-app,map-manager,poi-manager,search-manager,job-manager,geo-navigation-manager,auth-manager",
                "avs-tier-clients": "supabase-module,jobs-api,geo-api,open-data-api,auth-client",
                "avs-tier-api": "vercel-runtime,express-app,better-auth",
                "avs-tier-data": "supabase-db,job-entity,poi-entity,data-gov",
            }
            for identifier, node_ids in expected_nodes.items():
                wrapper = diagram.find(f".//object[@id='{identifier}']")
                if wrapper is None or wrapper.get("nodeIds") != node_ids:
                    errors.append(f"{identifier} has incorrect graph metadata")

        if serialized(expected_document) != SOURCE.read_bytes().replace(b"\r\n", b"\n"):
            errors.append("checked-in source is not deterministic generator output")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 5000:
        errors.append("generated SVG preview is missing")
    else:
        preview = PREVIEW.read_text(encoding="utf-8")
        if len(re.findall(r"<image\b", preview, re.I)) < 11:
            errors.append("SVG preview does not retain the embedded logo roster")
        if re.search(r"(?:href|xlink:href)=['\"]https?", preview, re.I):
            errors.append("SVG preview contains a remote dependency")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    manifest_entry = manifest.get("diagrams", {}).get("architecture-visual-stack", {})
    if manifest_entry != {
        "xml": "assets/editor/architecture-visual-stack.drawio",
        "svg": "assets/diagrams/architecture-visual-stack.svg",
        "pageId": PAGE_ID,
        "title": "PetaKerja Layered Architecture — Visual Stack",
        "diagramType": "architecture",
    }:
        errors.append("workspace manifest registration is incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    package = (ROOT / "package.json").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")

    try:
        order = [architecture.index(f"id: '{diagram_id}', title:") for diagram_id in ("architecture-visual-stack", "architecture", "architecture-original")]
        if order != sorted(order):
            errors.append("Layered Architecture variant order is incorrect")
    except ValueError:
        errors.append("Layered Architecture variants are not all registered")
    for marker in (
        "variantLabelEn: 'Visual Stack', variantLabelMs: 'Susunan Visual'",
        "variantLabelEn: 'Detailed Layers', variantLabelMs: 'Lapisan Terperinci'",
        "variantLabelEn: 'Original', variantLabelMs: 'Asal'",
        "variantRecommended: true",
        "PetaKerja does not follow strict textbook MVC.",
        "PetaKerja tidak menggunakan MVC buku teks secara ketat.",
    ):
        if marker not in architecture:
            errors.append(f"architecture data is missing {marker}")

    registrations = (
        ("app.js", app, "'architecture-visual-stack': 'layers-2'"),
        ("translations.js", translations, "'architecture-visual-stack': ['Layered architecture — Visual Stack'"),
        ("editor-core.js", editor, "assets/editor/architecture-visual-stack.drawio"),
        ("build-diagram-assets.py", builder, '"architecture-visual-stack": (ARCHITECTURE_VISUAL_STACK_SOURCE, 0, "architecture-visual-stack.svg")'),
        ("package.json", package, "python scripts/test-architecture-visual-stack.py"),
        ("README.md", readme, "### Layered Architecture variants"),
        ("diagram-assets.js", bundle, '"architecture-visual-stack"'),
    )
    for filename, text, marker in registrations:
        if marker not in text:
            errors.append(f"{filename} is missing registration {marker}")
    if '"architecture-visual-stack"' in bundle and '"supportsLabelModes":true' not in bundle:
        errors.append("generated asset bundle does not expose Simple/Code capability")

    for logo_file in ("vite.svg", "postgresql.svg"):
        path = ROOT / "assets" / "brands" / logo_file
        if not path.exists() or path.stat().st_size < 150:
            errors.append(f"missing local brand asset {logo_file}")

    if errors:
        print("Architecture Visual Stack checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Architecture Visual Stack checks passed for 5 tiers, 5 flows and 11 embedded logos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
