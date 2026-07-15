#!/usr/bin/env python3
"""Create polished presentation variants of the three User flow charts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_polisher():
    path = Path(__file__).with_name("build-polished-admin-flowcharts.py")
    spec = importlib.util.spec_from_file_location("petakerja_flow_polisher", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


polisher = load_polisher()


SPECS = (
    polisher.Spec(
        "user-search-jobs-flowchart",
        "Flow Chart PetaKerja - Search Jobs",
        "flowchart-user-search-jobs",
        20,
        23,
    ),
    polisher.Spec(
        "user-explore-3d-map-flowchart",
        "Flow Chart PetaKerja - Explore the 3D Map",
        "flowchart-user-explore-3d-map",
        21,
        24,
    ),
    polisher.Spec(
        "user-sign-out-flowchart",
        "Flow Chart PetaKerja - User Sign Out",
        "flowchart-user-sign-out",
        14,
        15,
    ),
)


def main() -> None:
    results = [polisher.build_one(spec) for spec in SPECS]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
