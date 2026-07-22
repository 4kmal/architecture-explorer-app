"""Attach bilingual Simple/Code labels to the canonical routing stack."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "editor" / "petakerja-map-routing-responsibility-stack.drawio"


LABELS = {
    "layer1-inputs": ("1 · What the user provides", "1 · Input pengguna", "LAYER 1 · INPUTS", "LAPISAN 1 · INPUT"),
    "input-search": ("Search for a place or address", "Cari tempat atau alamat", "SearchManager.search()", "SearchManager.search()"),
    "input-ab": ("Choose route start and destination", "Pilih mula dan destinasi laluan", 'GeoNavigationManager.setPoint("A" | "B")', 'GeoNavigationManager.setPoint("A" | "B")'),
    "input-gps": ("Use the current device location", "Gunakan lokasi peranti semasa", "navigator.geolocation", "navigator.geolocation"),
    "layer2-maplibre": ("2 · Draw the map and route", "2 · Paparkan peta dan laluan", "LAYER 2 · RENDERING — MAPLIBRE GL JS", "LAPISAN 2 · PAPARAN — MAPLIBRE GL JS"),
    "maplibre-current": ("Draws route lines and markers", "Memaparkan garisan laluan dan penanda", "GeoRouteRenderer + MapLibre GL JS", "GeoRouteRenderer + MapLibre GL JS"),
    "maplibre-capability": ("Handles route interaction and camera", "Mengendalikan interaksi laluan dan kamera", "GeoJSONSource.setData() + fitBounds()", "GeoJSONSource.setData() + fitBounds()"),
    "layer3-browser": ("3 · Coordinate the browser workflow", "3 · Selaras aliran pelayar", "LAYER 3 · PETAKERJA BROWSER ORCHESTRATION", "LAPISAN 3 · ORKESTRASI PELAYAR PETAKERJA"),
    "browser-search-manager": ("Finds places and POIs", "Mencari tempat dan POI", "SearchManager", "SearchManager"),
    "browser-navigation-manager": ("Coordinates A-to-B navigation", "Menyelaras navigasi A-ke-B", "GeoNavigationManager", "GeoNavigationManager"),
    "browser-geo-service": ("Calls the same-origin geo API", "Memanggil API geo asal sama", "src/services/geo.ts → /api/geo/*", "src/services/geo.ts → /api/geo/*"),
    "layer4-gateway": ("4 · Validate and dispatch requests", "4 · Sahkan dan hantar permintaan", "LAYER 4 · PETAKERJA GEOGATEWAY", "LAPISAN 4 · GEOGATEWAY PETAKERJA"),
    "gateway-express": ("Receives browser geo requests", "Menerima permintaan geo pelayar", "Express /api/geo/*", "Express /api/geo/*"),
    "gateway-core": ("Chooses providers and normalizes results", "Memilih penyedia dan menormalkan hasil", "GeoGateway", "GeoGateway"),
    "gateway-guards": ("Applies safety, limits and cache", "Menggunakan keselamatan, had dan cache", "Malaysia guards + timeout + rate limit + cache", "Pengawal Malaysia + timeout + had kadar + cache"),
    "layer5-providers": ("5 · Calculate and reuse geo data", "5 · Kira dan guna semula data geo", "LAYER 5 · PROVIDERS + REUSABLE DATA", "LAPISAN 5 · PENYEDIA + DATA BOLEH GUNA SEMULA"),
    "provider-nominatim": ("Converts places and coordinates", "Menukar tempat dan koordinat", "Nominatim search + reverse + lookup", "Nominatim search + reverse + lookup"),
    "provider-valhalla": ("Calculates road routes and travel time", "Mengira laluan jalan dan masa perjalanan", "Valhalla route + matrix + isochrone", "Valhalla route + matrix + isochrone"),
    "provider-supabase": ("Reuses recent geo results", "Menggunakan semula hasil geo terkini", "geo_geocode_cache + geo_route_cache", "geo_geocode_cache + geo_route_cache"),
}


def main() -> None:
    tree = ET.parse(SOURCE)
    wrappers = {item.get("id", ""): item for item in tree.getroot().findall(".//object")}
    missing = sorted(set(LABELS) - set(wrappers))
    if missing:
        raise ValueError(f"Routing label-mode targets are missing: {', '.join(missing)}")
    for identifier, (simple_en, simple_ms, code_en, code_ms) in LABELS.items():
        wrapper = wrappers[identifier]
        wrapper.set("labelEn", wrapper.get("labelEn") or wrapper.get("label") or code_en)
        wrapper.set("labelMs", wrapper.get("labelMs") or simple_ms)
        wrapper.set("simpleLabelEn", simple_en)
        wrapper.set("simpleLabelMs", simple_ms)
        wrapper.set("codeLabelEn", code_en)
        wrapper.set("codeLabelMs", code_ms)
    ET.indent(tree, space="  ")
    tree.write(SOURCE, encoding="utf-8", xml_declaration=True)
    print(f"Annotated {len(LABELS)} routing-stack labels in {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
