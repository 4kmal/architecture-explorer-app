#!/usr/bin/env python3
"""Regression checks for the editable PetaKerja operational ETL diagram."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "etl-pipeline.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "etl-pipeline.svg"
PAGE_ID = "petakerja_etl_pipeline"


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&amp;", "&").lower()


def bounds(wrapper: ET.Element) -> tuple[float, float, float, float]:
    geometry = wrapper.find("mxCell/mxGeometry")
    if geometry is None:
        raise ValueError(f"{wrapper.get('id')} has no geometry")
    return tuple(float(geometry.get(name, "0")) for name in ("x", "y", "width", "height"))


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def main() -> int:
    errors: list[str] = []
    if not SOURCE.exists():
        print(f"ETL diagram checks failed:\n- missing source {SOURCE}")
        return 1

    root = ET.parse(SOURCE).getroot()
    diagram = root.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        errors.append(f"missing page {PAGE_ID}")
        diagram = ET.Element("diagram")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("2048", "1120"):
        errors.append("canvas is not exactly 2048 x 1120")

    wrappers = diagram.findall(".//object")
    keyed = {wrapper.get("petakerjaKey", ""): wrapper for wrapper in wrappers}
    if len(keyed) != len(wrappers):
        errors.append("component keys are missing or duplicated")
    required_keys = {
        "etl-pipeline/region-control", "etl-pipeline/region-sources", "etl-pipeline/region-etl",
        "etl-pipeline/region-serving", "etl-pipeline/region-notes", "etl-pipeline/control-github",
        "etl-pipeline/control-vercel", "etl-pipeline/control-admin", "etl-pipeline/control-do",
        "etl-pipeline/serve-supabase", "etl-pipeline/serve-do", "etl-pipeline/serve-vercel",
        "etl-pipeline/serve-browser", "etl-pipeline/serve-nominatim",
    }
    missing_keys = required_keys - set(keyed)
    if missing_keys:
        errors.append(f"missing required components: {sorted(missing_keys)}")

    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            errors.append(f"{wrapper.get('id')} is missing bilingual labels")
        cell = wrapper.find("mxCell")
        if cell is not None and cell.get("vertex") == "1" and "light-dark(" not in cell.get("style", ""):
            errors.append(f"{wrapper.get('id')} is not theme-aware")

    cards = [wrapper for wrapper in wrappers if wrapper.get("etlRole") == "card"]
    for index, card in enumerate(cards):
        for other in cards[index + 1:]:
            if overlaps(bounds(card), bounds(other)):
                errors.append(f"cards overlap: {card.get('id')} and {other.get('id')}")

    vertex_ids = {
        wrapper.get("id", "")
        for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    edges = [
        wrapper for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("edge") == "1"
    ]
    for edge in edges:
        cell = edge.find("mxCell")
        if cell is None or cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids:
            errors.append(f"{edge.get('id')} has a disconnected endpoint")

    content = " ".join(clean(wrapper.get("label", "")) for wrapper in wrappers)
    required_phrases = (
        "github actions", "events every 6 h", "jobs 02:00 utc", "extractors 03:00 utc",
        "coffee weekly", "/api/cron/daily", "supabase postgresql + postgis",
        "digitalocean valhalla", "geofabrik osm extract", "service role: server / ci only",
        "failed or zero-result scrapes preserve existing serving data",
        "eta traffic-independent", "nominatim disabled",
    )
    for phrase in required_phrases:
        if phrase not in content:
            errors.append(f"missing operational truth: {phrase}")
    forbidden = ("aws lambda", "terraform", "step functions", "bronze layer", "silver layer", "gold layer", "dbt")
    for phrase in forbidden:
        if phrase in content:
            errors.append(f"contains unimplemented platform claim: {phrase}")

    represented = {
        node_id
        for wrapper in wrappers
        for node_id in wrapper.get("nodeIds", "").split(",")
        if node_id
    }
    required_nodes = {
        "github-actions", "vercel-runtime", "vercel-daily-cron", "digitalocean-geo-host",
        "valhalla-tile-builder", "supabase-db", "geo-gateway", "valhalla", "nominatim", "browser",
    }
    if required_nodes - represented:
        errors.append(f"missing node mappings: {sorted(required_nodes - represented)}")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    entry = manifest.get("diagrams", {}).get("etl-pipeline")
    if entry != {
        "xml": "assets/editor/etl-pipeline.drawio",
        "svg": "assets/diagrams/etl-pipeline.svg",
        "pageId": PAGE_ID,
        "title": "PetaKerja Operational ETL & Serving Pipeline",
        "diagramType": "data-flow",
    }:
        errors.append("workspace manifest entry is missing or incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    for marker in (
        "id: 'etl-pipeline'", "category: 'ETL Pipeline'", "id: 'github-actions'",
        "id: 'vercel-runtime'", "id: 'vercel-daily-cron'", "id: 'digitalocean-geo-host'",
        "id: 'valhalla-tile-builder'",
    ):
        if marker not in architecture:
            errors.append(f"architecture model is missing {marker}")
    try:
        if not architecture.index("id: 'data-flow', title:") < architecture.index("id: 'etl-pipeline', title:") < architecture.index("id: 'jobops', title:"):
            errors.append("ETL category is not ordered after Data and before Extended modules")
    except ValueError:
        errors.append("could not verify ETL navigation order")

    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    for path, text, marker in (
        ("editor-core.js", editor, "'etl-pipeline': { url: 'assets/editor/etl-pipeline.drawio"),
        ("translations.js", translations, "'etl-pipeline': ['PetaKerja Operational ETL & Serving Pipeline'"),
        ("build-diagram-assets.py", builder, '"etl-pipeline": (ETL_PIPELINE_SOURCE, 1, "etl-pipeline.svg")'),
    ):
        if marker not in text:
            errors.append(f"{path} is missing ETL registration")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 1000:
        errors.append("generated ETL SVG preview is missing")
    asset_bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    if '"etl-pipeline"' not in asset_bundle:
        errors.append("generated asset bundle is missing etl-pipeline")

    if errors:
        print("ETL diagram checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"ETL diagram checks passed for {len(cards)} cards and {len(edges)} connected flows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
