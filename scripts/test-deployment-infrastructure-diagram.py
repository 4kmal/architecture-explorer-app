#!/usr/bin/env python3
"""Regression checks for the editable production deployment diagram."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "deployment-infrastructure.drawio"
PREVIEW = ROOT / "assets" / "diagrams" / "deployment-infrastructure.svg"
PAGE_ID = "petakerja_deployment_infrastructure"


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
        print(f"Deployment diagram checks failed:\n- missing source {SOURCE}")
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
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if len(keys) != len(set(keys)) or any(not key.startswith("deployment-infrastructure/") for key in keys):
        errors.append("component keys are missing, duplicated or not namespaced")
    keyed = {wrapper.get("petakerjaKey", ""): wrapper for wrapper in wrappers}
    required_keys = {
        "deployment-infrastructure/region-control",
        "deployment-infrastructure/region-domain",
        "deployment-infrastructure/region-source",
        "deployment-infrastructure/region-build",
        "deployment-infrastructure/region-vercel",
        "deployment-infrastructure/region-data",
        "deployment-infrastructure/region-geo",
        "deployment-infrastructure/region-users",
        "deployment-infrastructure/region-notes",
        "deployment-infrastructure/domain-exabytes",
        "deployment-infrastructure/domain-cloudflare",
        "deployment-infrastructure/build-pipeline",
        "deployment-infrastructure/vercel-edge",
        "deployment-infrastructure/vercel-function",
        "deployment-infrastructure/data-postgres",
        "deployment-infrastructure/data-storage",
        "deployment-infrastructure/geo-caddy",
        "deployment-infrastructure/geo-valhalla",
        "deployment-infrastructure/user-browser",
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

    cards = [wrapper for wrapper in wrappers if wrapper.get("deploymentRole") == "card"]
    for index, card in enumerate(cards):
        for other in cards[index + 1:]:
            if overlaps(bounds(card), bounds(other)):
                errors.append(f"cards overlap: {card.get('id')} and {other.get('id')}")

    vertex_ids = {
        wrapper.get("id", "")
        for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
    }
    wrappers_by_id = {wrapper.get("id", ""): wrapper for wrapper in wrappers}
    edges = [
        wrapper for wrapper in wrappers
        if (cell := wrapper.find("mxCell")) is not None and cell.get("edge") == "1"
    ]
    for edge in edges:
        cell = edge.find("mxCell")
        if cell is None or cell.get("source") not in vertex_ids or cell.get("target") not in vertex_ids:
            errors.append(f"{edge.get('id')} has a disconnected endpoint")
            continue
        source = wrappers_by_id[cell.get("source", "")]
        target = wrappers_by_id[cell.get("target", "")]
        source_nodes = set(source.get("nodeIds", "").split(","))
        target_nodes = set(target.get("nodeIds", "").split(","))
        geo_nodes = {"digitalocean-geo-host", "valhalla", "valhalla-tile-builder"}
        if "browser" in source_nodes and target_nodes & geo_nodes:
            errors.append(f"forbidden browser-to-DigitalOcean flow: {edge.get('id')}")
        if "browser" in target_nodes and source_nodes & geo_nodes:
            errors.append(f"forbidden DigitalOcean-to-browser flow: {edge.get('id')}")

    content = " ".join(clean(wrapper.get("label", "")) for wrapper in wrappers)
    required_phrases = (
        "exabytes", "cloudflare authoritative dns", "dns-only records", "github main branch",
        "npm run build", "vercel edge delivery", "api/server.ts", "server/app.ts",
        "/api/cron/daily", "supabase postgresql + postgis", "supabase storage",
        "publishable/anon key", "explicit grants + rls", "server-only bearer token",
        "geo.petakerja.my", "caddy public gateway", "valhalla private container",
        "nominatim disabled", "geo_router_enabled=false", "usd 24/month",
        "cost footer is not a complete tco estimate",
        "service-role, database_url and provider tokens never enter the browser",
    )
    for phrase in required_phrases:
        if phrase not in content:
            errors.append(f"missing production truth: {phrase}")
    forbidden = (
        "aws lambda", "s3 raw", "terraform", "step functions", "bronze layer",
        "silver layer", "gold layer", "dbt", "staging.petakerja.my", "staging project",
    )
    for phrase in forbidden:
        if phrase in content:
            errors.append(f"contains excluded infrastructure claim: {phrase}")

    represented = {
        node_id
        for wrapper in wrappers
        for node_id in wrapper.get("nodeIds", "").split(",")
        if node_id
    }
    required_nodes = {
        "github-repository", "github-actions", "vercel-build-pipeline", "vercel-edge-delivery",
        "vercel-node-function", "vercel-runtime", "vercel-daily-cron", "cloudflare-dns",
        "exabytes-registrar", "supabase-db", "supabase-storage", "better-auth", "geo-gateway",
        "digitalocean-geo-host", "valhalla-tile-builder", "valhalla", "nominatim", "browser",
        "google-cloud-services", "email-platforms", "ai-provider", "external-data-platforms",
    }
    if required_nodes - represented:
        errors.append(f"missing node mappings: {sorted(required_nodes - represented)}")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    entry = manifest.get("diagrams", {}).get("deployment-infrastructure")
    if entry != {
        "xml": "assets/editor/deployment-infrastructure.drawio",
        "svg": "assets/diagrams/deployment-infrastructure.svg",
        "pageId": PAGE_ID,
        "title": "PetaKerja Production Deployment & Infrastructure",
        "diagramType": "architecture",
    }:
        errors.append("workspace manifest entry is missing or incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    for marker in (
        "id: 'deployment-infrastructure'", "category: 'Deployment & Infra'",
        "id: 'github-repository'", "id: 'vercel-build-pipeline'", "id: 'vercel-edge-delivery'",
        "id: 'vercel-node-function'", "id: 'cloudflare-dns'", "id: 'exabytes-registrar'",
        "id: 'supabase-storage'", "id: 'google-cloud-services'", "id: 'email-platforms'",
        "id: 'external-data-platforms'",
    ):
        if marker not in architecture:
            errors.append(f"architecture model is missing {marker}")
    try:
        etl = architecture.index("id: 'etl-pipeline', title:")
        deployment = architecture.index("id: 'deployment-infrastructure', title:")
        extended = architecture.index("id: 'jobops', title:")
        if not etl < deployment < extended:
            errors.append("Deployment & Infra is not ordered after ETL Pipeline and before Extended modules")
    except ValueError:
        errors.append("could not verify Deployment & Infra navigation order")

    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    for path, text, marker in (
        ("editor-core.js", editor, "'deployment-infrastructure': { url: 'assets/editor/deployment-infrastructure.drawio"),
        ("translations.js", translations, "'deployment-infrastructure': ['PetaKerja Production Deployment & Infrastructure'"),
        ("build-diagram-assets.py", builder, '"deployment-infrastructure": (DEPLOYMENT_INFRASTRUCTURE_SOURCE, 1, "deployment-infrastructure.svg")'),
    ):
        if marker not in text:
            errors.append(f"{path} is missing Deployment & Infra registration")

    if not PREVIEW.exists() or PREVIEW.stat().st_size < 1000:
        errors.append("generated Deployment & Infra SVG preview is missing")
    asset_bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")
    if '"deployment-infrastructure"' not in asset_bundle:
        errors.append("generated asset bundle is missing deployment-infrastructure")

    if errors:
        print("Deployment diagram checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Deployment diagram checks passed for {len(cards)} cards and {len(edges)} connected flows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
