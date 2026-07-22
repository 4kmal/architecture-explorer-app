#!/usr/bin/env python3
"""Focused deterministic checks for the Map & Routing workflow explainers."""

from __future__ import annotations

import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "assets" / "editor" / "map-routing"
PREVIEWS = ROOT / "assets" / "diagrams" / "map-routing"
GENERATOR = ROOT / "scripts" / "generate-map-routing-workflows.py"

SPECS = {
    "nominatim-valhalla-workflow": {
        "page": "petakerja_nominatim_valhalla_workflow",
        "flows": 5,
        "logos": 8,
        "required_keys": {"stage-input", "stage-nominatim", "stage-coordinates", "stage-valhalla", "stage-result", "note-separation", "note-fallback"},
        "logo_keys": {"petakerja", "nominatim", "typescript", "valhalla", "maplibre", "vercel", "express", "supabase"},
    },
    "nominatim-maplibre-workflow": {
        "page": "petakerja_nominatim_maplibre_workflow",
        "flows": 6,
        "logos": 6,
        "required_keys": {"stage-map-input", "stage-search", "stage-nominatim", "stage-merge", "stage-render", "source-pois", "note-boundary"},
        "logo_keys": {"maplibre-input", "typescript", "nominatim", "petakerja", "maplibre-result", "supabase"},
    },
    "valhalla-maplibre-workflow": {
        "page": "petakerja_valhalla_maplibre_workflow",
        "flows": 7,
        "logos": 6,
        "required_keys": {"stage-input", "stage-api", "stage-provider", "stage-normalize", "stage-render", "route-cache", "note-fallback"},
        "logo_keys": {"maplibre-input", "vercel", "valhalla", "typescript", "maplibre-result", "supabase"},
    },
    "geo-server-communication-workflow": {
        "page": "petakerja_geo_server_communication_workflow",
        "flows": 8,
        "logos": 10,
        "required_keys": {"stage-browser", "stage-vercel", "stage-cache", "stage-origin", "stage-docker", "maintenance", "note-security", "note-status"},
        "logo_keys": {"petakerja", "vercel", "supabase", "cloudflare", "digitalocean", "caddy", "docker", "valhalla", "nominatim", "openstreetmap"},
    },
}


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&amp;", "&").lower()


def serialized(document: ET.Element) -> bytes:
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="utf-8", xml_declaration=True).replace(b"\r\n", b"\n")


def main() -> int:
    errors: list[str] = []
    generated = runpy.run_path(str(GENERATOR))
    documents = generated["build_documents"]()

    for diagram_id, spec in SPECS.items():
        source = EDITOR / f"{diagram_id}.drawio"
        preview_path = PREVIEWS / f"{diagram_id}.svg"
        if not source.exists():
            errors.append(f"{diagram_id}: missing canonical Draw.io source")
            continue

        root = ET.parse(source).getroot()
        diagram = root.find("diagram")
        if diagram is None or diagram.get("id") != spec["page"]:
            errors.append(f"{diagram_id}: missing page {spec['page']}")
            continue
        model = diagram.find("mxGraphModel")
        if model is None or (model.get("pageWidth"), model.get("pageHeight")) != ("1920", "900"):
            errors.append(f"{diagram_id}: canvas is not exactly 1920 x 900")

        wrappers = diagram.findall(".//object")
        keyed = {wrapper.get("petakerjaKey", ""): wrapper for wrapper in wrappers}
        if "" in keyed or len(keyed) != len(wrappers):
            errors.append(f"{diagram_id}: component keys are missing or duplicated")
        required = {f"{diagram_id}/{key}" for key in spec["required_keys"]}
        if missing := required - set(keyed):
            errors.append(f"{diagram_id}: missing stable keys {sorted(missing)}")

        stages = [wrapper for wrapper in wrappers if wrapper.get("workflowRole") == "stage"]
        if len(stages) != 5:
            errors.append(f"{diagram_id}: expected five stages, found {len(stages)}")
        for wrapper in wrappers:
            if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
                errors.append(f"{diagram_id}: {wrapper.get('id')} is missing bilingual labels")

        vertices = {
            wrapper.get("id", "") for wrapper in wrappers
            if (cell := wrapper.find("mxCell")) is not None and cell.get("vertex") == "1"
        }
        flows = [
            wrapper for wrapper in wrappers
            if (cell := wrapper.find("mxCell")) is not None and cell.get("edge") == "1"
        ]
        if len(flows) != spec["flows"]:
            errors.append(f"{diagram_id}: expected {spec['flows']} flows, found {len(flows)}")
        for flow in flows:
            cell = flow.find("mxCell")
            if cell is None or cell.get("source") not in vertices or cell.get("target") not in vertices:
                errors.append(f"{diagram_id}: {flow.get('id')} has a disconnected endpoint")

        image_cells = [cell for cell in diagram.findall(".//mxCell") if "shape=image" in cell.get("style", "")]
        if len(image_cells) != spec["logos"]:
            errors.append(f"{diagram_id}: expected {spec['logos']} embedded logos, found {len(image_cells)}")
        raw_ids = {cell.get("id", "") for cell in diagram.findall(".//mxCell")}
        for logo_key in spec["logo_keys"]:
            if not any(cell_id.endswith(f"-logo-{logo_key}") for cell_id in raw_ids):
                errors.append(f"{diagram_id}: missing logo {logo_key}")
        for cell in image_cells:
            style = cell.get("style", "")
            if "image=data:image/" not in style or re.search(r"image=https?", style, re.I):
                errors.append(f"{diagram_id}: {cell.get('id')} is not a local embedded image")

        raw = source.read_text(encoding="utf-8")
        if "gradientColor=" in raw:
            errors.append(f"{diagram_id}: gradients are not allowed")
        if re.search(r"(?:image=|href=|xlink:href=)https?", raw, re.I):
            errors.append(f"{diagram_id}: source contains a remote image dependency")
        if "simpleLabelEn=" in raw or "codeLabelEn=" in raw:
            errors.append(f"{diagram_id}: fixed explainer unexpectedly enables label-mode metadata")

        content_en = " ".join(clean(wrapper.get("labelEn", "")) for wrapper in wrappers)
        content_ms = " ".join(clean(wrapper.get("labelMs", "")) for wrapper in wrappers)
        if not content_en or not content_ms or content_en == content_ms:
            errors.append(f"{diagram_id}: bilingual content is incomplete")

        expected_document = documents[diagram_id]
        if serialized(expected_document) != source.read_bytes().replace(b"\r\n", b"\n"):
            errors.append(f"{diagram_id}: checked-in source is not deterministic generator output")

        if not preview_path.exists() or preview_path.stat().st_size < 3000:
            errors.append(f"{diagram_id}: generated SVG preview is missing")
        else:
            preview = preview_path.read_text(encoding="utf-8")
            if len(re.findall(r"<image\b", preview, re.I)) < spec["logos"]:
                errors.append(f"{diagram_id}: SVG does not retain the embedded logo roster")
            if re.search(r"(?:href|xlink:href)=['\"]https?", preview, re.I):
                errors.append(f"{diagram_id}: SVG contains a remote dependency")

    nv = ET.parse(EDITOR / "nominatim-valhalla-workflow.drawio").getroot()
    nm = ET.parse(EDITOR / "nominatim-maplibre-workflow.drawio").getroot()
    vm = ET.parse(EDITOR / "valhalla-maplibre-workflow.drawio").getroot()
    gs = ET.parse(EDITOR / "geo-server-communication-workflow.drawio").getroot()

    for root, stage_id, flow_ids in (
        (nv, "nv-stage-nominatim", {"nv-flow-search", "nv-flow-place"}),
        (nm, "nm-stage-nominatim", {"nm-flow-geocode", "nm-flow-place"}),
    ):
        stage = root.find(f".//object[@id='{stage_id}']")
        stage_cell = stage.find("mxCell") if stage is not None else None
        if stage is None or stage.get("workflowStatus") != "gated" or stage_cell is None or "dashed=1" not in stage_cell.get("style", ""):
            errors.append(f"{stage_id}: Nominatim stage is not visibly gated")
        for flow_id in flow_ids:
            flow = root.find(f".//object[@id='{flow_id}']")
            flow_cell = flow.find("mxCell") if flow is not None else None
            if flow is None or flow.get("workflowStatus") != "gated" or flow_cell is None or "dashed=1" not in flow_cell.get("style", ""):
                errors.append(f"{flow_id}: Nominatim flow is not visibly gated")

    vm_text = " ".join(clean(obj.get("labelEn", "")) for obj in vm.findall(".//object"))
    for phrase in ("maplibre is the visualizer, not the routing engine", "no eta, no maneuvers and no navigable-route claim", "caddy → private docker port 8002"):
        if phrase not in vm_text:
            errors.append(f"valhalla-maplibre-workflow: missing truth {phrase}")
    gs_text = " ".join(clean(obj.get("labelEn", "")) for obj in gs.findall(".//object"))
    for phrase in ("calls only same-origin /api/geo/*", "cloudflare dns-only", "ports 8002/8080 stay inside docker", "solid path", "dashed path", "geofabrik"):
        if phrase not in gs_text:
            errors.append(f"geo-server-communication-workflow: missing infrastructure truth {phrase}")
    future = gs.find(".//object[@id='gs-flow-future-nominatim']")
    future_cell = future.find("mxCell") if future is not None else None
    if future is None or future.get("workflowStatus") != "gated" or future_cell is None or "dashed=1" not in future_cell.get("style", ""):
        errors.append("geo server future Nominatim route is not dashed and gated")

    manifest = json.loads((ROOT / "workspace-manifest.json").read_text(encoding="utf-8"))
    for diagram_id, spec in SPECS.items():
        entry = manifest.get("diagrams", {}).get(diagram_id, {})
        expected_type = "architecture" if diagram_id == "geo-server-communication-workflow" else "data-flow"
        if entry.get("xml") != f"assets/editor/map-routing/{diagram_id}.drawio" or entry.get("svg") != f"assets/diagrams/map-routing/{diagram_id}.svg" or entry.get("pageId") != spec["page"] or entry.get("diagramType") != expected_type:
            errors.append(f"{diagram_id}: workspace manifest registration is incorrect")

    architecture = (ROOT / "architecture-data.js").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    editor = (ROOT / "editor-core.js").read_text(encoding="utf-8")
    translations = (ROOT / "translations.js").read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build-diagram-assets.py").read_text(encoding="utf-8")
    package = (ROOT / "package.json").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    bundle = (ROOT / "diagram-assets.js").read_text(encoding="utf-8")

    for node_id in ("caddy-geo-edge", "geo-docker-network", "geofabrik-extract"):
        if f"id: '{node_id}'" not in architecture:
            errors.append(f"architecture model is missing {node_id}")
    if "edge('browser', 'nominatim'" in architecture or "edge('browser', 'valhalla'" in architecture:
        errors.append("architecture graph contains a forbidden direct browser-provider edge")
    for marker in ("collectionId: 'map-routing', collectionGroupId: 'overview'", "collectionGroupId: 'provider-workflows'", "collectionGroupId: 'infrastructure'", "reportExplanation:"):
        if marker not in architecture:
            errors.append(f"architecture model is missing {marker}")
    try:
        order = [architecture.index(f"id: '{diagram_id}', title:") for diagram_id in ["map-routing-responsibility-stack", *SPECS]]
        if order != sorted(order):
            errors.append("Map & Routing collection ordering is incorrect")
    except ValueError:
        errors.append("Map & Routing collection diagrams are not all registered")

    registrations = (
        ("app.js", app, "'map-routing': Object.freeze(["),
        ("app.js", app, "ui.collectionProviderWorkflows"),
        ("app.js", app, "ui.collectionRoutingInfrastructure"),
        ("translations.js", translations, "collectionProviderWorkflows: 'Provider Workflows'"),
        ("editor-core.js", editor, "assets/editor/map-routing/nominatim-valhalla-workflow.drawio"),
        ("build-diagram-assets.py", builder, '"geo-server-communication-workflow": (GEO_SERVER_COMMUNICATION_WORKFLOW_SOURCE, 0, "map-routing/geo-server-communication-workflow.svg")'),
        ("package.json", package, "python scripts/test-map-routing-workflows.py"),
        ("README.md", readme, "### Map & Routing explainers"),
    )
    for filename, text, marker in registrations:
        if marker not in text:
            errors.append(f"{filename} is missing registration {marker}")
    for diagram_id in SPECS:
        if f"'{diagram_id}'" not in editor or f"'{diagram_id}': [" not in translations or f'"{diagram_id}"' not in bundle:
            errors.append(f"{diagram_id}: View/Edit/Agent asset registration is incomplete")
        entry_start = architecture.find(f"id: '{diagram_id}', title:")
        entry_end = architecture.find("\n    },", entry_start)
        entry = architecture[entry_start:entry_end]
        if "supportsLabelModes" in entry:
            errors.append(f"{diagram_id}: fixed explainer incorrectly enables Simple/Code")

    if errors:
        print("Map & Routing workflow checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    total_logos = sum(int(spec["logos"]) for spec in SPECS.values())
    total_flows = sum(int(spec["flows"]) for spec in SPECS.values())
    print(f"Map & Routing workflow checks passed for 4 diagrams, {total_logos} embedded logos and {total_flows} connected flows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
