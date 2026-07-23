#!/usr/bin/env python3
"""Focused deterministic checks for the FYP Work Breakdown Structure."""

from __future__ import annotations

import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "fyp-report" / "work-breakdown-structure.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "fyp-report" / "work-breakdown-structure.svg"
GENERATOR = ROOT / "scripts" / "generate-fyp-work-breakdown-structure.py"
PAGE_ID = "petakerja_fyp_work_breakdown_structure"
DIAGRAM_ID = "fyp-work-breakdown-structure"


def serialized(document: ET.Element) -> bytes:
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="utf-8", xml_declaration=True).replace(b"\r\n", b"\n")


def main() -> int:
    errors: list[str] = []
    generated = runpy.run_path(str(GENERATOR))
    expected_document = generated["build_document"]()
    generated["validate"](expected_document)

    if not SOURCE.exists():
        errors.append("missing canonical work-breakdown-structure.drawio")
    else:
        document = ET.parse(SOURCE).getroot()
        diagram = document.find("diagram")
        if diagram is None or diagram.get("id") != PAGE_ID:
            errors.append(f"missing exact page id {PAGE_ID}")
        else:
            model = diagram.find("mxGraphModel")
            if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1800", "1350"):
                errors.append("canvas is not exactly 1800 x 1350")

            wrappers = diagram.findall(".//object")
            phases = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "phase"]
            packages = [wrapper for wrapper in wrappers if wrapper.get("architectureRole") == "work-package"]
            edges = [cell for cell in diagram.findall(".//mxCell") if cell.get("edge") == "1"]
            if len(wrappers) != 27:
                errors.append(f"expected 27 selectable components, found {len(wrappers)}")
            if len(phases) != 5 or len(packages) != 21:
                errors.append(f"expected five phases and 21 work packages, found {len(phases)} and {len(packages)}")
            if len(edges) != 26:
                errors.append(f"expected 26 hierarchy connections, found {len(edges)}")

            keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
            if not all(keys) or len(keys) != len(set(keys)):
                errors.append("stable component keys are missing or duplicated")
            required_keys = {
                "project", "phase-planning", "phase-design", "phase-development", "phase-testing", "phase-documentation",
                "planning-scope", "design-data", "development-jobs", "testing-resilience", "documentation-report",
            }
            for key in required_keys:
                if f"{DIAGRAM_ID}/{key}" not in keys:
                    errors.append(f"missing stable component key {key}")

            vertex_ids = {wrapper.get("id", "") for wrapper in wrappers}
            for edge in edges:
                if edge.get("source") not in vertex_ids or edge.get("target") not in vertex_ids:
                    errors.append(f"{edge.get('id')} has a disconnected endpoint")
                style = edge.get("style", "")
                if "edgeStyle=orthogonalEdgeStyle" not in style or "endArrow=none" not in style:
                    errors.append(f"{edge.get('id')} is not an orthogonal arrow-free hierarchy connection")

            for wrapper in wrappers:
                fields = (
                    "labelEn", "labelMs", "simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs",
                    "petakerjaKey", "nodeIds", "sourceFiles",
                )
                if any(not wrapper.get(field) for field in fields):
                    errors.append(f"{wrapper.get('id')} is missing bilingual label or implementation metadata")
                if wrapper.get("simpleLabelEn") == wrapper.get("codeLabelEn"):
                    errors.append(f"{wrapper.get('id')} does not visibly change between Simple and Code")
                cell = wrapper.find("mxCell")
                geometry = cell.find("mxGeometry") if cell is not None else None
                if geometry is None or any(geometry.get(name) is None for name in ("x", "y", "width", "height")):
                    errors.append(f"{wrapper.get('id')} has unstable or incomplete geometry")

            image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
            if len(image_cells) != 1 or image_cells[0].get("id") != "wbs-logo-petakerja":
                errors.append("expected exactly one embedded PetaKerja logo in the root")
            for cell in image_cells:
                style = cell.get("style", "")
                if "image=data:image/" not in style or re.search(r"image=https?", style, re.I):
                    errors.append("PetaKerja logo is not embedded locally")

            raw = SOURCE.read_text(encoding="utf-8")
            if "gradientColor=" in raw:
                errors.append("gradients are not allowed")
            if re.search(r"(?:image=|href=|xlink:href=)https?", raw, re.I):
                errors.append("source contains a remote dependency")
            for phrase in (
                "Planning and Analysis", "Perancangan dan Analisis", "System Development", "Pembangunan Sistem",
                "docs/architecture/overview.md", "supabase/migrations/", "npm run typecheck", "External FYP DOCX · Rajah 1.8",
            ):
                if phrase not in raw:
                    errors.append(f"source is missing expected Simple/Code content: {phrase}")

        if serialized(expected_document) != SOURCE.read_bytes().replace(b"\r\n", b"\n"):
            errors.append("checked-in source is not deterministic generator output")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 5000:
        errors.append("generated SVG preview is missing")
    else:
        preview = PREVIEW.read_text(encoding="utf-8")
        if len(re.findall(r"<image\b", preview, re.I)) < 1:
            errors.append("SVG preview does not retain the embedded PetaKerja logo")
        if re.search(r"(?:href|xlink:href)=['\"]https?", preview, re.I):
            errors.append("SVG preview contains a remote dependency")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    expected_manifest = {
        "xml": "assets/editor/fyp-report/work-breakdown-structure.drawio",
        "svg": "assets/diagrams/fyp-report/work-breakdown-structure.svg",
        "pageId": PAGE_ID,
        "title": "PetaKerja FYP Work Breakdown Structure",
        "diagramType": "hierarchy",
    }
    if manifest.get("diagrams", {}).get(DIAGRAM_ID) != expected_manifest:
        errors.append("workspace manifest registration is incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    package = (ROOT / "package.json").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")

    registrations = (
        ("architecture-data.js", architecture, "collectionId: 'fyp-report', collectionGroupId: 'project-planning', collectionOrder: 1"),
        ("architecture-data.js", architecture, "collectionGroupId: 'report-tables', collectionOrder: 2"),
        ("architecture-data.js", architecture, "Figure 1.8 divides the PetaKerja project into five coordinated Agile workstreams"),
        ("architecture-data.js", architecture, "Rajah 1.8 memecahkan projek PetaKerja kepada lima aliran kerja Agile"),
        ("app.js", app, "'fyp-work-breakdown-structure': 'folder-tree'"),
        ("app.js", app, "'fyp-report': Object.freeze(["),
        ("app.js", app, "countSingularKey: 'ui.collectionTable'"),
        ("translations.js", translations, "'Laporan FYP': 'FYP Report'"),
        ("translations.js", translations, "'fyp-work-breakdown-structure': ['Work Breakdown Structure'"),
        ("editor-core.js", editor, "assets/editor/fyp-report/work-breakdown-structure.drawio?v=20260723-1"),
        ("build-diagram-assets.py", builder, '"fyp-work-breakdown-structure": (FYP_WORK_BREAKDOWN_STRUCTURE_SOURCE, 0, "fyp-report/work-breakdown-structure.svg")'),
        ("package.json", package, "python scripts/test-fyp-work-breakdown-structure.py"),
        ("README.md", readme, "### FYP Report collection"),
        ("diagram-assets.js", bundle, '"fyp-work-breakdown-structure"'),
    )
    for filename, text, marker in registrations:
        if marker not in text:
            errors.append(f"{filename} is missing registration {marker}")
    if '"fyp-work-breakdown-structure"' in bundle and '"supportsLabelModes":true' not in bundle:
        errors.append("generated asset bundle does not expose Simple/Code capability")

    try:
        order = [architecture.index(f"id: '{diagram_id}', title:") for diagram_id in (DIAGRAM_ID, "fyp-kamus-data", "fyp-use-case-specification")]
        if order != sorted(order):
            errors.append("FYP Report collection ordering is incorrect")
    except ValueError:
        errors.append("FYP Report resources are not all registered")

    if errors:
        print("FYP Work Breakdown Structure checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("FYP Work Breakdown Structure checks passed for 27 components, 26 edges and the mixed FYP collection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
