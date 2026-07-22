#!/usr/bin/env python3
"""Focused regression checks for the editable Live Search workflow diagram."""

from __future__ import annotations

import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "live-search-workflow.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "live-search-workflow.svg"
GENERATOR = ROOT / "scripts" / "generate-live-search-workflow-diagram.py"
PAGE_ID = "petakerja_live_search_workflow"


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&amp;", "&").lower()


def main() -> int:
    errors: list[str] = []
    if not SOURCE.exists():
        print(f"Live Search workflow checks failed:\n- missing source {SOURCE}")
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
        "live-search-workflow/stage-request",
        "live-search-workflow/stage-auth",
        "live-search-workflow/stage-server",
        "live-search-workflow/stage-fanout",
        "live-search-workflow/stage-result",
        "live-search-workflow/job-sources",
        "live-search-workflow/comparison",
        "live-search-workflow/comparison-live",
        "live-search-workflow/comparison-daily",
        "live-search-workflow/note-failure",
        "live-search-workflow/flow-bypass",
    }
    missing_keys = required_keys - set(keyed)
    if missing_keys:
        errors.append(f"missing required components: {sorted(missing_keys)}")

    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            errors.append(f"{wrapper.get('id')} is missing bilingual labels")

    expected_metadata = {
        "live-search-workflow/stage-request": ("job-manager,browser,jobs-api", "jobs-search"),
        "live-search-workflow/stage-auth": ("better-auth,jobs-api,auth-client", "auth-modal,jobs-search"),
        "live-search-workflow/stage-server": ("live-search-route,express-app,vercel-runtime", ""),
        "live-search-workflow/stage-fanout": ("live-search-job-sources", ""),
        "live-search-workflow/stage-result": ("job-search-relevance,job-entity,job-manager,map-manager,browser", "jobs-cards,jobs-map"),
    }
    for key, (nodes, hotspots) in expected_metadata.items():
        wrapper = keyed.get(key)
        if wrapper is not None and (wrapper.get("nodeIds", ""), wrapper.get("uiHotspots", "")) != (nodes, hotspots):
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
    if len(edges) != 6:
        errors.append(f"expected 6 workflow connections, found {len(edges)}")
    for edge in edges:
        cell = edge.find("mxCell")
        if cell is None or cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids:
            errors.append(f"{edge.get('id')} has a disconnected endpoint")
    bypass = keyed.get("live-search-workflow/flow-bypass")
    bypass_cell = bypass.find("mxCell") if bypass is not None else None
    if bypass_cell is None or "dashed=1" not in bypass_cell.get("style", ""):
        errors.append("cache-hit / single-flight bypass is not dashed")

    image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
    if len(image_cells) != 14:
        errors.append(f"expected 14 embedded logos, found {len(image_cells)}")
    for cell in image_cells:
        style = cell.get("style", "")
        if "image=data:image/" not in style:
            errors.append(f"{cell.get('id')} does not contain an embedded logo")
        if re.search(r"image=https?", style, re.I):
            errors.append(f"{cell.get('id')} contains a remote image dependency")

    content_en = " ".join(clean(wrapper.get("labelEn", "")) for wrapper in wrappers)
    content_ms = " ".join(clean(wrapper.get("labelMs", "")) for wrapper in wrappers)
    for phrase in (
        "live search workflow", "jobfindermanager.executelivesearch()", "authenticatedfetch()",
        "get /api/search-jobs", "5 min cache", "256 max", "single-flight", "7 s timeout per source",
        "partial source failures preserve usable results", "fatal error responses are not cached",
        "sign-in required", "reads public.scraped_jobs", "02:00 utc or manual run",
    ):
        if phrase not in content_en:
            errors.append(f"missing workflow truth: {phrase}")
    for phrase in (
        "aliran kerja carian langsung", "cache 5 min", "had masa 7 s setiap sumber",
        "log masuk diperlukan", "baca public.scraped_jobs", "respons ralat fatal tidak dicache",
    ):
        if phrase not in content_ms:
            errors.append(f"missing Malay workflow text: {phrase}")
    raw_labels = " ".join(cell.get("value", "").lower() for cell in diagram.findall(".//mxCell"))
    for source_name in ("maukerja", "hiredly", "ricebowl", "graduan", "jora", "jobstreet", "jobstore", "careerjet"):
        if source_name not in raw_labels:
            errors.append(f"missing source label: {source_name}")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    expected_entry = {
        "xml": "assets/editor/live-search-workflow.drawio",
        "svg": "assets/diagrams/live-search-workflow.svg",
        "pageId": PAGE_ID,
        "title": "Live Search Workflow",
        "diagramType": "data-flow",
    }
    if manifest.get("diagrams", {}).get("live-search-workflow") != expected_entry:
        errors.append("workspace manifest entry is missing or incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    for marker in (
        "id: 'live-search-route'", "id: 'live-search-job-sources'", "id: 'live-search-workflow'",
        "collectionId: 'etl-pipeline', collectionGroupId: 'overview'",
        "collectionId: 'etl-pipeline', collectionGroupId: 'job-search-workflows'",
        "reportExplanation:", "does not read or write a job table",
    ):
        if marker not in architecture:
            errors.append(f"architecture model is missing {marker}")
    try:
        if not architecture.index("id: 'etl-pipeline', title:") < architecture.index("id: 'daily-index-workflow', title:") < architecture.index("id: 'live-search-workflow', title:") < architecture.index("id: 'deployment-infrastructure', title:"):
            errors.append("Live Search workflow is not grouped after Daily Index")
    except ValueError:
        errors.append("could not verify ETL navigation order")

    app = (ROOT / "app.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    package = (ROOT / "package.json").read_text(encoding="utf-8")
    registrations = (
        ("app.js", app, "'etl-pipeline': Object.freeze(["),
        ("app.js", app, "collectionFolder(collectionId, category, categoryDiagrams)"),
        ("app.js", app, "ui.collectionETLOverview"),
        ("app.js", app, "ui.collectionJobSearchWorkflows"),
        ("editor-core.js", editor, "'live-search-workflow': { url: 'assets/editor/live-search-workflow.drawio"),
        ("translations.js", translations, "'live-search-workflow': ['Live Search Workflow'"),
        ("build-diagram-assets.py", builder, '"live-search-workflow": (LIVE_SEARCH_WORKFLOW_SOURCE, 0, "live-search-workflow.svg")'),
        ("package.json", package, "python scripts/test-live-search-workflow-diagram.py"),
    )
    for path, text, marker in registrations:
        if marker not in text:
            errors.append(f"{path} is missing Live Search registration: {marker}")

    generated = runpy.run_path(str(GENERATOR))
    document = generated["build_document"]()
    generated["validate"](document)
    ET.indent(document, space="  ")
    generated_bytes = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    if generated_bytes.replace(b"\r\n", b"\n") != SOURCE.read_bytes().replace(b"\r\n", b"\n"):
        errors.append("checked-in Draw.io source is not deterministic generator output")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 3000:
        errors.append("generated Live Search SVG preview is missing")
    else:
        preview = PREVIEW.read_text(encoding="utf-8")
        if len(re.findall(r"<image\b", preview, re.I)) < 14:
            errors.append("generated SVG preview does not retain all embedded logos")
        if re.search(r"(?:href|xlink:href)=['\"]https?", preview, re.I):
            errors.append("generated SVG preview contains a remote image dependency")
    asset_bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    if '"live-search-workflow"' not in asset_bundle:
        errors.append("generated asset bundle is missing live-search-workflow")

    if errors:
        print("Live Search workflow checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Live Search workflow checks passed for {len(image_cells)} logos and {len(edges)} connected flows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
