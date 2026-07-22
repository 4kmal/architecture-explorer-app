#!/usr/bin/env python3
"""Regression checks for the editable Daily Index workflow diagram."""

from __future__ import annotations

import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "daily-index-workflow.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "daily-index-workflow.svg"
GENERATOR = ROOT / "scripts" / "generate-daily-index-workflow-diagram.py"
PAGE_ID = "petakerja_daily_index_workflow"


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&amp;", "&").lower()


def main() -> int:
    errors: list[str] = []
    if not SOURCE.exists():
        print(f"Daily Index workflow checks failed:\n- missing source {SOURCE}")
        return 1

    root = ET.parse(SOURCE).getroot()
    diagram = root.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        errors.append(f"missing page {PAGE_ID}")
        diagram = ET.Element("diagram")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1920", "900"):
        errors.append("canvas is not exactly 1920 x 900")

    wrappers = diagram.findall(".//object")
    keyed = {wrapper.get("petakerjaKey", ""): wrapper for wrapper in wrappers}
    if len(keyed) != len(wrappers) or "" in keyed:
        errors.append("component keys are missing or duplicated")
    required_keys = {
        "daily-index-workflow/stage-github",
        "daily-index-workflow/stage-script",
        "daily-index-workflow/stage-supabase",
        "daily-index-workflow/stage-api",
        "daily-index-workflow/stage-frontend",
        "daily-index-workflow/job-sources",
        "daily-index-workflow/note-security",
        "daily-index-workflow/note-failure",
    }
    missing_keys = required_keys - set(keyed)
    if missing_keys:
        errors.append(f"missing required components: {sorted(missing_keys)}")

    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            errors.append(f"{wrapper.get('id')} is missing bilingual labels")

    expected_metadata = {
        "daily-index-workflow/stage-github": ("github-actions", "", ""),
        "daily-index-workflow/stage-script": ("daily-index-scraper", "", ""),
        "daily-index-workflow/stage-supabase": ("supabase-db", "scraped_jobs", ""),
        "daily-index-workflow/stage-api": ("vercel-runtime,express-app,supa-jobs-route", "", ""),
        "daily-index-workflow/stage-frontend": ("browser,job-manager,jobs-api", "", "jobs-search,jobs-cards,jobs-map"),
    }
    for key, (nodes, table, hotspots) in expected_metadata.items():
        wrapper = keyed.get(key)
        if wrapper is None:
            continue
        if (wrapper.get("nodeIds", ""), wrapper.get("tableName", ""), wrapper.get("uiHotspots", "")) != (nodes, table, hotspots):
            errors.append(f"{key} has incorrect Explorer metadata")

    vertex_ids = {
        wrapper.get("id", "")
        for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    edges = [
        wrapper for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("edge") == "1"
    ]
    if len(edges) != 5:
        errors.append(f"expected 5 workflow connections, found {len(edges)}")
    for edge in edges:
        cell = edge.find("mxCell")
        if cell is None or cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids:
            errors.append(f"{edge.get('id')} has a disconnected endpoint")

    image_cells = [
        cell for cell in diagram.findall(".//mxCell")
        if "shape=image" in cell.get("style", "")
    ]
    if len(image_cells) != 13:
        errors.append(f"expected 13 embedded logos, found {len(image_cells)}")
    for cell in image_cells:
        style = cell.get("style", "")
        if "image=data:image/" not in style:
            errors.append(f"{cell.get('id')} does not contain an embedded logo")
        if re.search(r"image=https?", style, re.I):
            errors.append(f"{cell.get('id')} contains a remote image dependency")

    content_en = " ".join(clean(wrapper.get("labelEn", "")) for wrapper in wrappers)
    content_ms = " ".join(clean(wrapper.get("labelMs", "")) for wrapper in wrappers)
    for phrase in (
        "daily index workflow", "daily 02:00 utc", "scripts/scrape-jobs.ts",
        "public.scraped_jobs", "get /api/jobs/supa", "cache 60 s",
        "searchsupajobs() → executesupasearch()", "service_role_key",
        "zero-result scrape keeps the previous supabase snapshot",
    ):
        if phrase not in content_en:
            errors.append(f"missing workflow truth: {phrase}")
    for phrase in ("aliran kerja indeks harian", "harian 02:00 utc", "cache 60 s", "snapshot supabase terdahulu"):
        if phrase not in content_ms:
            errors.append(f"missing Malay workflow text: {phrase}")
    for source_name in ("maukerja", "hiredly", "ricebowl", "graduan", "jora", "jobstreet", "jobstore", "careerjet"):
        raw_labels = " ".join(cell.get("value", "").lower() for cell in diagram.findall(".//mxCell"))
        if source_name not in raw_labels:
            errors.append(f"missing source label: {source_name}")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    expected_entry = {
        "xml": "assets/editor/daily-index-workflow.drawio",
        "svg": "assets/diagrams/daily-index-workflow.svg",
        "pageId": PAGE_ID,
        "title": "Daily Index Workflow",
        "diagramType": "data-flow",
    }
    if manifest.get("diagrams", {}).get("daily-index-workflow") != expected_entry:
        errors.append("workspace manifest entry is missing or incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    for marker in (
        "id: 'daily-index-scraper'", "id: 'daily-index-job-sources'",
        "id: 'daily-index-workflow'", "category: 'ETL Pipeline'",
        "reportExplanation:", "service-role key remains inside GitHub Actions",
    ):
        if marker not in architecture:
            errors.append(f"architecture model is missing {marker}")
    try:
        if not architecture.index("id: 'etl-pipeline', title:") < architecture.index("id: 'daily-index-workflow', title:") < architecture.index("id: 'deployment-infrastructure', title:"):
            errors.append("Daily Index workflow is not grouped after the operational ETL diagram")
    except ValueError:
        errors.append("could not verify Daily Index navigation order")

    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    package = (ROOT / "package.json").read_text(encoding="utf-8")
    registrations = (
        ("editor-core.js", editor, "'daily-index-workflow': { url: 'assets/editor/daily-index-workflow.drawio"),
        ("translations.js", translations, "'daily-index-workflow': ['Daily Index Workflow'"),
        ("build-diagram-assets.py", builder, '"daily-index-workflow": (DAILY_INDEX_WORKFLOW_SOURCE, 0, "daily-index-workflow.svg")'),
        ("package.json", package, "python scripts/test-daily-index-workflow-diagram.py"),
    )
    for path, text, marker in registrations:
        if marker not in text:
            errors.append(f"{path} is missing Daily Index registration")

    generated = runpy.run_path(str(GENERATOR))
    document = generated["build_document"]()
    generated["validate"](document)
    ET.indent(document, space="  ")
    generated_bytes = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    if generated_bytes.replace(b"\r\n", b"\n") != SOURCE.read_bytes().replace(b"\r\n", b"\n"):
        errors.append("checked-in Draw.io source is not deterministic generator output")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 3000:
        errors.append("generated Daily Index SVG preview is missing")
    else:
        preview = PREVIEW.read_text(encoding="utf-8")
        if len(re.findall(r"<image\b", preview, re.I)) < 13:
            errors.append("generated SVG preview does not retain all embedded logos")
        if re.search(r"(?:href|xlink:href)=['\"]https?", preview, re.I):
            errors.append("generated SVG preview contains a remote image dependency")
    asset_bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    if '"daily-index-workflow"' not in asset_bundle:
        errors.append("generated asset bundle is missing daily-index-workflow")

    if errors:
        print("Daily Index workflow checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Daily Index workflow checks passed for {len(image_cells)} logos and {len(edges)} connected flows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
