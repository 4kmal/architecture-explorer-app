#!/usr/bin/env python3
"""Regression checks for the bilingual User sequence editor sources."""

from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from sequence_label_catalog import NON_MESSAGE_LABELS


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "google-oauth-sequence": {
        "path": ROOT / "assets/editor/sequence-google-oauth.drawio",
        "page": "petakerja_google_oauth_sequence",
        "messages": 39,
        "structure": "eb636b277b6625adc3fdb97e9dfc50592092e29a46a1188cb0ea7163979483d7",
    },
    "sequence": {
        "path": ROOT / "assets/editor/sequence-job-search.drawio",
        "page": "petakerja_job_search_sequence",
        "messages": 31,
        "structure": "c46e5961a48426290fa48f1054d5ada285055ec3b3f2e0e4c5796baa127cc866",
    },
    "user-explore-3d-map-sequence": {
        "path": ROOT / "assets/editor/sequence-user-explore-3d-map.drawio",
        "page": "petakerja_user_explore_3d_map_sequence",
        "messages": 24,
        "structure": "6722e0e7c840b6d73d7a0fdf6801a846fc8c1103bb2218af68540dadd24d5ad4",
    },
    "user-sign-out-sequence": {
        "path": ROOT / "assets/editor/sequence-user-sign-out.drawio",
        "page": "petakerja_user_sign_out_sequence",
        "messages": 18,
        "structure": "b5cea596e7aef4cc52075503561922de9be613dccd43629312022bf316f57f58",
    },
}

TRANSLATION_ATTRIBUTES = {
    "label",
    "labelEn",
    "labelMs",
    "simpleLabelEn",
    "simpleLabelMs",
    "codeLabelEn",
    "codeLabelMs",
    "petakerjaKey",
}
VOLATILE_ATTRIBUTES = {"modified", "etag", "agent"}


def structural_node(element: ET.Element) -> dict[str, object]:
    return {
        "tag": element.tag,
        "attrs": sorted(
            (name, value)
            for name, value in element.attrib.items()
            if name not in TRANSLATION_ATTRIBUTES | VOLATILE_ATTRIBUTES
        ),
        "children": [structural_node(child) for child in element],
    }


def structural_hash(root: ET.Element) -> str:
    payload = json.dumps(structural_node(root), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def check_source(prefix: str, config: dict[str, object]) -> list[str]:
    errors: list[str] = []
    path = config["path"]
    assert isinstance(path, Path)
    root = ET.parse(path).getroot()
    pages = root.findall("diagram")
    if len(pages) != 1 or pages[0].get("id") != config["page"]:
        errors.append(f"{path.name}: unexpected page identity")

    wrappers = root.findall(".//object")
    ids: set[str] = set()
    keys: set[str] = set()
    messages: list[ET.Element] = []
    for wrapper in wrappers:
        wrapper_id = wrapper.get("id", "")
        key = wrapper.get("petakerjaKey", "")
        if not wrapper_id or wrapper_id in ids:
            errors.append(f"{path.name}: missing or duplicate object id {wrapper_id!r}")
        ids.add(wrapper_id)
        if not key or key in keys:
            errors.append(f"{path.name}: missing or duplicate petakerjaKey {key!r}")
        keys.add(key)

        if "/message-" in key:
            messages.append(wrapper)
            for field in ("simpleLabelEn", "simpleLabelMs", "codeLabelEn", "codeLabelMs"):
                if not wrapper.get(field):
                    errors.append(f"{path.name}: {key} is missing {field}")

        cell = wrapper.find("mxCell")
        if cell is not None and cell.get("edge") == "1" and "divider" not in key:
            if not cell.get("source") or not cell.get("target"):
                errors.append(f"{path.name}: connector {key} has a missing endpoint")

    if len(messages) != config["messages"]:
        errors.append(f"{path.name}: expected {config['messages']} messages, found {len(messages)}")

    for key in (key for key in NON_MESSAGE_LABELS if key.startswith(f"{prefix}/")):
        wrapper = next((item for item in wrappers if item.get("petakerjaKey") == key), None)
        if wrapper is None:
            errors.append(f"{path.name}: missing bilingual object {key}")
        elif not wrapper.get("labelEn") or not wrapper.get("labelMs"):
            errors.append(f"{path.name}: incomplete bilingual labels for {key}")

    actual_hash = structural_hash(root)
    if actual_hash != config["structure"]:
        errors.append(
            f"{path.name}: geometry/style/endpoint structure changed "
            f"({actual_hash} != {config['structure']})"
        )
    return errors


def main() -> int:
    errors = [error for prefix, config in SOURCES.items() for error in check_source(prefix, config)]
    if errors:
        print("Bilingual User sequence checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Bilingual User sequence checks passed for 4 diagrams and 112 messages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
