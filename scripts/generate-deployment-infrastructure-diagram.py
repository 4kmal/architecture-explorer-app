#!/usr/bin/env python3
"""Generate the editable bilingual PetaKerja deployment diagram.

The source documents the checked-in production topology: Exabytes and
Cloudflare provide domain authority, GitHub and Vercel build and deliver the
application, Supabase provides operational data services, and DigitalOcean
hosts the isolated Valhalla routing origin. It deliberately does not model the
AWS/Terraform/medallion stack shown only in the layout reference.
"""

from __future__ import annotations

from dataclasses import dataclass
import html
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "editor" / "deployment-infrastructure.drawio"
PAGE_ID = "petakerja_deployment_infrastructure"
PAGE_WIDTH = 2048
PAGE_HEIGHT = 1120


TITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=25;fontStyle=1;fontColor=light-dark(#172033,#e8edf7);"
SUBTITLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontStyle=2;fontColor=light-dark(#667085,#aeb8c8);"
CONTROL_REGION = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#f3f0ff,#1f1b32);strokeColor=light-dark(#9b82e8,#8168d6);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=16;fontStyle=1;align=left;verticalAlign=top;spacingTop=14;spacingLeft=16;"
DOMAIN_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#eef6ff,#142235);strokeColor=light-dark(#83b8ec,#4f8bc6);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
SOURCE_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#f3f0ff,#211a35);strokeColor=light-dark(#a38ae9,#8068d2);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
BUILD_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#fff8e8,#2d2516);strokeColor=light-dark(#e3b45d,#bd8730);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
VERCEL_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#f4f6f8,#1a1f27);strokeColor=light-dark(#8d99a8,#6f7b8c);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
DATA_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#eefaf3,#14281d);strokeColor=light-dark(#75c997,#4a9d6c);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
GEO_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#eef9fb,#13282d);strokeColor=light-dark(#63becb,#4496a4);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
USER_REGION = "rounded=1;arcSize=16;whiteSpace=wrap;html=1;fillColor=light-dark(#f2f7ff,#172235);strokeColor=light-dark(#8aa9dc,#5f82bd);strokeWidth=1.25;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=center;verticalAlign=top;spacingTop=14;"
NOTES_REGION = "rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor=light-dark(#f7f9fc,#171c24);strokeColor=light-dark(#c7d0dc,#596579);strokeWidth=1;fontColor=light-dark(#172033,#e8edf7);fontFamily=Arial;fontSize=15;fontStyle=1;align=left;verticalAlign=middle;spacingLeft=16;"

CARD_CONTROL = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#28213f);strokeColor=light-dark(#7759d8,#9a82ef);strokeWidth=1.25;fontColor=light-dark(#172033,#eef1ff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;shadow=1;"
CARD_DOMAIN = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1b2d43);strokeColor=light-dark(#4f91d4,#70afea);strokeWidth=1.1;fontColor=light-dark(#17375e,#e7f2ff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_SOURCE = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#2a2140);strokeColor=light-dark(#8064cf,#a48cec);strokeWidth=1.1;fontColor=light-dark(#38236d,#f0eaff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_BUILD = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#fffdf8,#342918);strokeColor=light-dark(#cf8b30,#d9a04c);strokeWidth=1.1;fontColor=light-dark(#57380e,#fff0d3);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_RUNTIME = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#242a33);strokeColor=light-dark(#667085,#8a95a6);strokeWidth=1.15;fontColor=light-dark(#273142,#eef1f5);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;shadow=1;"
CARD_DATA = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#193126);strokeColor=light-dark(#3da86a,#62ca88);strokeWidth=1.15;fontColor=light-dark(#174a2b,#e5ffed);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_STORE = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;whiteSpace=wrap;html=1;fillColor=light-dark(#eaf9f0,#183324);strokeColor=light-dark(#3da86a,#62ca88);strokeWidth=1.2;fontColor=light-dark(#174a2b,#e5ffed);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_GEO = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#173138);strokeColor=light-dark(#3498a7,#61c3d2);strokeWidth=1.15;fontColor=light-dark(#14505a,#e3fbff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_USER = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#1d2b43);strokeColor=light-dark(#5d83bd,#7ea4df);strokeWidth=1.15;fontColor=light-dark(#263c61,#eaf2ff);fontFamily=Arial;fontSize=12;align=center;verticalAlign=middle;spacing=8;"
CARD_DISABLED = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=light-dark(#f2f4f7,#242932);strokeColor=light-dark(#98a2b3,#747f90);strokeWidth=1.1;dashed=1;dashPattern=6 4;fontColor=light-dark(#475467,#d0d5dd);fontFamily=Arial;fontSize=11;align=center;verticalAlign=middle;spacing=6;"
NOTE = "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=light-dark(#ffffff,#202630);strokeColor=light-dark(#98a2b3,#697586);strokeWidth=1;fontColor=light-dark(#344054,#e2e7ef);fontFamily=Arial;fontSize=11;align=center;verticalAlign=middle;spacing=7;"

EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=light-dark(#667085,#aeb8c8);strokeWidth=1.35;fontColor=light-dark(#344054,#d7deea);fontFamily=Arial;fontSize=10;labelBackgroundColor=light-dark(#ffffff,#15191f);"
EDGE_CONTROL = EDGE + "dashed=1;dashPattern=7 4;strokeColor=light-dark(#7759d8,#9a82ef);"
EDGE_DEPLOY = EDGE + "strokeColor=light-dark(#bd7621,#e0a24e);"
EDGE_DATA = EDGE + "strokeColor=light-dark(#2f9b5e,#62ca88);"
EDGE_GEO = EDGE + "strokeColor=light-dark(#278899,#61c3d2);"
EDGE_DNS = EDGE + "dashed=1;dashPattern=6 4;strokeColor=light-dark(#397bb5,#70afea);"


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
    routes: str = ""
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
    label_position: float = 0
    label_offset: tuple[int, int] = (0, -8)


def rich(title: str, *lines: str) -> str:
    detail = "<br>".join(html.escape(line) for line in lines)
    return f"<b>{html.escape(title)}</b>" + (f"<br>{detail}" if detail else "")


def attrs(label_en: str, label_ms: str, key: str, node_ids: str = "",
          routes: str = "", hotspots: str = "", **extra: str) -> dict[str, str]:
    result = {
        "label": label_en,
        "labelEn": label_en,
        "labelMs": label_ms,
        "petakerjaKey": f"deployment-infrastructure/{key}",
        **extra,
    }
    if node_ids:
        result.update({"nodeIds": node_ids, "component": "1"})
    if routes:
        result["routes"] = routes
    if hotspots:
        result["uiHotspots"] = hotspots
    return result


def add_vertex(root: ET.Element, spec: Vertex) -> str:
    wrapper = ET.SubElement(root, "object", {
        "id": spec.identifier,
        **attrs(
            spec.label_en, spec.label_ms, spec.key, spec.node_ids,
            spec.routes, spec.hotspots, deploymentRole=spec.role,
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
        **attrs(spec.label_en, spec.label_ms, spec.key, deploymentRole="flow"),
    })
    cell = ET.SubElement(wrapper, "mxCell", {
        "parent": "1", "edge": "1", "source": spec.source,
        "target": spec.target, "style": spec.style,
    })
    geometry = ET.SubElement(cell, "mxGeometry", {
        "x": str(spec.label_position), "y": "0", "relative": "1", "as": "geometry",
    })
    if spec.label_en:
        ET.SubElement(geometry, "mxPoint", {
            "x": str(spec.label_offset[0]), "y": str(spec.label_offset[1]), "as": "offset",
        })
    if spec.points:
        array = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in spec.points:
            ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})
    return spec.identifier


def build_document() -> ET.Element:
    mxfile = ET.Element("mxfile", {
        "host": "PetaKerja Architecture Explorer",
        "agent": "PetaKerja Deployment Infrastructure Generator",
        "version": "27.0.2",
        "compressed": "false",
        "pages": "1",
        "petakerjaProjectionLanguage": "en",
        "petakerjaLayoutStandard": "deployment-infrastructure-v1",
    })
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": PAGE_ID,
        "name": "PetaKerja Production Deployment & Infrastructure",
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
        Vertex("title", "deployment-title", "PetaKerja Production Deployment & Infrastructure", "Deployment & Infrastruktur Produksi PetaKerja", 50, 18, 1948, 38, TITLE, role="title"),
        Vertex("subtitle", "deployment-subtitle", "Production delivery, operational data, secure routing origin and external platform boundaries", "Penyampaian produksi, data operasi, origin penghalaan selamat dan sempadan platform luaran", 50, 58, 1948, 26, SUBTITLE, role="subtitle"),

        Vertex("region-control", "deployment-region-control", "PRODUCTION CONTROL PLANE", "KAWALAN PRODUKSI", 50, 95, 1948, 125, CONTROL_REGION, role="region"),
        Vertex("control-main", "deployment-control-main", rich("GitHub main branch", "release source of truth", "four independent ingestion workflows"), rich("Branch utama GitHub", "sumber benar release", "empat workflow ingest berasingan"), 230, 130, 330, 66, CARD_CONTROL, "github-repository,github-actions"),
        Vertex("control-vercel", "deployment-control-vercel", rich("Vercel Production", "petakerja.my", "build, deploy, TLS and application rollback"), rich("Produksi Vercel", "petakerja.my", "bina, deploy, TLS dan undur aplikasi"), 635, 130, 330, 66, CARD_CONTROL, "vercel-runtime,vercel-build-pipeline,vercel-edge-delivery"),
        Vertex("control-secrets", "deployment-control-secrets", rich("Secret domains", "GitHub Actions secrets", "Vercel server env · Droplet runtime token"), rich("Domain rahsia", "rahsia GitHub Actions", "env pelayan Vercel · token runtime Droplet"), 1040, 130, 330, 66, CARD_CONTROL, "github-actions,vercel-node-function,digitalocean-geo-host"),
        Vertex("control-ops", "deployment-control-ops", rich("Operations & rollback", "Vercel deployment rollback", "GEO_ROUTER_ENABLED=false · tile archive restore"), rich("Operasi & undur", "undur deployment Vercel", "GEO_ROUTER_ENABLED=false · pulih arkib jubin"), 1445, 130, 330, 66, CARD_CONTROL, "vercel-runtime,valhalla-tile-builder"),

        Vertex("region-domain", "deployment-region-domain", "DOMAIN & DNS", "DOMAIN & DNS", 50, 245, 235, 680, DOMAIN_REGION, role="region"),
        Vertex("domain-exabytes", "deployment-domain-exabytes", rich("Exabytes", "petakerja.my registrar", "renewal and nameserver ownership"), rich("Exabytes", "pendaftar petakerja.my", "pembaharuan dan pemilikan nameserver"), 70, 315, 195, 95, CARD_DOMAIN, "exabytes-registrar"),
        Vertex("domain-cloudflare", "deployment-domain-cloudflare", rich("Cloudflare authoritative DNS", "DNS-only records", "no proxy layer in front of Vercel"), rich("DNS autoritatif Cloudflare", "rekod DNS sahaja", "tiada lapisan proksi di hadapan Vercel"), 70, 450, 195, 120, CARD_DOMAIN, "cloudflare-dns"),
        Vertex("domain-routes", "deployment-domain-routes", rich("Production hostnames", "petakerja.my + www → Vercel", "geo.petakerja.my → DigitalOcean"), rich("Nama hos produksi", "petakerja.my + www → Vercel", "geo.petakerja.my → DigitalOcean"), 70, 620, 195, 135, CARD_DOMAIN, "cloudflare-dns,vercel-edge-delivery,digitalocean-geo-host"),

        Vertex("region-source", "deployment-region-source", "SOURCE & AUTOMATION", "SUMBER & AUTOMASI", 300, 245, 245, 680, SOURCE_REGION, role="region"),
        Vertex("source-repo", "deployment-source-repo", rich("GitHub repository", "main production branch", "application + docs + infra definitions"), rich("Repositori GitHub", "branch produksi utama", "definisi aplikasi + docs + infra"), 320, 315, 205, 100, CARD_SOURCE, "github-repository"),
        Vertex("source-actions", "deployment-source-actions", rich("GitHub Actions", "events 6 h · jobs 02:00 UTC", "extractors 03:00 UTC · coffee weekly", "service-role batch writes"), rich("GitHub Actions", "acara 6 jam · kerja 02:00 UTC", "extractor 03:00 UTC · kopi mingguan", "tulisan kelompok service-role"), 320, 455, 205, 125, CARD_SOURCE, "github-actions"),
        Vertex("source-operator", "deployment-source-operator", rich("Maintainer / administrator", "manual release and smoke checks", "monthly routing-data maintenance"), rich("Penyelenggara / pentadbir", "release manual dan semakan asap", "selenggara data penghalaan bulanan"), 320, 625, 205, 115, CARD_SOURCE, "pentadbir,valhalla-tile-builder"),

        Vertex("region-build", "deployment-region-build", "BUILD & RELEASE", "BINA & RELEASE", 560, 245, 270, 680, BUILD_REGION, role="region"),
        Vertex("build-pipeline", "deployment-build-pipeline", rich("Vercel build pipeline", "npm run build", "TypeScript + deterministic asset generation"), rich("Pipeline binaan Vercel", "npm run build", "TypeScript + penjanaan aset deterministik"), 580, 315, 230, 115, CARD_BUILD, "vercel-build-pipeline"),
        Vertex("build-app", "deployment-build-app", rich("Application bundles", "Vite SPA → dist", "api/server.ts → Node Function"), rich("Bundle aplikasi", "SPA Vite → dist", "api/server.ts → Fungsi Node"), 580, 465, 230, 90, CARD_BUILD, "vercel-build-pipeline,vercel-node-function"),
        Vertex("build-docs", "deployment-build-docs", rich("Documentation bundles", "Docusaurus → dist/docs", "Architecture Explorer → protected route"), rich("Bundle dokumentasi", "Docusaurus → dist/docs", "Architecture Explorer → route dilindungi"), 580, 590, 230, 105, CARD_BUILD, "vercel-build-pipeline"),
        Vertex("build-geo-studio", "deployment-build-geo-studio", rich("Geo Studio bundle", "nested npm ci", "Kepler workspace → dist/geo-studio"), rich("Bundle Geo Studio", "npm ci bersarang", "workspace Kepler → dist/geo-studio"), 580, 730, 230, 105, CARD_BUILD, "vercel-build-pipeline"),

        Vertex("region-vercel", "deployment-region-vercel", "VERCEL RUNTIME", "RUNTIME VERCEL", 845, 245, 295, 680, VERCEL_REGION, role="region"),
        Vertex("vercel-edge", "deployment-vercel-edge", rich("Vercel edge delivery", "CDN + managed TLS", "/ · /docs · /geo-studio · static assets"), rich("Penyampaian edge Vercel", "CDN + TLS terurus", "/ · /docs · /geo-studio · aset statik"), 865, 315, 255, 105, CARD_RUNTIME, "vercel-edge-delivery,vercel-runtime"),
        Vertex("vercel-function", "deployment-vercel-function", rich("Vercel Node Function", "api/server.ts", "restores rewritten path and invokes Express"), rich("Fungsi Node Vercel", "api/server.ts", "pulih path rewrite dan panggil Express"), 865, 455, 255, 110, CARD_RUNTIME, "vercel-node-function,vercel-runtime", "/api/*"),
        Vertex("vercel-express", "deployment-vercel-express", rich("Express application boundary", "server/app.ts · Better Auth · protected APIs", "/api/geo/* → GeoGateway"), rich("Sempadan aplikasi Express", "server/app.ts · Better Auth · API dilindungi", "/api/geo/* → GeoGateway"), 865, 600, 255, 125, CARD_RUNTIME, "express-app,better-auth,geo-gateway", "/api/*,/api/auth/*,/api/geo/*"),
        Vertex("vercel-cron", "deployment-vercel-cron", rich("Vercel daily cron", "/api/cron/daily · 01:00 UTC", "four bounded maintenance steps"), rich("Cron harian Vercel", "/api/cron/daily · 01:00 UTC", "empat langkah penyelenggaraan terhad"), 865, 765, 255, 95, CARD_RUNTIME, "vercel-daily-cron", "/api/cron/daily"),

        Vertex("region-data", "deployment-region-data", "DATA & IDENTITY", "DATA & IDENTITI", 1155, 245, 275, 680, DATA_REGION, role="region"),
        Vertex("data-postgres", "deployment-data-postgres", rich("Supabase PostgreSQL + PostGIS", "operational and geo tables", "direct SQL restricted to trusted server workloads"), rich("Supabase PostgreSQL + PostGIS", "jadual operasi dan geo", "SQL terus terhad kepada beban pelayan dipercayai"), 1175, 315, 235, 160, CARD_STORE, "supabase-db"),
        Vertex("data-storage", "deployment-data-storage", rich("Supabase Storage", "blog media · diagrams · presentations", "resume and Geo Studio assets"), rich("Supabase Storage", "media blog · rajah · pembentangan", "resume dan aset Geo Studio"), 1175, 510, 235, 115, CARD_STORE, "supabase-storage"),
        Vertex("data-api", "deployment-data-api", rich("Data API + RPC", "publishable/anon key", "explicit grants + RLS + least privilege"), rich("Data API + RPC", "kunci publishable/anon", "grant nyata + RLS + hak minimum"), 1175, 665, 235, 105, CARD_DATA, "supabase-db,supabase-module"),
        Vertex("data-auth", "deployment-data-auth", rich("Better Auth persistence", "cookie-backed sessions", "identity tables + public.users bridge"), rich("Persistensi Better Auth", "sesi berasaskan cookie", "jadual identiti + jambatan public.users"), 1175, 805, 235, 85, CARD_DATA, "better-auth,supabase-db"),

        Vertex("region-geo", "deployment-region-geo", "DIGITALOCEAN GEO", "GEO DIGITALOCEAN", 1445, 245, 300, 680, GEO_REGION, role="region"),
        Vertex("geo-builder", "deployment-geo-builder", rich("Geofabrik → tile builder", "Malaysia + Singapore + Brunei PBF", "monthly preflight, build and route validation"), rich("Geofabrik → pembina jubin", "PBF Malaysia + Singapura + Brunei", "prasemak, bina dan sah laluan bulanan"), 1465, 315, 260, 105, CARD_GEO, "valhalla-tile-builder,external-data-platforms"),
        Vertex("geo-droplet", "deployment-geo-droplet", rich("DigitalOcean Droplet", "Singapore · 2 vCPU · 4 GB RAM · 80 GB SSD", "firewall + USD 20 billing alert"), rich("Droplet DigitalOcean", "Singapura · 2 vCPU · RAM 4 GB · SSD 80 GB", "firewall + amaran bil USD 20"), 1465, 455, 260, 110, CARD_GEO, "digitalocean-geo-host"),
        Vertex("geo-caddy", "deployment-geo-caddy", rich("Caddy public gateway", "ports 80/443 · managed TLS", "/healthz public · bearer token otherwise"), rich("Gerbang awam Caddy", "port 80/443 · TLS terurus", "/healthz awam · token bearer selainnya"), 1465, 605, 260, 90, CARD_GEO, "digitalocean-geo-host"),
        Vertex("geo-valhalla", "deployment-geo-valhalla", rich("Valhalla private container", "port 8002 internal only", "route · matrix · isochrone · traffic-independent ETA"), rich("Kontena Valhalla persendirian", "port 8002 dalaman sahaja", "laluan · matriks · isokron · ETA tanpa trafik"), 1465, 730, 260, 105, CARD_GEO, "valhalla"),
        Vertex("geo-nominatim", "deployment-geo-nominatim", rich("Nominatim", "feature gate disabled"), rich("Nominatim", "pagar ciri dinyahaktifkan"), 1465, 850, 260, 55, CARD_DISABLED, "nominatim"),

        Vertex("region-users", "deployment-region-users", "USERS", "PENGGUNA", 1760, 245, 238, 680, USER_REGION, role="region"),
        Vertex("user-browser", "deployment-user-browser", rich("PetaKerja browser", "public + signed-in workspaces", "MapLibre, jobs, blog, docs and Geo Studio"), rich("Pelayar PetaKerja", "workspace awam + log masuk", "MapLibre, kerja, blog, docs dan Geo Studio"), 1780, 315, 198, 120, CARD_USER, "browser,pengguna", hotspots="map-canvas,jobs-search,blog-posts"),
        Vertex("user-admin", "deployment-user-admin", rich("Administrator", "release and operational checks", "protected application controls"), rich("Pentadbir", "semakan release dan operasi", "kawalan aplikasi dilindungi"), 1780, 475, 198, 100, CARD_USER, "pentadbir"),
        Vertex("user-integrations", "deployment-user-integrations", rich("Grouped external platforms", "Google OAuth + Gmail", "SMTP/Mailgun · AI providers", "public-data + job-source APIs"), rich("Platform luaran berkumpulan", "Google OAuth + Gmail", "SMTP/Mailgun · penyedia AI", "API data awam + sumber kerja"), 1780, 615, 198, 175, CARD_USER, "google-cloud-services,email-platforms,ai-provider,external-data-platforms,data-gov"),
        Vertex("user-monitor", "deployment-user-monitor", rich("Operational monitoring", "public /healthz uptime check", "CPU · RAM · disk alerts"), rich("Pemantauan operasi", "semakan uptime /healthz awam", "amaran CPU · RAM · cakera"), 1780, 825, 198, 80, CARD_USER, "digitalocean-geo-host"),

        Vertex("region-notes", "deployment-region-notes", "VERIFIED OPERATING NOTES", "NOTA OPERASI DISAHKAN", 50, 955, 1948, 120, NOTES_REGION, role="region"),
        Vertex("note-cost", "deployment-note-cost", rich("Verified cost direction", "DigitalOcean routing pilot: USD 24/month", "Vercel, Supabase, email and AI: plan/usage dependent"), rich("Arah kos disahkan", "Rintis penghalaan DigitalOcean: USD 24/bulan", "Vercel, Supabase, e-mel dan AI: ikut pelan/penggunaan"), 245, 980, 365, 68, NOTE, role="note"),
        Vertex("note-security", "deployment-note-security", rich("Secret boundary", "service-role, DATABASE_URL and provider tokens never enter the browser"), rich("Sempadan rahsia", "service-role, DATABASE_URL dan token penyedia tidak masuk ke pelayar"), 660, 980, 365, 68, NOTE, role="note"),
        Vertex("note-rollback", "deployment-note-rollback", rich("Rollback", "Vercel deployment rollback · GEO_ROUTER_ENABLED=false", "previous Valhalla archive restored after failed rebuild"), rich("Undur", "undur deployment Vercel · GEO_ROUTER_ENABLED=false", "arkib Valhalla lama dipulih selepas binaan gagal"), 1075, 980, 365, 68, NOTE, role="note"),
        Vertex("note-status", "deployment-note-status", rich("Production status · 20 Jul 2026", "Valhalla available · Nominatim disabled", "cost footer is not a complete TCO estimate"), rich("Status produksi · 20 Jul 2026", "Valhalla tersedia · Nominatim dinyahaktifkan", "footer kos bukan anggaran TCO lengkap"), 1490, 980, 365, 68, NOTE, role="note"),
    ]

    ids: dict[str, str] = {}
    for vertex in vertices:
        ids[vertex.key] = add_vertex(root, vertex)

    flows = [
        Flow("control/main-repo", "deployment-flow-control-main", ids["control-main"], ids["source-repo"], style=EDGE_CONTROL, points=((395, 225), (422, 225))),
        Flow("control/vercel-build", "deployment-flow-control-vercel", ids["control-vercel"], ids["build-pipeline"], style=EDGE_CONTROL, points=((800, 225), (695, 225))),
        Flow("control/secrets-function", "deployment-flow-control-secrets-function", ids["control-secrets"], ids["vercel-function"], "server environment", "env pelayan", EDGE_CONTROL, ((1205, 230), (1135, 230), (1135, 510))),
        Flow("control/ops-monitor", "deployment-flow-control-ops", ids["control-ops"], ids["user-monitor"], style=EDGE_CONTROL, points=((1610, 230), (1748, 230), (1748, 865))),

        Flow("dns/registrar", "deployment-flow-registrar-dns", ids["domain-exabytes"], ids["domain-cloudflare"], "nameservers", "nameserver", EDGE_DNS),
        Flow("dns/vercel", "deployment-flow-dns-vercel", ids["domain-cloudflare"], ids["vercel-edge"], "petakerja.my DNS-only", "DNS sahaja petakerja.my", EDGE_DNS, ((285, 510), (290, 510), (290, 232), (1135, 232), (1135, 367))),
        Flow("dns/geo", "deployment-flow-dns-geo", ids["domain-cloudflare"], ids["geo-caddy"], "geo.petakerja.my DNS-only", "DNS sahaja geo.petakerja.my", EDGE_DNS, ((285, 530), (295, 530), (295, 238), (1435, 238), (1435, 650), (1465, 650))),

        Flow("source/repo-actions", "deployment-flow-repo-actions", ids["source-repo"], ids["source-actions"], style=EDGE_DEPLOY),
        Flow("source/repo-build", "deployment-flow-repo-build", ids["source-repo"], ids["build-pipeline"], "main commit", "commit utama", EDGE_DEPLOY),
        Flow("source/actions-data", "deployment-flow-actions-data", ids["source-actions"], ids["data-postgres"], "service-role batch upsert", "upsert kelompok service-role", EDGE_DATA + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;", ((540, 518), (550, 518), (550, 940), (1140, 940), (1140, 395), (1175, 395))),
        Flow("source/operator-builder", "deployment-flow-operator-builder", ids["source-operator"], ids["geo-builder"], "monthly maintenance", "selenggara bulanan", EDGE_CONTROL + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;", ((540, 682), (550, 682), (550, 946), (1435, 946), (1435, 368), (1465, 368))),

        Flow("build/pipeline-app", "deployment-flow-build-app", ids["build-pipeline"], ids["build-app"], style=EDGE_DEPLOY),
        Flow("build/pipeline-docs", "deployment-flow-build-docs", ids["build-pipeline"], ids["build-docs"], style=EDGE_DEPLOY, points=((570, 372), (550, 372), (550, 642), (580, 642))),
        Flow("build/pipeline-geo", "deployment-flow-build-geo", ids["build-pipeline"], ids["build-geo-studio"], "nested npm ci", "npm ci bersarang", EDGE_DEPLOY, ((820, 372), (830, 372), (830, 782), (810, 782))),
        Flow("build/app-edge", "deployment-flow-app-edge", ids["build-app"], ids["vercel-edge"], "static output", "output statik", EDGE_DEPLOY, ((820, 510), (835, 510), (835, 367), (865, 367))),
        Flow("build/app-function", "deployment-flow-app-function", ids["build-app"], ids["vercel-function"], "server bundle", "bundle pelayan", EDGE_DEPLOY),
        Flow("build/docs-edge", "deployment-flow-docs-edge", ids["build-docs"], ids["vercel-edge"], style=EDGE_DEPLOY, points=((820, 642), (838, 642), (838, 390), (865, 390))),
        Flow("build/geo-edge", "deployment-flow-geo-edge", ids["build-geo-studio"], ids["vercel-edge"], style=EDGE_DEPLOY, points=((820, 782), (840, 782), (840, 405), (865, 405))),

        Flow("runtime/browser-edge", "deployment-flow-browser-edge", ids["user-browser"], ids["vercel-edge"], "HTTPS application request", "permintaan aplikasi HTTPS", EDGE, ((1780, 375), (1750, 375), (1750, 234), (1138, 234), (1138, 350), (1120, 350))),
        Flow("runtime/edge-function", "deployment-flow-edge-function", ids["vercel-edge"], ids["vercel-function"], "rewritten dynamic routes", "route dinamik rewrite", EDGE),
        Flow("runtime/function-express", "deployment-flow-function-express", ids["vercel-function"], ids["vercel-express"], style=EDGE),
        Flow("runtime/cron-express", "deployment-flow-cron-express", ids["vercel-cron"], ids["vercel-express"], "CRON_SECRET", "CRON_SECRET", EDGE_CONTROL),

        Flow("data/express-postgres", "deployment-flow-express-postgres", ids["vercel-express"], ids["data-postgres"], "DATABASE_URL / service-role", "DATABASE_URL / service-role", EDGE_DATA, ((1120, 645), (1145, 645), (1145, 410), (1175, 410))),
        Flow("data/express-storage", "deployment-flow-express-storage", ids["vercel-express"], ids["data-storage"], "server-only asset operations", "operasi aset pelayan sahaja", EDGE_DATA),
        Flow("data/browser-api", "deployment-flow-browser-data-api", ids["user-browser"], ids["data-api"], "publishable key + RLS", "kunci publishable + RLS", EDGE_DATA, ((1780, 415), (1752, 415), (1752, 712), (1410, 712))),
        Flow("data/api-postgres", "deployment-flow-api-postgres", ids["data-api"], ids["data-postgres"], "least-privilege grants", "grant hak minimum", EDGE_DATA),
        Flow("data/auth-postgres", "deployment-flow-auth-postgres", ids["data-auth"], ids["data-postgres"], "identity + application users", "identiti + pengguna aplikasi", EDGE_DATA, ((1145, 847), (1145, 450), (1175, 450))),

        Flow("geo/builder-droplet", "deployment-flow-builder-droplet", ids["geo-builder"], ids["geo-droplet"], "validated tile archive", "arkib jubin disahkan", EDGE_GEO),
        Flow("geo/droplet-caddy", "deployment-flow-droplet-caddy", ids["geo-droplet"], ids["geo-caddy"], "Docker network", "rangkaian Docker", EDGE_GEO),
        Flow("geo/caddy-valhalla", "deployment-flow-caddy-valhalla", ids["geo-caddy"], ids["geo-valhalla"], "reverse proxy · internal port 8002", "proksi songsang · port dalaman 8002", EDGE_GEO),
        Flow("geo/gateway-caddy", "deployment-flow-gateway-caddy", ids["vercel-express"], ids["geo-caddy"], "server-only bearer token", "token bearer pelayan sahaja", EDGE_GEO, ((1120, 660), (1140, 660), (1140, 645), (1465, 645))),
        Flow("geo/nominatim-gate", "deployment-flow-nominatim-gate", ids["vercel-express"], ids["geo-nominatim"], "feature gate: off", "pagar ciri: tutup", EDGE_CONTROL, ((1118, 700), (1132, 700), (1132, 934), (1438, 934), (1438, 878), (1465, 878))),

        Flow("external/express-platforms", "deployment-flow-external-platforms", ids["vercel-express"], ids["user-integrations"], "server-side provider calls", "panggilan penyedia sisi pelayan", EDGE + "exitX=1;exitY=0.8;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;", ((1138, 700), (1138, 942), (1750, 942), (1750, 702), (1780, 702))),
        Flow("monitor/healthz", "deployment-flow-monitor-health", ids["user-monitor"], ids["geo-caddy"], "public /healthz", "/healthz awam", EDGE_GEO + "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.8;entryDx=0;entryDy=0;", ((1752, 865), (1752, 948), (1440, 948), (1440, 680), (1465, 680))),
    ]
    for flow in flows:
        add_flow(root, flow)
    return mxfile


def validate(document: ET.Element) -> None:
    diagram = document.find("diagram")
    if diagram is None or diagram.get("id") != PAGE_ID:
        raise RuntimeError(f"Deployment diagram must contain page {PAGE_ID!r}")
    model = diagram.find("mxGraphModel")
    if model is None or (model.get("pageWidth"), model.get("pageHeight")) != (str(PAGE_WIDTH), str(PAGE_HEIGHT)):
        raise RuntimeError(f"Deployment diagram canvas must be {PAGE_WIDTH} x {PAGE_HEIGHT}")

    wrappers = diagram.findall(".//object")
    keys = [wrapper.get("petakerjaKey", "") for wrapper in wrappers]
    if len(keys) != len(set(keys)) or any(not key.startswith("deployment-infrastructure/") for key in keys):
        raise RuntimeError("Deployment component keys must be unique and namespaced")
    for wrapper in wrappers:
        if wrapper.get("label") and (not wrapper.get("labelEn") or not wrapper.get("labelMs")):
            raise RuntimeError(f"{wrapper.get('id')} is missing bilingual labels")

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
        "github-repository", "github-actions", "vercel-build-pipeline", "vercel-edge-delivery",
        "vercel-node-function", "vercel-runtime", "vercel-daily-cron", "cloudflare-dns",
        "exabytes-registrar", "supabase-db", "supabase-storage", "better-auth", "geo-gateway",
        "digitalocean-geo-host", "valhalla-tile-builder", "valhalla", "nominatim", "browser",
        "google-cloud-services", "email-platforms", "ai-provider", "external-data-platforms",
    }
    represented = {
        node_id
        for wrapper in wrappers
        for node_id in wrapper.get("nodeIds", "").split(",")
        if node_id
    }
    missing = required_nodes - represented
    if missing:
        raise RuntimeError(f"Deployment diagram is missing architecture nodes: {sorted(missing)}")

    visible = " ".join(html.unescape(wrapper.get("label", "")) for wrapper in wrappers).lower()
    forbidden = (
        "aws lambda", "s3 raw", "terraform", "step functions", "bronze layer", "silver layer",
        "gold layer", "dbt", "staging.petakerja.my", "staging project",
    )
    found = [term for term in forbidden if term in visible]
    if found:
        raise RuntimeError(f"Deployment diagram contains excluded platform claims: {found}")
    required_truth = (
        "npm run build", "dns-only", "publishable/anon key", "explicit grants + rls",
        "service-role, database_url and provider tokens never enter the browser",
        "server-only bearer token", "geo_router_enabled=false", "usd 24/month",
        "cost footer is not a complete tco estimate", "nominatim disabled",
    )
    missing_truth = [term for term in required_truth if term not in visible]
    if missing_truth:
        raise RuntimeError(f"Deployment diagram is missing operational truth: {missing_truth}")


def main() -> None:
    document = build_document()
    validate(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(document, space="  ")
    ET.ElementTree(document).write(OUTPUT, encoding="utf-8", xml_declaration=False)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
